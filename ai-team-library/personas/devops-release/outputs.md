# DevOps / Release Engineer -- Outputs

This document enumerates every artifact the DevOps / Release Engineer is
responsible for producing, including quality standards and who consumes each
deliverable.

---

## 1. Release Runbook

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Release Runbook                                    |
| **Cadence**        | One per service or deployment target; updated per release cycle |
| **Template**       | `personas/devops-release/templates/release-runbook.md` |
| **Format**         | Markdown                                           |

**Description.** A step-by-step operational guide that describes exactly how to
deploy a release to each target environment. The runbook eliminates tribal
knowledge by encoding every deployment action -- from pre-flight checks through
post-deployment verification -- into a procedure that any team member can
execute. When it is 2 AM and the on-call engineer needs to push a hotfix, this
is the document they follow.

**Quality Bar:**
- Every step is numbered and includes the exact command, script, or UI action
  to perform.
- Pre-deployment checks are explicit: pipeline status, artifact verification,
  database migration readiness, and feature flag state.
- The runbook specifies the expected outcome of each step so the operator can
  verify success before proceeding.
- Environment-specific variables (URLs, service names, region identifiers) are
  parameterized, not hardcoded.
- The runbook includes estimated duration for each step and total deployment
  time.
- Failure handling is documented for each step: what to do if the step fails,
  and at what point to trigger a rollback.
- The runbook has been executed successfully at least once in a staging
  environment before being considered complete.

**Downstream Consumers:** Team Lead (for release planning and scheduling),
Developer (for understanding deployment process), Compliance / Risk Analyst (for
audit trail of deployment procedures).

---

## 2. CI/CD Pipeline Review

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | CI/CD Pipeline Review                              |
| **Cadence**        | At pipeline creation; updated when pipeline configuration changes |
| **Template**       | `personas/devops-release/templates/pipeline-yaml-review.md` |
| **Format**         | Markdown                                           |

**Description.** A structured review of the CI/CD pipeline configuration,
assessing correctness, security, performance, and alignment with project
standards. The review covers every stage from source checkout through artifact
publication and deployment, identifying misconfigurations, security gaps, and
optimization opportunities.

**Quality Bar:**
- Every pipeline stage (build, test, lint, security scan, deploy) is reviewed
  and documented with its purpose and expected behavior.
- Security checks are verified: secrets are not exposed in logs, service
  accounts use least-privilege permissions, and artifact integrity is validated.
- Build reproducibility is confirmed: the same commit produces the same artifact
  on repeated runs.
- Test stage coverage is assessed: unit, integration, and any required
  compliance or security scans are present and blocking.
- Pipeline performance is measured: total run time, parallelization
  opportunities, and caching effectiveness are documented.
- Failure modes are analyzed: what happens when each stage fails, whether
  subsequent stages are correctly blocked, and whether notifications fire.
- Dependencies on external services (registries, cloud APIs, third-party
  scanners) are identified with fallback behavior documented.

**Downstream Consumers:** Developer (for understanding build and test
expectations), Security Engineer (for pipeline security posture), Team Lead (for
pipeline reliability and cycle time metrics).

---

## 3. Rollback Runbook

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Rollback Runbook                                   |
| **Cadence**        | One per service or deployment target; updated when deployment architecture changes |
| **Template**       | `personas/devops-release/templates/rollback-runbook.md` |
| **Format**         | Markdown                                           |

**Description.** A step-by-step procedure for reverting a deployment to the
previous known-good state. The rollback runbook is the safety net that makes
deployments reversible. It covers application rollback, database migration
reversal, configuration restoration, and cache invalidation -- everything
required to return the system to its pre-deployment state.

**Quality Bar:**
- The runbook specifies the rollback strategy: blue-green switch, canary
  revert, artifact redeployment, or database restore, with rationale for the
  chosen approach.
- Every step includes the exact command or action, the expected outcome, and
  verification criteria.
- Database rollback is addressed explicitly: whether migrations are reversible,
  whether data written since deployment must be preserved, and how schema
  conflicts are resolved.
- The estimated rollback time is documented and meets the project's recovery
  time objective (RTO).
- The runbook identifies the decision criteria for initiating a rollback: which
  metrics, error rates, or health check failures trigger the procedure.
- Post-rollback verification steps confirm the system is functioning correctly
  in the reverted state.
- The runbook has been tested in a staging environment -- an untested rollback
  procedure is not a rollback procedure.

**Downstream Consumers:** Team Lead (for incident response planning), Developer
(for understanding rollback implications on their changes), Compliance / Risk
Analyst (for operational continuity documentation).

---

## 4. Environment Matrix

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Environment Matrix                                 |
| **Cadence**        | Created at project start; updated when environments change |
| **Template**       | `personas/devops-release/templates/environment-matrix.md` |
| **Format**         | Markdown                                           |

