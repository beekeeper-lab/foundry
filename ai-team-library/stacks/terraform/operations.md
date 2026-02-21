# Terraform Operations

Patterns for running Terraform safely in CI/CD, detecting drift, managing
plan/apply workflows, and handling production deployments.

---

## Plan / Apply Workflow

```bash
# Standard workflow: init → validate → plan → review → apply.

# 1. Initialize — download providers, configure backend.
terraform init

# 2. Validate — syntax and configuration checks (no API calls).
terraform validate

# 3. Plan — generate execution plan, save to file.
terraform plan -out=tfplan

# 4. Review — inspect the saved plan.
terraform show tfplan

# 5. Apply — execute the reviewed plan (no re-planning).
terraform apply tfplan
```

**Rules:**
- Always save the plan to a file (`-out=tfplan`) and apply that file. This ensures
  the applied changes match exactly what was reviewed.
- Never run `terraform apply` without `-out` in production. Without it, Terraform
  re-plans at apply time, and the infrastructure may have changed since review.
- Never use `-auto-approve` in production. It bypasses the review step.
- In CI/CD, the plan step runs on PR creation. The apply step runs after PR merge
  (or after manual approval in the pipeline).

---

## CI/CD Integration

```yaml
# Example: GitHub Actions pipeline.
name: Terraform
on:
  pull_request:
    paths: ["environments/**", "modules/**"]
  push:
    branches: [main]
    paths: ["environments/**", "modules/**"]

jobs:
  plan:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.6.x"

      - name: Init
        run: terraform init -input=false
        working-directory: environments/prod

      - name: Validate
        run: terraform validate
        working-directory: environments/prod

      - name: Lint
        run: tflint --init && tflint
        working-directory: environments/prod

      - name: Security Scan
        run: tfsec environments/prod

      - name: Plan
        run: terraform plan -input=false -no-color -out=tfplan
        working-directory: environments/prod

      - name: Post Plan to PR
        uses: actions/github-script@v7
        with:
          script: |
            // Post plan output as PR comment for review.

  apply:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: production    # Requires manual approval.
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3

      - name: Init
        run: terraform init -input=false
        working-directory: environments/prod

      - name: Plan
        run: terraform plan -input=false -out=tfplan
        working-directory: environments/prod

      - name: Apply
        run: terraform apply -input=false tfplan
        working-directory: environments/prod
```

**Rules:**
- Run `terraform plan` on every PR. Post the plan output as a PR comment for review.
- Run `terraform apply` only on merge to `main`, with manual approval for production.
- Use `-input=false` in CI/CD to prevent interactive prompts from hanging the pipeline.
- Pin the Terraform version in CI/CD to match `.terraform-version`.
- Use OIDC / workload identity for cloud credentials in CI/CD. Never store
  long-lived access keys in CI/CD secrets.
- Run linting (`tflint`) and security scanning (`tfsec` / `checkov`) before plan.
  Fail the pipeline on high-severity findings.

---

## Drift Detection

Drift occurs when real infrastructure diverges from Terraform state — caused by
manual console changes, other tools, or external processes.

```bash
# Detect drift by running plan on a schedule (e.g., daily cron).
terraform plan -detailed-exitcode -out=drift-check.tfplan

# Exit codes:
# 0 = no changes (no drift)
# 1 = error
# 2 = changes detected (drift found)
```

```yaml
# Scheduled drift detection in CI/CD.
name: Drift Detection
on:
  schedule:
    - cron: "0 6 * * *"   # Daily at 6 AM UTC.

jobs:
  detect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3

      - name: Init
        run: terraform init -input=false
        working-directory: environments/prod

      - name: Check Drift
        id: drift
        run: |
          terraform plan -detailed-exitcode -input=false -no-color \
            -out=drift.tfplan 2>&1 | tee plan-output.txt
          echo "exitcode=$?" >> "$GITHUB_OUTPUT"
        working-directory: environments/prod
        continue-on-error: true

      - name: Alert on Drift
        if: steps.drift.outputs.exitcode == '2'
        run: |
          echo "::warning::Drift detected in prod. Review plan output."
          # Send alert to Slack / PagerDuty / email.
```

**Rules:**
- Run drift detection on a daily schedule for production environments.
- Use `-detailed-exitcode` to distinguish "no changes" (0) from "changes
  detected" (2).
- Alert the team when drift is detected. Do not auto-remediate — investigate
  why drift occurred before applying corrections.
