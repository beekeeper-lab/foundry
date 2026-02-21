# Terraform Module Design

Patterns for writing reusable, composable Terraform modules. A module is a
directory of `.tf` files that encapsulates a logical group of resources behind
a clean interface of inputs and outputs.

---

## Module Structure

```
modules/
  networking/
    main.tf              # Resource definitions
    variables.tf         # All input variables
    outputs.tf           # All output values
    versions.tf          # required_providers block
    locals.tf            # Computed local values (optional)
    data.tf              # Data sources (optional)
    README.md            # Usage examples, input/output tables
  compute/
    main.tf
    variables.tf
    outputs.tf
    versions.tf
```

**Rules:**
- Every module must have `variables.tf`, `outputs.tf`, and `versions.tf`.
- `main.tf` contains the core resources. Split into additional files only when a
  module grows beyond ~200 lines.
- `versions.tf` declares `required_providers` but never configures them. Providers
  are configured by the calling root module.
- `README.md` is mandatory. Include a usage example, input table, and output table.

---

## Module Interface Design

```hcl
# variables.tf — define the module's public API.
variable "name" {
  type        = string
  description = "Name prefix for all resources created by this module."

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,28}[a-z0-9]$", var.name))
    error_message = "Name must be 3-30 lowercase alphanumeric characters or hyphens."
  }
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC."
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "Must be a valid CIDR block."
  }
}

variable "availability_zones" {
  type        = list(string)
  description = "List of availability zones to deploy subnets into."
}

variable "tags" {
  type        = map(string)
  description = "Additional tags to apply to all resources."
  default     = {}
}
```

```hcl
# outputs.tf — expose only what consumers need.
output "vpc_id" {
  description = "ID of the created VPC."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs."
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Map of AZ to private subnet ID."
  value       = { for k, v in aws_subnet.private : k => v.id }
}
```

**Rules:**
- Inputs define the module's API. Keep the surface area small — expose only what
  callers need to customize.
- Use `validation` blocks to fail fast on invalid inputs.
- Accept a `tags` map variable and merge it with module-level tags using `merge()`.
- Outputs are the module's return values. Expose IDs, ARNs, and endpoints — not
  entire resource objects.
- Use `sensitive = true` on outputs containing secrets.

---

## Module Composition

```hcl
# environments/prod/main.tf — compose modules in root modules.
module "networking" {
  source = "../../modules/networking"

  name               = "myapp-prod"
  vpc_cidr           = "10.1.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

  tags = local.common_tags
}

module "compute" {
  source = "../../modules/compute"

  name              = "myapp-prod"
  vpc_id            = module.networking.vpc_id
  subnet_ids        = module.networking.private_subnet_ids
  instance_type     = "m5.large"
  min_instances     = 3
  max_instances     = 10

  tags = local.common_tags
}

module "database" {
  source = "../../modules/database"

  name              = "myapp-prod"
  vpc_id            = module.networking.vpc_id
  subnet_ids        = module.networking.private_subnet_ids
  instance_class    = "db.r6g.xlarge"
  multi_az          = true

  tags = local.common_tags
}
```

**Rules:**
- Root modules compose child modules. Child modules never call other child modules.
  Keep the dependency graph flat.
- Pass data between modules via outputs and variables, not via `terraform_remote_state`
  within the same root module.
- Use `terraform_remote_state` only to reference outputs from a different root module
  (e.g., networking root referencing global root).
- Never nest modules more than two levels (root → child). Deep nesting makes
  debugging plan output nearly impossible.
- Use `locals` in root modules to define shared values (tags, naming conventions)
  passed to multiple child modules.

---

## Module Versioning

```hcl
# Reference modules by Git tag for version control.
module "networking" {
  source = "git::https://github.com/org/tf-modules.git//networking?ref=v2.1.0"
}

# Or from a private Terraform registry.
module "networking" {
  source  = "app.terraform.io/org/networking/aws"
  version = "~> 2.1"
}

# Local path for modules in the same repo.
module "networking" {
  source = "../../modules/networking"
}
```

**Rules:**
- In monorepos, use relative paths (`../../modules/networking`). Modules evolve
  with the infrastructure.
- For shared modules across repos, use Git tags (`?ref=v2.1.0`) or a private
  registry with semantic versioning.
- Never reference a branch (`ref=main`) in production. Branches are mutable —
  use immutable tags.
- Follow semantic versioning: breaking input/output changes are major bumps,
  new optional features are minor, bug fixes are patch.
- Document breaking changes in the module's CHANGELOG or README.

---

## Module Testing

```hcl
# tests/networking_test.tftest.hcl — Terraform native testing (1.6+).
run "creates_vpc_with_correct_cidr" {
  command = plan

  variables {
    name               = "test"
    vpc_cidr           = "10.99.0.0/16"
    availability_zones = ["us-east-1a"]
    tags               = { Test = "true" }
  }

  assert {
    condition     = aws_vpc.main.cidr_block == "10.99.0.0/16"
    error_message = "VPC CIDR does not match input."
  }
}

run "validates_name_format" {
  command = plan

  variables {
    name               = "INVALID_NAME"
    vpc_cidr           = "10.0.0.0/16"
    availability_zones = ["us-east-1a"]
  }

  expect_failures = [var.name]
}
```

**Rules:**
- Use Terraform native tests (`.tftest.hcl`, Terraform 1.6+) for plan-level
  validation. They run `terraform plan` without provisioning real resources.
- Use `command = plan` for fast unit-style tests. Use `command = apply` only for
  integration tests that need real resources.
- Test validation rules by asserting `expect_failures`.
- For integration tests, use Terratest (Go) or `pytest-terraform` when you need
  to verify real infrastructure behavior.
- Store test files in a `tests/` directory within the module.

---

## Common Module Anti-Patterns

1. **God module** — One module that creates VPC, subnets, security groups, load
   balancers, databases, and DNS records. Split by lifecycle and responsibility.
2. **Hardcoded values** — Module contains hardcoded AMIs, CIDRs, or account IDs.
   Expose these as variables with validation.
3. **Missing outputs** — Module creates resources but exposes nothing. Consumers
   cannot reference the module's resources without outputs.
4. **Provider in module** — Child module configures a provider. This prevents the
   root module from controlling provider settings and breaks multi-region patterns.
5. **Conditional resources via count** — Using `count = var.enabled ? 1 : 0`
   creates fragile resources addressed by index. Prefer separate modules or
   `for_each` with a map.
6. **Implicit dependencies on external state** — Module uses
   `terraform_remote_state` internally. This hides dependencies and breaks
   portability. Accept required values as variables instead.
