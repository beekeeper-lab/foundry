# AI Team Library

A library of reusable building blocks -- personas, templates, expertise, and workflows -- for assembling and operating agentic AI development teams. The library is designed for use with [Foundry](../), a PySide6 desktop application that compiles these building blocks into ready-to-use Claude Code project folders. Each building block is a self-contained markdown file that can also be read and used independently.

## Quick Start

1. **Clone the library** as part of the Foundry workspace (it lives at `ai-team-library/` inside the Foundry repo).
2. **Select your team** by choosing personas, expertise, and workflows that match your project needs.
3. **Compose a spec** by creating a `composition.yaml` that lists your selections (or use the Foundry UI to generate one).
4. **Run the pipeline** through Foundry to compile, scaffold, seed, and export a ready-to-use Claude Code project folder.

## Library Structure

```
ai-team-library/
  personas/           # 13 role constitutions (persona.md, outputs.md, prompts.md, templates/)
  expertise/          # 39 expertise conventions and skill files
  templates/shared/   # 7 cross-persona templates
  workflows/          # Pipeline and taxonomy reference docs
  claude/             # Claude Code integration (commands, skills, hooks)
  README.md           # This file
```

## Personas

Each persona directory contains a constitution (`persona.md`), expected outputs (`outputs.md`), prompt patterns (`prompts.md`), and a `templates/` directory with role-specific templates.

| Persona                   | Mission                                                                 |
|---------------------------|-------------------------------------------------------------------------|
| Team Lead                 | Orchestrate the team: decompose work, route tasks, enforce stage gates  |
| BA                        | Translate business needs into precise, actionable, testable requirements|
| Architect                 | Own system design, boundaries, NFRs, and architectural decisions        |
| Developer                 | Deliver clean, tested, incremental implementations                      |
| Tech-QA                   | Verify acceptance criteria, catch edge cases, prevent regressions       |
| Code Quality Reviewer     | Review code for readability, correctness, and adherence to standards    |
| DevOps / Release Engineer | Own CI/CD pipelines, environments, deployments, and rollback            |
| Security Engineer         | Identify, assess, and mitigate security risks via threat modeling       |
| Compliance / Risk Analyst | Map controls, gather evidence, manage regulatory risk                   |
| Researcher / Librarian    | Find references, compare options, deliver curated research              |
| Technical Writer          | Produce READMEs, runbooks, API docs, and onboarding guides              |
| UX / UI Designer          | Shape user experience through flows, wireframes, and content design     |
| Integrator / Merge Captain| Merge work from multiple personas into a conflict-free whole            |

## Expertise

Each expertise directory contains a `conventions.md` file defining domain standards, plus additional skill files as needed. Items span languages, architecture patterns, infrastructure, data/ML, compliance, and business practices.

| Expertise          | Scope                                           |
|--------------------|-------------------------------------------------|
| python             | Python language conventions, packaging, testing  |
| python-qt-pyside6  | PySide6 desktop application patterns             |
| react              | React component patterns, state management       |
| typescript         | TypeScript language conventions and type safety   |
| node               | Node.js runtime, server patterns, npm ecosystem  |
| java               | Java language conventions, build tools, patterns  |
| dotnet             | .NET / C# conventions, project structure          |
| go                 | Go language conventions, concurrency, tooling     |
| kotlin             | Kotlin language conventions, JVM interop          |
| rust               | Rust language conventions, safety, cargo          |
| swift              | Swift language conventions, Apple frameworks      |
| react-native       | React Native mobile development patterns          |
| sql-dba            | SQL conventions, schema design, query patterns    |
| devops             | CI/CD, containerization, infrastructure-as-code   |
| security           | Secure coding, dependency scanning, hardening     |
| clean-code         | Cross-language quality principles and practices   |
| api-design         | RESTful and GraphQL API design conventions        |
| microservices      | Microservices architecture and service mesh        |
| event-driven-messaging | Event-driven and messaging system patterns    |
| frontend-build-tooling | Frontend bundlers, build tools, monorepos     |
| kubernetes         | Container orchestration and cluster management    |
| terraform          | Infrastructure-as-code with Terraform             |
| aws-cloud-platform | AWS cloud services and architecture patterns      |
| azure-cloud-platform | Azure cloud services and architecture patterns  |
| gcp-cloud-platform | Google Cloud services and architecture patterns   |
| data-engineering   | Data pipelines, ETL, and data platform patterns   |
| business-intelligence | BI analytics, dashboards, and reporting        |
| mlops              | ML/AI operations, model lifecycle management      |
| change-management  | Organizational change and adoption practices      |
| customer-enablement | Customer onboarding and enablement programs      |
| finops             | Cloud financial operations and cost management    |
| product-strategy   | Product strategy, roadmapping, and prioritization |
| sales-engineering  | Pre-sales technical demonstrations and PoCs       |
| accessibility-compliance | ADA/WCAG accessibility standards             |
| gdpr-data-privacy  | GDPR data privacy compliance                     |
| hipaa-compliance   | HIPAA healthcare data compliance                  |
| iso-9000           | ISO 9000 quality management certification         |
| pci-dss-compliance | PCI-DSS payment card data security                |
| sox-compliance     | SOX financial compliance and audit controls       |

## Templates

Templates provide standardized starting points for common project artifacts.

**Per-persona templates** live in each persona's `templates/` directory and are specific to that role's outputs (e.g., `test-plan.md` for Tech-QA, `adr.md` for Architect). Each template includes a metadata table, placeholder fields, guidance text, and a Definition of Done checklist.

**Shared templates** in `templates/shared/` are cross-persona artifacts used by the whole team:

- `glossary.md` -- Project terminology and definitions
- `change-log.md` -- Chronological record of changes
- `meeting-notes.md` -- Structured meeting minutes
- `decision-record.md` -- Lightweight decision documentation
- `risk-log.md` -- Running log of identified risks
- `definition-of-done.md` -- Project-wide done criteria
- `evidence-attachments.md` -- Index of compliance evidence files

## Workflows

Workflow documents describe how the team operates as a coordinated unit.

- **foundry-pipeline.md** -- The end-to-end Foundry pipeline: Select, Compose, Compile, Scaffold, Seed, Export. Describes each stage's inputs, outputs, validation, and error handling.
- **task-taxonomy.md** -- A classification system mapping task categories to personas, lifecycle states, assignment rules, and cross-cutting concerns.

## Claude Integration

The `claude/` directory contains integration files for Claude Code:

- **commands/** -- Slash commands that can be invoked during a Claude Code session
- **skills/** -- Skill definitions that extend Claude's capabilities for the project
- **hooks/** -- Lifecycle hooks that run at defined points during Claude Code operations

## Contributing

To extend the library with new building blocks:

- **Add a persona:** Create a directory under `personas/` containing `persona.md`, `outputs.md`, `prompts.md`, and a `templates/` subdirectory with at least one template. Follow the structure and tone of existing personas.
- **Add expertise:** Create a directory under `expertise/` with `conventions.md` and any skill files. Name the directory after the domain (lowercase, hyphenated).
- **Add a shared template:** Place a new `.md` file in `templates/shared/`. Include a metadata table, placeholder fields, and a Definition of Done checklist.
- **Add a workflow:** Place a new `.md` document in `workflows/`. Use it as a reference document, not a template.

The Foundry library indexer discovers new items automatically based on directory structure and file naming conventions. No registration step is required.
