# Cloud Cost Optimization

Standards for identifying waste, right-sizing resources, and continuously reducing cloud spend
without sacrificing reliability. AWS Cost Explorer is the default visibility tool; deviations
require an ADR.

---

## Defaults

| Area | Default | Alternatives |
|------|---------|--------------|
| **Cost visibility** | AWS Cost Explorer + CUR (Cost and Usage Reports) | Azure Cost Management, GCP Billing Export, CloudHealth, Apptio Cloudability |
| **Right-sizing** | AWS Compute Optimizer | Azure Advisor, GCP Recommender, Densify, Spot.io |
| **Waste detection** | Scheduled Lambda scanning for idle resources | Trusted Advisor, CloudHealth, custom scripts via Cloud Custodian |
| **Anomaly detection** | AWS Cost Anomaly Detection | Anodot, CloudHealth, custom threshold alerts |
| **Optimization cadence** | Weekly review, monthly deep-dive | Continuous automated, quarterly only (not recommended) |

---

## Do / Don't

- **Do** establish a baseline cost per environment, per service, and per team before
  optimizing — you cannot improve what you have not measured.
- **Do** automate idle-resource detection: unattached EBS volumes, stopped instances older
  than 7 days, unused Elastic IPs, empty load balancers, idle RDS instances.
- **Do** right-size before purchasing reservations — over-provisioned instances lock in waste
  when converted to Reserved Instances.
- **Do** use Spot/Preemptible instances for fault-tolerant workloads (batch processing,
  CI/CD runners, dev/test environments).
- **Do** set up automated shutdown schedules for non-production environments (nights, weekends).
- **Don't** optimize blindly — always validate that right-sizing does not degrade latency,
  throughput, or availability.
- **Don't** treat cost optimization as a one-time project. Cloud spend drifts continuously;
  reviews must be recurring.
- **Don't** ignore data transfer costs — they are often the fastest-growing line item and the
  hardest to forecast.
- **Don't** delete resources without confirming ownership. Use a quarantine period (tag, stop,
  wait 14 days, then terminate).

---

## Common Pitfalls

1. **Right-sizing too aggressively.** Cutting instance sizes based on average CPU ignores peak
   demand. Use P95/P99 utilization over at least 14 days before downsizing. Always load-test
   after a resize.

2. **Ignoring data transfer costs.** Inter-AZ, inter-region, and internet egress charges
   compound silently. Consolidate services into fewer AZs where HA requirements allow, use VPC
   endpoints for AWS service traffic, and consider CDN offloading for egress-heavy workloads.

3. **Zombie resources.** Developers spin up resources for testing and forget them. Automate
   detection with Cloud Custodian policies or scheduled Lambda functions that tag unattached
   volumes, idle instances (CPU < 5% for 7+ days), and unused snapshots older than 90 days.

4. **Savings Plans purchased for the wrong workload.** Compute Savings Plans offer flexibility
   across instance families and regions, but EC2 Instance Savings Plans give deeper discounts.
   Match the plan type to workload stability — flexible workloads get Compute plans; stable,
   predictable workloads get Instance plans.

5. **Optimizing dev/test at the expense of velocity.** Shutting down dev environments saves
   money, but if startup takes 30 minutes, developers waste time waiting. Balance cost savings
   with developer productivity — use fast-provisioning patterns (containers, snapshotted AMIs).

---

## Waste Identification Automation

Automate resource scanning to detect waste before it accumulates.

```python
# Cloud Custodian policy — find unattached EBS volumes older than 7 days
policies:
  - name: delete-unattached-ebs
    resource: ebs
    filters:
      - type: value
        key: Attachments
        value: empty
      - type: value
        key: CreateTime
        value_type: age
        op: greater-than
        value: 7
    actions:
      - type: tag
        key: custodian-quarantine
        value: "true"
      - type: notify
        to:
          - finops-team@example.com
        subject: "Unattached EBS volume detected"
        transport:
          type: sqs
          queue: custodian-notifications
```

```python
# Cloud Custodian policy — identify idle EC2 instances (CPU < 5% for 14 days)
policies:
  - name: flag-idle-instances
    resource: ec2
    filters:
      - type: instance-age
        days: 14
      - type: metrics
        name: CPUUtilization
        statistics: Average
        period: 86400       # 1 day
        days: 14
        value: 5
        op: less-than
    actions:
      - type: tag
        key: idle-candidate
        value: "true"
      - type: notify
        to:
          - resource-owner
        subject: "Idle EC2 instance flagged for review"
        transport:
          type: sqs
          queue: custodian-notifications
```

---

## Right-Sizing Workflow

```
1. Collect metrics (CPU, memory, network, disk I/O) — minimum 14-day window
2. Identify candidates: avg utilization < 40% AND p99 < 70%
3. Propose new instance type (one size down, or different family)
4. Validate in staging with load test
5. Apply change via IaC (Terraform / CloudFormation)
6. Monitor for 7 days post-change
7. Rollback if latency p99 increases > 10% or error rate increases
```

```bash
# AWS CLI — get CPU utilization for right-sizing analysis
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-0abc123def456 \
  --start-time "$(date -u -d '14 days ago' +%Y-%m-%dT%H:%M:%S)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%S)" \
  --period 3600 \
  --statistics Average Maximum \
  --output table
```

---

## Non-Production Environment Scheduling

```python
# Terraform — auto-stop dev instances outside business hours
resource "aws_autoscaling_schedule" "scale_down_nights" {
  scheduled_action_name  = "dev-stop-nights"
  autoscaling_group_name = aws_autoscaling_group.dev.name
  min_size               = 0
  max_size               = 0
  desired_capacity       = 0
  recurrence             = "0 19 * * MON-FRI"  # 7 PM UTC weekdays
}

resource "aws_autoscaling_schedule" "scale_up_mornings" {
  scheduled_action_name  = "dev-start-mornings"
  autoscaling_group_name = aws_autoscaling_group.dev.name
  min_size               = 1
  max_size               = 3
  desired_capacity       = 2
  recurrence             = "0 7 * * MON-FRI"   # 7 AM UTC weekdays
}
```

---

## Alternatives

| Tool | When to consider |
|------|-----------------|
| CloudHealth (VMware) | Multi-cloud visibility with governance features |
| Apptio Cloudability | Enterprise-grade cost management with business mapping |
| Kubecost | Kubernetes-specific cost allocation and optimization |
| Spot.io (NetApp) | Automated Spot instance management with SLA guarantees |
| Cloud Custodian | Policy-as-code for resource governance and waste cleanup |
| Infracost | Shift-left cost estimation in CI/CD pipelines (Terraform) |

---

## Checklist

- [ ] Cost baseline established per environment and per service
- [ ] Automated waste detection scanning runs weekly at minimum
- [ ] Unattached volumes, idle instances, and unused snapshots are auto-tagged
- [ ] Quarantine-before-delete process enforced (tag → stop → wait 14 days → terminate)
- [ ] Right-sizing reviews performed monthly using 14-day utilization data
- [ ] Non-production environments have automated shutdown schedules
- [ ] Spot/Preemptible instances used for fault-tolerant workloads
- [ ] Data transfer costs tracked and optimized (VPC endpoints, CDN, AZ consolidation)
- [ ] Cost anomaly alerts configured and routed to responsible teams
- [ ] Optimization actions tracked in a shared register with measured savings