- Common drift causes: manual console changes, auto-scaling events, AWS service
  updates, other IaC tools modifying the same resources.
- After investigating, either `terraform apply` to correct drift or `terraform
  import` / `terraform state rm` if the drift is intentional.

---

## Import and Adoption

```hcl
# import.tf — Terraform 1.5+ import blocks (declarative).
import {
  to = aws_s3_bucket.existing_logs
  id = "my-existing-logs-bucket"
}

resource "aws_s3_bucket" "existing_logs" {
  bucket = "my-existing-logs-bucket"
  # Fill in attributes to match the real resource.
}
```

```bash
# Imperative import (pre-1.5 or one-off).
terraform import aws_s3_bucket.existing_logs my-existing-logs-bucket

# After import, run plan to verify configuration matches reality.
terraform plan
# Fix any diffs until plan shows zero changes.
```

**Rules:**
- Prefer declarative `import` blocks (Terraform 1.5+) over `terraform import` CLI.
  Import blocks are reviewable in PRs and repeatable.
- After importing, run `terraform plan` and resolve all diffs. The configuration
  must match the real resource exactly before applying.
- Import one resource at a time. Verify plan output after each import.
- Document imported resources in the module's README with context on why they were
  imported rather than created by Terraform.

---

## Destroy and Cleanup

```bash
# Target a specific resource for destruction.
terraform destroy -target=aws_s3_bucket.temp_data

# Destroy all resources managed by this root module.
terraform destroy

# Remove from state without destroying the real resource.
terraform state rm aws_s3_bucket.migrated_elsewhere
```

**Rules:**
- Never run `terraform destroy` without specifying a target in production unless
  decommissioning the entire stack.
- Use `-target` to destroy specific resources. Verify the plan before confirming.
- Use `terraform state rm` when transferring ownership of a resource to another
  root module or to manual management.
- After removing state references, verify with `terraform plan` that Terraform
  does not attempt to recreate the resource.
- Protect critical resources with `lifecycle { prevent_destroy = true }`.

```hcl
resource "aws_rds_instance" "main" {
  # ...
  lifecycle {
    prevent_destroy = true
  }
}
```

---

## Secrets Management

```hcl
# Reference secrets from a vault — never store them in .tf or .tfvars files.
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/database/password"
}

resource "aws_db_instance" "main" {
  engine               = "postgres"
  instance_class       = "db.r6g.large"
  username             = "admin"
  password             = data.aws_secretsmanager_secret_version.db_password.secret_string
  # ...
}
```

**Rules:**
- Never store secrets in `.tf` files, `.tfvars` files, or environment variables
  that get logged.
- Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager,
  Azure Key Vault) and reference secrets via `data` sources.
- Mark secret variables and outputs as `sensitive = true`.
- Remember that Terraform state contains secret values in plaintext. Encrypt state
  at rest and restrict access.
- Rotate secrets through the secrets manager, not by editing Terraform variables.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Error acquiring the state lock` | Previous run crashed or is still running | Verify no apply is running, then `terraform force-unlock <ID>` |
| `Provider produced inconsistent result` | Provider bug or API race condition | Run `terraform refresh` then `terraform plan` again |
| Plan shows unexpected destroy/recreate | Resource changed outside Terraform | Investigate drift, import changes or update config to match |
| `Error: Unsupported Terraform Core version` | Terraform binary version mismatch | Install version matching `required_version` constraint |
| `Module not installed` | Missing `terraform init` after adding module | Run `terraform init` or `terraform init -upgrade` |
| Plan differs between engineers | Different provider versions | Commit `.terraform.lock.hcl` and run `terraform init` |

---

## Checklist

- [ ] `terraform plan -out=tfplan` used in CI/CD; plan file applied (not re-planned).
- [ ] `-input=false` set in all CI/CD steps.
- [ ] Plan output posted as PR comment for team review.
- [ ] Apply runs only after PR merge with manual approval for production.
- [ ] OIDC / workload identity used for CI/CD credentials (no long-lived keys).
- [ ] `tflint` and `tfsec`/`checkov` run in CI/CD pipeline.
- [ ] Daily drift detection scheduled for production environments.
- [ ] Drift alerts sent to team channel (Slack, email, PagerDuty).
- [ ] Secrets referenced from secrets manager, not stored in config files.
- [ ] Critical resources protected with `lifecycle { prevent_destroy = true }`.
- [ ] `terraform destroy` requires explicit `-target` in production.
- [ ] Import blocks used for adopting existing resources (Terraform 1.5+).
