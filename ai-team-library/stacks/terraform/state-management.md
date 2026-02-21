# Terraform State Management

State is Terraform's source of truth for what infrastructure exists. Mismanaging
state causes resource leaks, conflicts, and outages. This guide covers backend
configuration, locking, migration, and workspace strategies.

---

## Backend Configuration

```hcl
# backend.tf — S3 backend with DynamoDB locking (AWS).
terraform {
  backend "s3" {
    bucket         = "myorg-terraform-state"
    key            = "prod/networking/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

```hcl
# backend.tf — GCS backend (Google Cloud).
terraform {
  backend "gcs" {
    bucket = "myorg-terraform-state"
    prefix = "prod/networking"
  }
}
```

```hcl
# backend.tf — Azure Blob backend.
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "myorgterraformstate"
    container_name       = "tfstate"
    key                  = "prod/networking/terraform.tfstate"
  }
}
```

**Rules:**
- Always use a remote backend in shared environments. Local state (`terraform.tfstate`
  on disk) is only acceptable for throwaway experiments.
- Enable encryption at rest on the state bucket (S3 SSE-S3 / SSE-KMS, GCS CMEK,
  Azure Storage encryption).
- Enable versioning on the state bucket. This provides rollback if state becomes
  corrupted.
- Use a consistent key naming scheme: `{env}/{component}/terraform.tfstate`.
- Restrict access to the state bucket with IAM policies. Only CI/CD pipelines and
  authorized engineers should read/write state.

---

## State Locking

| Backend  | Locking Mechanism     | Setup Required               |
|----------|-----------------------|------------------------------|
| S3       | DynamoDB table        | Create table with `LockID` partition key |
| GCS      | Native (built-in)    | None                         |
| Azure    | Native (blob leases) | None                         |
| Terraform Cloud | Native         | None                         |
| Consul   | Native (sessions)    | Consul cluster required      |

```hcl
# DynamoDB lock table (create once, shared across all state files).
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    ManagedBy = "terraform"
    Purpose   = "terraform-state-locking"
  }
}
```

**Rules:**
- Never disable state locking. Concurrent applies without locking corrupt state.
- If a lock is stuck (engineer's session crashed), use `terraform force-unlock <ID>`
  only after confirming no apply is running. Document the incident.
- The lock table / mechanism is shared across all state files in the same backend.
  Create it once in the `global/` root module.

---

## State Isolation Strategies

### Directory-Based Isolation (Recommended)

```
environments/
  dev/
    backend.tf       # key = "dev/app/terraform.tfstate"
  staging/
    backend.tf       # key = "staging/app/terraform.tfstate"
  prod/
    backend.tf       # key = "prod/app/terraform.tfstate"
```

Each environment is a separate root module with its own state file. Environments
are completely isolated — a bad `apply` in dev cannot affect prod state.

### Workspace-Based Isolation

```bash
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

terraform workspace select prod
terraform apply -var-file="prod.tfvars"
```

Workspaces share the same code and backend but use separate state files within the
backend. The workspace name is available as `terraform.workspace`.

### When to Use Each

| Strategy              | Use When                                          |
|-----------------------|---------------------------------------------------|
| Directory-based       | Environments differ structurally (different modules, resources) |
| Directory-based       | Teams need independent blast radius per environment |
| Directory-based       | State access policies differ per environment       |
| Workspace-based       | Environments are structurally identical (same code, different vars) |
| Workspace-based       | Rapid prototyping with ephemeral environments      |

**Rules:**
- Default to directory-based isolation. It provides the clearest separation.
- Workspaces are appropriate only when environments use identical code and differ
  only in variable values.
- Never mix workspace-based and directory-based isolation in the same project.
- If using workspaces, gate production applies with CI/CD — never allow
  `terraform workspace select prod && terraform apply` from a local machine.

---

## Cross-Stack References

```hcl
# Read outputs from another root module's state.
data "terraform_remote_state" "networking" {
  backend = "s3"

  config = {
    bucket = "myorg-terraform-state"
    key    = "prod/networking/terraform.tfstate"
    region = "us-east-1"
  }
}

# Use the referenced outputs.
module "compute" {
  source = "../../modules/compute"

  vpc_id     = data.terraform_remote_state.networking.outputs.vpc_id
  subnet_ids = data.terraform_remote_state.networking.outputs.private_subnet_ids
}
```

**Rules:**
- Use `terraform_remote_state` only for cross-stack references (different root
  modules). Within a root module, pass data via module outputs.
- Only reference `outputs` from remote state, never internal resource attributes.
  This respects module encapsulation.
- Document remote state dependencies in the root module's README.
- Consider using SSM Parameter Store, Consul KV, or a similar service for
  cross-stack data sharing if remote state references become complex.

---

## State Migration

### Moving State Between Backends

```bash
# 1. Update backend configuration in backend.tf.
# 2. Run init — Terraform detects the backend change and offers to migrate.
terraform init -migrate-state

# 3. Verify the new state.
terraform plan   # Should show no changes if migration was clean.
```

### Moving Resources Between State Files

```bash
# Remove a resource from one state (does NOT destroy the resource).
terraform state rm aws_s3_bucket.logs

# Import the resource into another root module's state.
cd ../other-root-module
terraform import aws_s3_bucket.logs my-logs-bucket
```

### Renaming Resources in State

```hcl
# Use moved blocks (Terraform 1.1+) instead of state mv.
moved {
  from = aws_s3_bucket.data
  to   = aws_s3_bucket.app_data
}
```

**Rules:**
- Always use `moved` blocks for refactoring resource names. They are declarative,
  reviewable in PRs, and execute during `apply`.
- Never use `terraform state rm` + `terraform import` for renames. Use `moved`.
- Before any state migration, back up the current state:
  `terraform state pull > backup.tfstate`.
- After migration, run `terraform plan` to verify zero diff (no unintended changes).
- Remove `moved` blocks after they have been applied in all environments.

---

## State Security

- **Encrypt at rest:** Enable server-side encryption on the state bucket.
- **Encrypt in transit:** Use HTTPS endpoints (all major backends enforce this).
- **Restrict access:** State contains sensitive values (passwords, keys, tokens).
  Limit read/write to CI/CD service accounts and senior engineers.
- **Enable versioning:** Bucket versioning allows recovery from accidental overwrites
  or corruption.
- **Audit access:** Enable access logging on the state bucket. Alert on unexpected
  reads or writes.
- **Sensitive outputs:** Mark outputs containing secrets as `sensitive = true` to
  prevent them from appearing in CLI output and logs.

---

## Checklist

- [ ] Remote backend configured for all shared environments.
- [ ] State locking enabled (DynamoDB, native, or Terraform Cloud).
- [ ] State bucket encrypted at rest with versioning enabled.
- [ ] State bucket access restricted via IAM / RBAC policies.
- [ ] Consistent state key naming: `{env}/{component}/terraform.tfstate`.
- [ ] `terraform state pull > backup.tfstate` before any migration.
- [ ] `moved` blocks used for resource renames (not `state mv`).
- [ ] `terraform plan` shows zero diff after migration.
- [ ] Cross-stack references documented in root module README.
- [ ] No local state files committed to version control.
