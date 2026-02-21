# AWS Core Services

Standards for deploying and operating workloads on Amazon Web Services.
This guide covers identity, networking, compute, storage, and databases.
All AWS usage must follow the Well-Architected Framework. Deviations require an ADR.

---

## Defaults

| Category | Default | Alternatives |
|----------|---------|-------------|
| **Identity** | IAM with OIDC federation from corporate IdP | IAM Identity Center (SSO), Cognito (customer-facing) |
| **Networking** | VPC with public + private subnets across 3 AZs | Transit Gateway (multi-VPC), PrivateLink (service endpoints) |
| **Compute** | ECS Fargate (containerized workloads) | Lambda (event-driven, <15 min), EKS (Kubernetes required), EC2 (bare metal/GPU) |
| **Storage** | S3 Standard with versioning enabled | S3-IA (infrequent access), S3 Glacier (archive), EFS (shared filesystem) |
| **Database** | RDS PostgreSQL Multi-AZ | Aurora (high throughput), DynamoDB (key-value/NoSQL), ElastiCache (caching) |
| **DNS** | Route 53 with health checks | CloudFront (CDN + DNS), Global Accelerator (multi-region) |
| **Secrets** | Secrets Manager with automatic rotation | SSM Parameter Store (non-rotating config), KMS (encryption keys) |
| **IaC** | CloudFormation or CDK (TypeScript) | Terraform (multi-cloud teams), Pulumi (programming-language preference) |

---

## IAM

### Principles

- **Least privilege.** Every role, user, and policy grants only the permissions needed
  for the specific task. Start with zero permissions and add incrementally.
- **No long-lived credentials.** Use IAM roles with temporary credentials via STS.
  Never embed access keys in code or config files.
- **Federated access.** Human users authenticate through the corporate IdP via
  OIDC or SAML federation. No IAM users with console passwords in production accounts.

### Policy Structure

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadSpecificBucket",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-app-data",
        "arn:aws:s3:::my-app-data/*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:PrincipalOrgID": "o-exampleorgid"
        }
      }
    }
  ]
}
```

### Guardrails

- Enable Service Control Policies (SCPs) at the AWS Organization level.
- Deny actions outside approved regions.
- Require MFA for sensitive operations (IAM changes, S3 bucket deletion).
- Tag every IAM role with `team`, `environment`, and `purpose`.

---

## VPC & Networking

### Standard Architecture

```
VPC (10.0.0.0/16)
├── Public Subnets  (10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24)  — ALB, NAT Gateway
├── Private Subnets (10.0.11.0/24, 10.0.12.0/24, 10.0.13.0/24) — App (ECS/Lambda)
└── Data Subnets    (10.0.21.0/24, 10.0.22.0/24, 10.0.23.0/24) — RDS, ElastiCache
```

- **3 Availability Zones** minimum for production workloads.
- **NAT Gateway** in each AZ for private subnet internet access. Use NAT Gateway per
  AZ, not a shared one, for resilience.
- **Security Groups** are stateful firewalls. Default deny all inbound.
  Allow only required ports from known sources.
- **NACLs** are the second layer. Use them sparingly for broad deny rules.
- **VPC Flow Logs** enabled and shipped to CloudWatch Logs or S3 for audit.

### Connectivity

| Pattern | Solution |
|---------|----------|
| Service-to-service within VPC | Security group references |
| VPC-to-VPC | VPC Peering or Transit Gateway |
| VPC-to-on-premises | Site-to-Site VPN or Direct Connect |
| VPC-to-AWS-services | VPC Endpoints (Gateway for S3/DynamoDB, Interface for others) |

---

## Compute

### ECS Fargate (Default)

```yaml
# Task definition essentials
family: my-service
cpu: 512          # 0.5 vCPU
memory: 1024      # 1 GB
networkMode: awsvpc
requiresCompatibilities: [FARGATE]
containerDefinitions:
  - name: app
    image: 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:abc123
    portMappings:
      - containerPort: 8080
    logConfiguration:
      logDriver: awslogs
      options:
        awslogs-group: /ecs/my-service
        awslogs-region: us-east-1
        awslogs-stream-prefix: ecs
    healthCheck:
      command: ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
      interval: 30
      timeout: 5
      retries: 3
