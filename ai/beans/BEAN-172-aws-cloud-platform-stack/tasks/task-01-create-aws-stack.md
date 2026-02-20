# Task 01: Create AWS Cloud Platform Stack File

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-172-T01 |
| **Owner** | Developer |
| **Status** | Done |
| **Depends On** | — |
| **Started** | 2026-02-20 18:13 |
| **Completed** | 2026-02-20 18:13 |
| **Duration** | < 1m |

## Description

Create the AWS cloud platform stack files in `ai-team-library/stacks/aws-cloud-platform/`
following the standardized template pattern (Defaults table+alternatives, Do/Don't,
Common Pitfalls, Checklist).

## Inputs

- Existing stack files (devops/pipelines.md, security/hardening.md) for template pattern
- Bean acceptance criteria

## Outputs

- `ai-team-library/stacks/aws-cloud-platform/core-services.md` — IAM, VPC, Lambda, ECS, RDS, S3
- `ai-team-library/stacks/aws-cloud-platform/well-architected.md` — Well-Architected Framework, cost optimization, security

## Acceptance Criteria

- [x] Files follow standardized template pattern
- [x] Covers core AWS services (IAM, VPC, Lambda, ECS, RDS, S3)
- [x] Covers Well-Architected Framework pillars
- [x] Covers cost optimization strategies
- [x] Covers security best practices (least privilege, encryption, logging)