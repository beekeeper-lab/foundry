# Terraform Stack Conventions

Non-negotiable defaults for Terraform infrastructure-as-code on this team. Targets
Terraform 1.6+ with the HashiCorp provider ecosystem. Deviations require an ADR
with justification. "I prefer it differently" is not justification.

---

## Defaults

| Concern              | Default Choice                          | Override Requires |
|----------------------|-----------------------------------------|-------------------|
| Terraform Version    | 1.6+ (latest stable)                   | ADR               |
| Language             | HCL (`.tf` files)                      | Never             |
| State Backend        | Remote (S3 + DynamoDB / GCS / Azure Blob) | ADR            |
| State Locking        | Enabled (DynamoDB / GCS / Azure Blob)  | Never             |
| Provider Pinning     | Pessimistic constraint (`~> X.Y`)      | Never             |
| Module Source        | Private registry or Git tags           | ADR               |
| Formatting           | `terraform fmt`                        | Never             |
| Validation           | `terraform validate` + `tflint`        | Never             |
| Security Scanning    | `tfsec` or `checkov`                   | ADR               |
| Workspace Strategy   | Directory-based (one root per env)     | ADR               |
| Variable Defaults    | Explicit — no implicit defaults for required values | Never |

### Alternatives

| Primary                     | Alternative              | When                                    |
|-----------------------------|--------------------------|-----------------------------------------|
| HCL                         | CDKTF (TypeScript/Python)| Team has no HCL experience              |
| S3 + DynamoDB backend       | Terraform Cloud          | Need built-in RBAC and run management   |
| Directory-per-env           | Terraform workspaces     | Identical envs differing only by tfvars |
| `tflint`                    | `sentinel` (Terraform Cloud) | Enterprise policy enforcement        |
| `tfsec`                     | `checkov`                | Multi-framework scanning (K8s, ARM)     |
| Pessimistic pinning (`~>`)  | Exact pinning (`=`)      | Compliance requires exact reproducibility|
| Git-tagged modules          | Terraform Registry       | Public module sharing                   |

---

## Project Structure

```
infrastructure/
  modules/                         # Reusable modules (no provider config)
    networking/
      main.tf                      # Resources
      variables.tf                 # Input variables
      outputs.tf                   # Output values
      versions.tf                  # Required providers + terraform block
      README.md                    # Module documentation
    compute/
      main.tf
      variables.tf
      outputs.tf
      versions.tf
  environments/                    # Root modules (one per environment)
    dev/
      main.tf                      # Module calls + provider config
      variables.tf                 # Environment-specific variables
      outputs.tf                   # Root outputs
      backend.tf                   # State backend config
      terraform.tfvars             # Variable values (NOT committed for secrets)
      versions.tf                  # Terraform + provider version constraints
    staging/
      ...
    prod/
      ...
  global/                          # Shared resources (DNS, IAM, state buckets)
    main.tf
    backend.tf
    versions.tf
  scripts/
    plan.sh                        # Wrapper: init + plan with correct backend
    apply.sh                       # Wrapper: apply with approval gate
  .tflint.hcl                      # Linter configuration
  .terraform-version               # tfenv version pinning
```

**Rules:**
- `modules/` contains reusable modules. No provider or backend configuration in
  modules. Providers are passed in by the root module.
- `environments/` contains root modules — one per environment. Each root module
  configures its own backend, providers, and calls shared modules.
- `global/` holds resources shared across all environments (DNS zones, IAM roles,
  state-management infrastructure).
- Never commit `.terraform/` directories, `*.tfstate` files, or files containing
  secrets.
- Every module has a `versions.tf` with `required_providers` blocks.
- One resource type per file is acceptable for large modules. For smaller modules,
  group logically related resources in `main.tf`.

---

## Provider Configuration

```hcl
# versions.tf — pin providers with pessimistic constraints.
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# main.tf — configure the provider in root modules only.
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "terraform"
      Project     = var.project_name
    }
  }
}

# For multi-region or multi-account, use provider aliases.
provider "aws" {
  alias  = "us_west"
  region = "us-west-2"
}

resource "aws_s3_bucket" "replica" {
  provider = aws.us_west
  bucket   = "${var.project_name}-replica-${var.environment}"
}
```

**Rules:**
- Pin providers with pessimistic constraints (`~> 5.0`). This allows patch updates
  but blocks breaking major changes.
- Configure providers only in root modules, never in child modules. Pass providers
  to child modules via the `providers` argument.
- Use `default_tags` (AWS) or equivalent to ensure all resources are tagged with
  environment, project, and `ManagedBy = "terraform"`.
- Never hardcode credentials in provider blocks. Use environment variables, instance
  profiles, or workload identity.
- Use provider aliases for multi-region or multi-account deployments.

---

## Naming Conventions

| Element              | Convention                 | Example                          |
|----------------------|----------------------------|----------------------------------|
| Resources            | `snake_case`               | `aws_s3_bucket.app_data`         |
| Variables            | `snake_case`               | `var.instance_type`              |
| Outputs              | `snake_case`               | `output.vpc_id`                  |
| Modules              | `kebab-case` (directory)   | `modules/networking/`            |
| Module calls         | `snake_case`               | `module.networking`              |
| Locals               | `snake_case`               | `local.common_tags`              |
| Data sources         | `snake_case`               | `data.aws_ami.amazon_linux`      |
| Files                | `snake_case.tf`            | `security_groups.tf`             |
| Environment dirs     | `lowercase`                | `environments/prod/`             |