```

- Use **Application Load Balancer** in front of ECS services.
- Configure **auto-scaling** based on CPU/memory utilization or custom CloudWatch metrics.
- Store container images in **ECR** with image scanning enabled.

### Lambda (Event-Driven)

- Use for event-driven workloads: API Gateway triggers, S3 events, SQS consumers,
  scheduled tasks (EventBridge).
- **Memory:** Start at 256 MB, tune with Lambda Power Tuning tool.
- **Timeout:** Set explicitly. Max 15 minutes. Most functions should complete in <30s.
- **Layers:** Share common code via Lambda Layers, not copy-paste.
- **Cold starts:** Use Provisioned Concurrency for latency-sensitive endpoints.

---

## Storage (S3)

### Bucket Configuration

- **Versioning:** Enabled on all buckets storing application data.
- **Encryption:** SSE-S3 (default) or SSE-KMS (regulatory requirements).
- **Public access:** Block all public access via the account-level S3 Block Public Access setting.
- **Lifecycle rules:** Transition objects to S3-IA after 90 days, Glacier after 365 days.
  Delete incomplete multipart uploads after 7 days.
- **Replication:** Cross-region replication for disaster recovery of critical data.

```json
{
  "Rules": [
    {
      "ID": "ArchiveOldObjects",
      "Status": "Enabled",
      "Transitions": [
        { "Days": 90, "StorageClass": "STANDARD_IA" },
        { "Days": 365, "StorageClass": "GLACIER" }
      ],
      "AbortIncompleteMultipartUpload": { "DaysAfterInitiation": 7 }
    }
  ]
}
```

---

## Database (RDS)

### RDS PostgreSQL Standards

- **Multi-AZ** enabled for production. Single-AZ acceptable for dev/test.
- **Encryption at rest** with KMS. Enforce `StorageEncrypted: true`.
- **Automated backups** with 14-day retention (production), 7-day (non-production).
- **Enhanced Monitoring** enabled with 60-second granularity.
- **Performance Insights** enabled to diagnose query performance.
- **Parameter group:** Set `log_statement = 'ddl'`, `log_min_duration_statement = 1000`.
- **No public accessibility.** Place RDS in data subnets with no internet route.

### Connection Management

- Use **IAM database authentication** for applications (no password in config).
- Use **RDS Proxy** for Lambda-to-RDS connections to manage connection pooling.
- Set application connection pool size to match expected concurrency, not max connections.

---

## Do / Don't

- **Do** use multiple AWS accounts (dev, staging, production) via AWS Organizations.
- **Do** tag every resource with `Environment`, `Team`, `CostCenter`, and `ManagedBy`.
- **Do** use VPC endpoints to keep traffic off the public internet.
- **Do** enable CloudTrail in all accounts and all regions.
- **Do** encrypt all data at rest and in transit.
- **Do** use infrastructure as code for all resource provisioning.
- **Don't** use the root account for daily operations. Lock it with MFA and alerts.
- **Don't** hardcode AWS account IDs, regions, or ARNs. Use SSM parameters or CDK context.
- **Don't** create IAM users with access keys for applications. Use IAM roles.
- **Don't** deploy resources in a single Availability Zone for production workloads.
- **Don't** use default VPCs for production. Create purpose-built VPCs.
- **Don't** leave S3 buckets without encryption, versioning, or access logging.

---

## Common Pitfalls

1. **Over-permissive IAM policies.** Using `"Action": "*"` or `"Resource": "*"` creates
   a blast radius. Solution: use IAM Access Analyzer to generate least-privilege policies
   from actual usage.
2. **Single-AZ deployments.** A single AZ outage takes down the entire application.
   Solution: deploy across at least 3 AZs with health checks and auto-failover.
3. **Unrestricted security groups.** `0.0.0.0/0` on port 22 or 3389 is an open
   invitation. Solution: use SSM Session Manager for shell access—no SSH ports needed.
4. **Unmonitored costs.** A forgotten EC2 instance or NAT Gateway runs up the bill.
   Solution: set up AWS Budgets with alerts at 50%, 80%, and 100% of target spend.
5. **No disaster recovery plan.** Backups exist but have never been tested.
   Solution: schedule quarterly DR drills. Restore from backup and verify data integrity.
6. **Lambda cold starts in synchronous paths.** Users experience 2–5 second delays.
   Solution: use Provisioned Concurrency for user-facing endpoints, or switch to
   Fargate for always-on workloads.
7. **S3 bucket name squatting.** Deleted bucket names can be claimed by anyone.
   Solution: use unique, prefixed bucket names and never delete buckets in production
   without replacing them.

---

## Checklist

- [ ] AWS accounts structured with Organizations (dev/staging/prod separation)
- [ ] SCPs enforce region restrictions and deny dangerous actions
- [ ] IAM roles use least-privilege policies; no wildcard permissions
- [ ] No long-lived access keys; applications use IAM roles with STS
- [ ] MFA enforced for all human users and the root account
- [ ] VPC spans 3+ AZs with public, private, and data subnets
- [ ] Security groups default-deny; only required ports open from known sources
- [ ] VPC Flow Logs enabled and retained for audit
- [ ] CloudTrail enabled in all regions with log file validation
- [ ] All S3 buckets have encryption, versioning, and Block Public Access enabled
- [ ] RDS instances are Multi-AZ with encryption at rest and automated backups
- [ ] ECS tasks / Lambda functions have scoped IAM execution roles
- [ ] All resources tagged with Environment, Team, CostCenter, ManagedBy
- [ ] Infrastructure provisioned via IaC (CloudFormation/CDK/Terraform)
- [ ] AWS Budgets configured with cost alerts