**Description.** A comprehensive reference document that catalogues every
deployment environment (development, staging, production, and any others),
their configurations, access controls, and the differences between them. The
environment matrix is the single source of truth for how environments are
structured and how they relate to each other.

**Quality Bar:**
- Every environment is listed with its purpose, URL or access method, and
  the branch or artifact version it tracks.
- Configuration differences between environments are explicitly documented:
  database endpoints, feature flags, resource limits, and third-party service
  tiers.
- Access controls are specified per environment: who can deploy, who can access
  logs, and who has administrative access.
- Environment parity is assessed: documented deviations between staging and
  production are flagged with rationale (e.g., "staging uses a smaller database
  instance to reduce cost").
- Infrastructure-as-code references are linked: the Terraform modules, Helm
  charts, or configuration files that define each environment.
- The matrix includes environment health check endpoints and monitoring
  dashboard links.
- Refresh and lifecycle policies are documented: how often environments are
  rebuilt, when ephemeral environments are torn down.

**Downstream Consumers:** Developer (for local and staging environment setup),
Tech QA (for test environment configuration), Security Engineer (for access
control review), Architect (for deployment topology reference).

---

## 5. Secrets Rotation Plan

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Secrets Rotation Plan                              |
| **Cadence**        | Created at project start; updated when secrets inventory changes |
| **Template**       | `personas/devops-release/templates/secrets-rotation-plan.md` |
| **Format**         | Markdown                                           |

**Description.** A plan that inventories all secrets used by the system (API
keys, database credentials, service account tokens, encryption keys) and defines
the rotation schedule, procedure, and responsible party for each. The plan
ensures that credentials are rotated regularly and that rotation can be performed
without downtime.

**Quality Bar:**
- Every secret is catalogued with its type, the system or service it
  authenticates to, and the secrets manager where it is stored.
- Rotation cadence is defined per secret based on risk: high-risk credentials
  (production database, payment gateway) rotate more frequently than low-risk
  ones.
- The rotation procedure for each secret is documented step by step, including
  how to update dependent services without downtime.
- Automated rotation is identified where supported, with manual rotation
  procedures documented as a fallback.
- The plan defines who is authorized to perform rotation and who must be
  notified.
- Emergency rotation procedures are documented for the scenario where a secret
  is compromised and must be rotated immediately.
- The plan includes verification steps to confirm that services are functioning
  correctly after rotation.

**Downstream Consumers:** Security Engineer (for security posture review),
Compliance / Risk Analyst (for audit evidence of credential management), Team
Lead (for operational scheduling).

---

## 6. Deployment Verification Report

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Deployment Verification Report                     |
| **Cadence**        | One per production deployment                      |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** A post-deployment report that documents what was deployed, when
it was deployed, and the results of all verification checks. The report provides
an auditable record of every production change and confirms that the deployment
met the project's quality and stability criteria.

**Required Sections:**
1. **Deployment Summary** -- Release version, commit SHA, deploying engineer,
   timestamp, and target environment.
2. **Pre-Deployment Checks** -- Status of each pre-flight check: pipeline
   green, artifact hash verified, database migrations reviewed, feature flags
   configured.
3. **Deployment Execution** -- Steps executed, any deviations from the runbook,
   and the time taken.
4. **Health Check Results** -- Status of automated health checks, endpoint
   response times, error rates, and key business metrics compared to
   pre-deployment baseline.
5. **Verification Sign-Off** -- Confirmation that the deployment meets
   acceptance criteria, with the name of the verifying engineer.
6. **Issues Encountered** -- Any problems during deployment, how they were
   resolved, and whether the runbook needs updating as a result.

**Quality Bar:**
- The report is created within one hour of deployment completion, not
  retroactively assembled days later.
- Health check results include specific numbers: "p95 latency 142ms (baseline
  138ms), error rate 0.02% (baseline 0.01%)" not "looks normal."
- Any deviation from the standard runbook is documented with the reason and
  outcome.
- The report links to the pipeline execution log, the release notes, and the
  relevant runbook version.
- Issues encountered include follow-up actions: runbook updates, pipeline
  fixes, or monitoring improvements.

**Downstream Consumers:** Team Lead (for release status tracking), Compliance /
Risk Analyst (for deployment audit trail), Security Engineer (for change
management records), Architect (for deployment performance trends).

---

## Output Format Guidelines

- All deliverables are written in Markdown and committed to the project
  repository under `docs/ops/` or `docs/release/`.
- Runbooks are versioned alongside the deployment configuration they describe.
  An outdated runbook is worse than no runbook because it creates false
  confidence.
- Environment matrices and secrets rotation plans are living documents updated
  in place, with version history tracked by the repository.
- Deployment verification reports are immutable once created -- they are
  historical records, not living documents.
- Use parameterized placeholders (e.g., `${ENV}`, `${VERSION}`) in runbook
  commands rather than hardcoded values, so the same runbook serves all
  environments.
- Pipeline review documents reference the specific pipeline configuration file
  and commit SHA reviewed, so the assessment can be tied to a known state.
