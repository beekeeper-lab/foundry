# Hook Posture Taxonomy

Foundry exposes three posture levels on `HooksConfig.posture`. This page documents what each one enables, so a reader of a composition YAML can predict the pack list without reading `safety_writer.py`.

Canonical mapping: `foundry_app.services.safety_writer.posture_base_packs(posture)`.
Decision record: `ai/context/decisions.md` ADR-006.
Stack-aware layering (how expertise + cloud add on top): `ai/context/hook-selection.md`.

## TL;DR

| Posture | Intent | Base packs | Base count | Default mode |
|---------|--------|------------|------------|--------------|
| `baseline` | Minimal guardrails. One branch-protection hook, no lint, no cloud. | `git-commit-branch` | 1 | `enforcing` |
| `hardened` | Sensible defaults for a team that wants branch + push hygiene + secret scanning. | `git-commit-branch`, `git-push-feature`, `security-scan` | 3 | `enforcing` |
| `regulated` | Compliance-adjacent. Adds a compliance gate and post-task QA on top of `hardened`. | `git-commit-branch`, `git-push-feature`, `security-scan`, `compliance-gate`, `post-task-qa` | 5 | `enforcing` |

Stack-aware layering (see `hook-selection.md`) adds at most one lint pack per mapped expertise and one cloud pack per cloud provider. Cloud hooks are added only at `hardened` and `regulated`.

## `baseline`

**Intent.** Every project gets the minimum guardrail: no edits on `main` / `master` / `test` / `prod`. No language-specific lint is required by the posture — stack-aware layering can still add a single lint pack if the expertise list maps to one.

**Base packs:**

- `git-commit-branch` — blocks `Edit` / `Write` / `NotebookEdit` on protected branches.

**Cloud:** none, regardless of declared cloud providers.
**Lint:** added only if the expertise list maps to one (e.g., Python → `pre-commit-lint`).

**Pick this when:** you want Foundry to stay out of the way. You want to be nudged off `main` but you'll handle lint, secrets, and cloud discipline elsewhere (IDE, CI, personal habit).

**Do not pick this when:** the project will touch secrets, production cloud accounts, or a compliance-reviewed codebase.

## `hardened`

**Intent.** Keep everything `baseline` does, then add branch-naming hygiene on feature branches and an in-editor secret scan. Adds cloud guardrails when a cloud provider is declared.

**Base packs (in addition to `baseline`):**

- `git-push-feature` — warns when the current branch doesn't match `(feature|fix|bean|hotfix|chore)/<name>`.
- `security-scan` — greps edits for obvious secret patterns (API keys, tokens).

**Cloud:** `aws-limited-ops` if `aws` is declared; `az-limited-ops` if `azure`. Both if both.
**Lint:** same as `baseline` — driven by the expertise list, not the posture.

**Pick this when:** working in a team repo with a branch-naming convention and you want casual protection against committing a secret.

**Do not pick this when:** you need evidence of compliance controls for a regulated audit — use `regulated` for that.

## `regulated`

**Intent.** Compliance-adjacent posture. Keeps everything `hardened` does, then adds a compliance gate that blocks sensitive ops and a post-task QA hook that runs after every tool invocation.

**Base packs (in addition to `hardened`):**

- `compliance-gate` — blocks destructive / regulated operations that require sign-off.
- `post-task-qa` — fires after every tool call; flags when a task completes without QA artifacts.

**Cloud:** same as `hardened`.
**Lint:** same as `baseline` / `hardened` — expertise-driven.

**Pick this when:** the project is subject to a compliance regime (HIPAA, PCI-DSS, SOX, GDPR) or the codebase produces evidence for an audit.

**Do not pick this when:** the friction from `post-task-qa` and `compliance-gate` will outweigh the assurance value — for example, internal tooling that is never audited.

## Why three levels and not two or four

`baseline` is the floor — one branch protection. `hardened` adds the defaults most teams actually want. `regulated` adds the compliance controls you only want when you need them. A fourth level would either duplicate `hardened` or pre-empt a future per-pack configuration feature. A two-level collapse would lose the distinction between "default team hygiene" and "audit-track compliance."

## Overriding the defaults

The posture sets **defaults**. An explicit `hooks.packs` list on the composition spec overrides stack-aware layering entirely — Foundry uses the user's list as-is (minus disabled packs) and warns when a listed pack doesn't match the declared stack. See `hook-selection.md` for the full resolution order.

## Testing

`tests/test_safety_writer.py::TestPostureTaxonomy` asserts the base pack list for each posture matches this page. If you change `_POSTURE_BASE`, update this doc and that test together.
