# Technical Writer / Doc Owner -- Outputs

This document enumerates every artifact the Technical Writer / Doc Owner is
responsible for producing, including quality standards and who consumes each
deliverable.

---

## 1. Project README

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Project README                                     |
| **Cadence**        | One per project; updated with each significant change |
| **Template**       | `personas/technical-writer/templates/readme.md`    |
| **Format**         | Markdown                                           |

**Description.** The project's front door -- the first document a new developer,
operator, or stakeholder reads. The README communicates what the project does,
how to set it up, how to use it, and where to find more detailed documentation.

**Quality Bar:**
- A new developer can clone the repository and have the project running locally
  by following only the README instructions, without asking for help.
- All commands and code examples have been tested on a clean environment and
  verified to work as written.
- Prerequisites are listed with specific versions (e.g., "Python >= 3.11",
  not "Python 3").
- The project description explains what the project does and who it is for in
  three sentences or fewer.
- Links to other documentation (runbooks, API docs, architecture) are present
  and validated.
- No placeholder text, TODO markers, or draft sections remain.

**Downstream Consumers:** Developer (for project setup), new team members (for
onboarding), Architect (for project overview), external stakeholders (for
project understanding).

---

## 2. Operational Runbook

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Operational Runbook                                |
| **Cadence**        | One per operational procedure; updated as procedures change |
| **Template**       | `personas/technical-writer/templates/runbook.md`   |
| **Format**         | Markdown                                           |

**Description.** A step-by-step procedure document for operational tasks such as
deployment, rollback, incident response, database migration, or environment
setup. Runbooks enable an operator to execute critical procedures reliably,
even under pressure, without relying on memory or tribal knowledge.

**Quality Bar:**
- Each step is a single, unambiguous action. No step combines multiple
  operations or requires interpretation.
- Every command is copy-pasteable and includes the expected output so the
  operator can confirm each step succeeded.
- Preconditions are listed explicitly: required access, environment state,
  dependencies that must be running.
- Failure handling is included for each step that can fail: what the error
  looks like, what to do, and when to escalate.
- The runbook has been executed end-to-end by someone other than the author
  to verify completeness.
- Rollback instructions are included for destructive operations.

**Downstream Consumers:** DevOps-Release (for deployment execution), Developer
(for environment setup), Team Lead (for incident response coordination), on-call
operators (for production procedures).

---

## 3. ADR Index

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | ADR Index                                          |
| **Cadence**        | Updated whenever an ADR is added, deprecated, or superseded |
| **Template**       | `personas/technical-writer/templates/adr-index.md` |
| **Format**         | Markdown                                           |

**Description.** A navigable index of all Architecture Decision Records in the
project, summarized for quick scanning. The ADR index allows team members to
find relevant decisions without reading every ADR, and provides a historical
timeline of how the architecture has evolved.

**Quality Bar:**
- Every ADR in the project is listed -- no gaps or missing entries.
- Each entry includes: ADR number, title, status (Accepted, Deprecated,
  Superseded), date, and a one-sentence summary.
- Entries are ordered chronologically by ADR number.
- Superseded ADRs link to their replacements; deprecated ADRs note the reason.
- The index is updated within one working day of any ADR status change.

**Downstream Consumers:** Architect (for decision tracking), Developer (for
understanding design constraints), new team members (for architectural context),
Compliance / Risk Analyst (for audit trail).

---

## 4. Onboarding Guide

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Onboarding Guide                                   |
| **Cadence**        | One per project; updated as tooling or processes change |
| **Template**       | `personas/technical-writer/templates/onboarding-guide.md` |
| **Format**         | Markdown                                           |

**Description.** A comprehensive guide for new team members covering everything
they need to become productive: project context, development environment setup,
team processes, communication channels, key contacts, and where to find
documentation.

**Quality Bar:**
- A new team member can complete the onboarding process independently by
  following the guide, without needing verbal instructions.
- Environment setup instructions are tested on a fresh machine and produce a
  working development environment.
- The guide covers: project overview, repository structure, development
  workflow, testing approach, deployment process, and team communication norms.
- Key contacts and escalation paths are listed with roles, not just names
  (so the guide survives team changes).
- Links to deeper documentation (README, runbooks, architecture docs) are
  provided for each topic rather than duplicating content.

**Downstream Consumers:** New team members (primary consumer), Team Lead (for
onboarding process management), Developer (for reference on team conventions).

---

## 5. API Documentation

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | API Documentation                                  |
| **Cadence**        | One per API surface; updated with every API change  |
| **Template**       | `personas/technical-writer/templates/api-docs.md`  |
| **Format**         | Markdown                                           |

**Description.** User-facing documentation for the project's APIs, covering
endpoints, request/response formats, authentication, error handling, and usage
examples. API documentation translates the technical API contract into a
resource that consumers can use to integrate with the system successfully.

**Quality Bar:**
- Every public endpoint is documented with: method, path, description,
  request parameters, request body schema, response schema, and error codes.
- At least one complete request/response example is provided per endpoint,
  using realistic (not placeholder) data.
- Authentication and authorization requirements are stated per endpoint or
  per group of endpoints.
- Error responses are documented with the error code, description, and
  suggested resolution.
- The documentation matches the current implementation -- verified against
  the live or staging API.
- Common workflows are documented as end-to-end tutorials.

**Downstream Consumers:** Developer (for API integration), external consumers
(for third-party integration), Tech QA (for API test planning), Architect (for
API contract verification).

---

## 6. Style Guide

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Documentation Style Guide                          |
| **Cadence**        | One per project; updated as conventions evolve     |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** The authoritative reference for how documentation is written
in the project. The style guide defines terminology, tone, formatting
conventions, and structural patterns so that documentation produced by any
persona is consistent and professional.

**Required Sections:**
1. **Voice and Tone** -- Active vs. passive voice preference, formality level,
   and audience-awareness guidelines.
2. **Terminology** -- Canonical terms for project concepts with definitions.
   If it is "deploy" in the style guide, it is "deploy" everywhere.
3. **Formatting Conventions** -- Heading levels, code block usage, list
   formatting, table structure, and link conventions.
4. **File and Naming Conventions** -- How documentation files are named,
   organized, and versioned.
5. **Examples** -- Before-and-after examples showing correct and incorrect
   application of the style guide rules.

**Quality Bar:**
- A new contributor can produce documentation that passes review by following
  the style guide alone, without verbal coaching.
- Terminology entries are specific: they define what the term means in this
  project, not generic dictionary definitions.
- Formatting rules are concrete and testable: "Use H2 for major sections,
  H3 for subsections" not "Use appropriate heading levels."
- The style guide is concise enough to read in fifteen minutes.

**Downstream Consumers:** All personas who produce documentation (Developer,
Architect, DevOps-Release, etc.), Code Quality Reviewer (for documentation
review standards), new team members (for writing consistency).

---

## Output Format Guidelines

- All deliverables are written in Markdown and committed to the project
  repository.
- The project README lives at the repository root. All other documentation
  lives in `docs/` with a clear directory structure.
- Runbooks are stored in `docs/runbooks/` with descriptive filenames
  (e.g., `runbook-database-migration.md`).
- The ADR index lives in `docs/adr/` alongside the ADRs it indexes.
- API documentation lives in `docs/api/` or is generated from source
  annotations into a `docs/api/` output directory.
- The style guide lives at `docs/style-guide.md` and is linked from the
  project README.
- Cross-references between documents use relative links that work in both
  the repository and any documentation site generator.