**Rules:**
- Resource names describe what, not how: `aws_s3_bucket.app_logs`, not
  `aws_s3_bucket.bucket1`.
- Use consistent prefixes in resource names when a module manages multiple
  instances of the same type: `aws_subnet.public`, `aws_subnet.private`.
- Variables must have `description` and `type`. Use `validation` blocks for
  constraints.
- Outputs must have `description`. Expose only what consumers need.

---

## Variables and Outputs

```hcl
# variables.tf — always include type, description, and validation.
variable "environment" {
  type        = string
  description = "Deployment environment (dev, staging, prod)."

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type for the application servers."
  default     = "t3.medium"
}

variable "enable_monitoring" {
  type        = bool
  description = "Whether to enable detailed CloudWatch monitoring."
  default     = true
}

# outputs.tf — expose only what downstream consumers need.
output "vpc_id" {
  description = "ID of the VPC created by this module."
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs."
  value       = aws_subnet.private[*].id
}
```

**Rules:**
- Every variable must have `type` and `description`. No untyped variables.
- Use `validation` blocks to catch invalid inputs early, before `plan`.
- Never set defaults for values that must differ per environment (account IDs,
  domain names). Force callers to provide them.
- Use `sensitive = true` for variables and outputs that contain secrets.
- Group variables logically: required first, optional with defaults second.

---

## Do / Don't

### Do
- Pin Terraform and all provider versions. Use pessimistic constraints (`~> X.Y`).
- Use remote state with locking enabled. Never use local state in shared environments.
- Run `terraform fmt` and `terraform validate` before every commit.
- Run `tflint` and `tfsec`/`checkov` in CI on every pull request.
- Tag all resources with `Environment`, `Project`, and `ManagedBy = "terraform"`.
- Use `data` sources to reference existing resources instead of hardcoding IDs.
- Write modules with clear inputs (`variables.tf`), outputs (`outputs.tf`), and
  documentation (`README.md`).
- Use `terraform plan` output as the source of truth for change reviews. Never
  `apply` without reviewing the plan.
- Store `.terraform.lock.hcl` in version control. It pins exact provider versions.

### Don't
- Commit `*.tfstate` files or `.terraform/` directories to version control.
- Hardcode credentials, account IDs, or resource IDs. Use variables and data sources.
- Use `terraform workspace` for environments that differ structurally. Workspaces
  share the same code, so structural differences require separate root modules.
- Apply changes to production without a peer-reviewed plan output.
- Use `count` for resources that have stable identity requirements. Use `for_each`
  with a map or set instead.
- Nest modules more than two levels deep. Flat composition is easier to debug.
- Use `depends_on` unless there is a hidden dependency Terraform cannot infer from
  resource references.
- Use provisioners (`local-exec`, `remote-exec`) for configuration management.
  Use Ansible, cloud-init, or user data instead.

---

## Common Pitfalls

1. **State file conflicts** — Two engineers running `apply` simultaneously without
   state locking causes corruption. Always enable locking (DynamoDB for S3, native
   for GCS/Azure Blob). Never disable it.
2. **Count index shifting** — Using `count` creates resources identified by index
   (`[0]`, `[1]`). Removing an item from the middle shifts all subsequent indices,
   causing destroys and recreates. Use `for_each` with stable keys instead.
3. **Workspace sprawl** — Creating workspaces ad-hoc leads to orphaned state files
   and resources nobody tracks. Prefer directory-per-environment for visibility.
4. **Provider version drift** — Not pinning providers causes different engineers
   to use different versions, producing inconsistent plans. Commit
   `.terraform.lock.hcl` and pin with `~>`.
5. **Secrets in state** — Terraform stores all resource attributes in state,
   including passwords and keys. Encrypt state at rest (S3 SSE, GCS CMEK) and
   restrict access to the state backend.
6. **Monolithic root modules** — Putting all infrastructure in a single root module
   makes plans slow and blast radius large. Split by lifecycle: networking, compute,
   data, monitoring.
7. **Hardcoded AMIs / resource IDs** — Hardcoded IDs break across regions and
   accounts. Use `data` sources to look up AMIs, VPCs, and subnets dynamically.
8. **Ignoring plan output** — Running `apply -auto-approve` without reading the
   plan. A plan that destroys and recreates a database will execute silently.
   Always review plans, especially for destructive changes.

---

## Checklist

- [ ] Terraform version pinned in `versions.tf` with `required_version`.
- [ ] All providers pinned with pessimistic constraints (`~> X.Y`).
- [ ] `.terraform.lock.hcl` committed to version control.
- [ ] Remote state backend configured with locking enabled.
- [ ] State bucket encrypted at rest with access restricted to authorized roles.
- [ ] `terraform fmt` applied; CI rejects unformatted code.
- [ ] `terraform validate` and `tflint` run in CI; no warnings.
- [ ] `tfsec` or `checkov` scan runs in CI; no high-severity findings.
- [ ] All variables have `type`, `description`, and `validation` where applicable.
- [ ] All outputs have `description`.
- [ ] No hardcoded credentials, account IDs, or resource IDs.
- [ ] All resources tagged with `Environment`, `Project`, `ManagedBy`.
- [ ] Modules document inputs, outputs, and usage in `README.md`.
- [ ] `for_each` used instead of `count` for resources needing stable identity.
- [ ] No secrets committed to version control (`.tfvars` with secrets in `.gitignore`).
