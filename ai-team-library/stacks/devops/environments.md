# Environment Management

Standards for provisioning, promoting, and managing deployment environments.
Infrastructure is defined as code. Manual environment changes are forbidden.

---

## Defaults

- **Environments:** `dev` (continuous deploy), `staging` (pre-production mirror),
  `prod` (production, gated approval).
- **IaC tool:** Terraform with remote state in S3/GCS + state locking via DynamoDB/GCS.
- **Parity principle:** Staging mirrors production in topology, network rules, and
  resource sizing (scaled down where cost-prohibitive).
- **Promotion flow:** Build once, deploy the same artifact through each environment.
  Never rebuild per environment.

```
dev  ──push to main──►  staging  ──manual approval──►  prod
         (auto)              (smoke + QA)                  (canary → full)
```

---

## Do / Don't

- **Do** define every environment in Terraform (or equivalent IaC). No ClickOps.
- **Do** use workspaces or directory-per-environment pattern to manage env differences.
- **Do** parameterize environment-specific values (URLs, scaling, feature flags)
  through variables, not code branches.
- **Do** require manual approval gates for production deployments.
- **Do** run smoke tests automatically after each deployment.
- **Don't** maintain long-lived feature environments. Spin up ephemeral preview
  environments per PR and tear them down on merge.
- **Don't** allow production database access from non-production environments.
- **Don't** share secrets across environments. Each environment has its own credentials.
- **Don't** treat staging as a testing playground. It is a production rehearsal.

---

## Common Pitfalls

1. **Environment drift.** Staging diverges from production because someone made a
   manual change. Solution: enforce IaC-only changes; detect drift with
   `terraform plan` in CI on a schedule.
2. **Config spaghetti.** Environment-specific logic scattered through application code.
   Solution: externalize all config via environment variables or a config service.
3. **Shared databases across environments.** One bad migration in dev corrupts staging
   data. Solution: each environment owns its own data stores.
4. **No teardown for preview environments.** Ephemeral environments accumulate cost.
   Solution: TTL labels + a reaper job that destroys environments older than 48h.
5. **Promotion by rebuilding.** Each environment builds its own artifact, introducing
   subtle differences. Solution: build once, promote the identical artifact.

---

## Terraform Environment Pattern

```hcl
# environments/staging/main.tf
module "app" {
  source = "../../modules/app"

  environment    = "staging"
  instance_count = 2
  instance_type  = "t3.medium"
  domain         = "staging.example.com"

  tags = {
    Environment = "staging"
    ManagedBy   = "terraform"
  }
}

terraform {
  backend "s3" {
    bucket         = "company-tfstate"
    key            = "staging/app.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

```hcl
# modules/app/variables.tf
variable "environment" {
  type        = string
  description = "Deployment environment: dev, staging, prod"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
```

---

## Environment Promotion Checklist

Before promoting from staging to production:

- [ ] All automated tests pass in staging
- [ ] Smoke tests confirm core user journeys work
- [ ] No open P1/P2 incidents in staging
- [ ] Database migrations have been applied and verified
- [ ] Rollback plan is documented and tested
- [ ] On-call engineer is aware of the deployment window

---

## Alternatives

| Tool            | When to consider                                     |
|-----------------|------------------------------------------------------|
| Pulumi          | Team prefers general-purpose languages over HCL      |
| AWS CDK         | Deep AWS investment, TypeScript/Python preference     |
| Crossplane      | Kubernetes-native infrastructure management          |
| OpenTofu        | Need BSL-free Terraform-compatible tooling           |

---

## Checklist

- [ ] All environments are defined in version-controlled IaC
- [ ] Terraform state is stored remotely with locking enabled
- [ ] Each environment has isolated data stores and credentials
- [ ] Promotion moves the same artifact -- no per-environment rebuilds
- [ ] Staging mirrors production topology and network rules
- [ ] Ephemeral preview environments have automated teardown
- [ ] Drift detection runs on a schedule (daily minimum)
- [ ] Production deploys require explicit manual approval
- [ ] Environment variables and config are externalized, not hardcoded
- [ ] Smoke tests run automatically after every deployment
