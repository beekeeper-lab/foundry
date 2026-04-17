# Starter Stacks — One Command Per Stack

Foundry scaffolds the AI-team context (`.claude/`, `ai/`, `CLAUDE.md`, team composition, starter bean). It does **not** scaffold stack-specific application code. That decision is recorded in [ADR-006](../ai/context/decisions.md).

Use this cheat sheet to initialize the app side of a newly generated project. Pick the row that matches your expertise selection, run the command at the project root, and commit the result. One line per stack — see the linked authoritative docs for anything deeper (options, templates, migration paths).

> **Where does this run?** In the root of a project Foundry just generated, alongside `CLAUDE.md`. None of these commands touch `ai/` or `.claude/`, so the AI team context is preserved.

## Language & Framework Stacks

| Expertise ID | Init Command | Authoritative Docs |
|---|---|---|
| `python` | `uv init` | <https://docs.astral.sh/uv/reference/cli/#uv-init> |
| `python-qt-pyside6` | `uv init && uv add PySide6` | <https://doc.qt.io/qtforpython-6/quickstart.html> |
| `node` | `npm init -y` | <https://docs.npmjs.com/cli/v10/commands/npm-init> |
| `typescript` | `npm init -y && npm install -D typescript && npx tsc --init` | <https://www.typescriptlang.org/docs/handbook/intro.html> |
| `react` | `npm create vite@latest -- --template react-ts` | <https://vite.dev/guide/> |
| `react-native` | `npx create-expo-app@latest` | <https://docs.expo.dev/get-started/create-a-project/> |
| `java` | `gradle init --type java-application` | <https://docs.gradle.org/current/samples/sample_building_java_applications.html> |
| `kotlin` | `gradle init --type kotlin-application` | <https://kotlinlang.org/docs/getting-started.html> |
| `dotnet` | `dotnet new console` | <https://learn.microsoft.com/en-us/dotnet/core/tutorials/with-dotnet-cli> |
| `swift` | `swift package init --type executable` | <https://www.swift.org/getting-started/cli-swiftpm/> |
| `rust` | `cargo new <name>` | <https://doc.rust-lang.org/cargo/getting-started/first-steps.html> |
| `go` | `go mod init <module-path>` | <https://go.dev/doc/tutorial/create-module> |

## Infrastructure & Tooling Stacks

These expertise packs produce configuration rather than a single scaffolded project. The canonical first command is shown for reference; each upstream has richer starter guides.

| Expertise ID | Init Command | Authoritative Docs |
|---|---|---|
| `terraform` | `terraform init` (after writing a `main.tf`) | <https://developer.hashicorp.com/terraform/tutorials/aws-get-started> |
| `kubernetes` | `kubectl create deployment <name> --image=<image> --dry-run=client -o yaml > deployment.yaml` | <https://kubernetes.io/docs/tutorials/kubernetes-basics/> |
| `devops` | `git init && git commit --allow-empty -m "init"` | <https://docs.github.com/en/actions/quickstart> |
| `frontend-build-tooling` | Covered by `react` / `node` / `typescript` above | — |
| `aws-cloud-platform` | `aws configure` (after installing the AWS CLI) | <https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html> |
| `azure-cloud-platform` | `az login` (after installing the Azure CLI) | <https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli> |
| `gcp-cloud-platform` | `gcloud init` (after installing the gcloud CLI) | <https://cloud.google.com/sdk/docs/install> |

## Non-Code Expertise

These packs ship conventions and checklists rather than code. There is no init command — they shape how the AI team writes docs, reviews, and audits. No action needed beyond selecting the expertise in your composition.

- `accessibility-compliance`, `api-design`, `business-intelligence`, `change-management`, `clean-code`, `customer-enablement`, `data-engineering`, `event-driven-messaging`, `finops`, `gdpr-data-privacy`, `hipaa-compliance`, `iso-9000`, `microservices`, `mlops`, `pci-dss-compliance`, `product-strategy`, `sales-engineering`, `security`, `sox-compliance`, `sql-dba`

## Why This Lives in the Foundry Repo (Not in Generated Projects)

This cheat sheet is a Foundry authoring reference — it names the commands *Foundry's users* run once per new project. Embedding it in every generated project would make the file go stale the moment any upstream generator renames a flag. Keeping it here lets us update the recipes without regenerating downstream projects. See [ADR-006](../ai/context/decisions.md) for the full reversibility argument.
