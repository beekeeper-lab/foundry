# Hook Selection Mapping

This document defines how Foundry selects hook packs for a generated project
based on the **posture**, **expertise**, and **cloud providers** chosen in the
composition spec. The logic lives in `foundry_app/services/safety_writer.py`.

## Why stack-aware selection

Prior to BEAN-255, hook selection was either:

- **Posture-driven:** a fixed list of packs keyed on `baseline` / `hardened` /
  `regulated`, independent of the stack.
- **User-composed:** explicit packs in `hooks.packs` on the spec.

The posture defaults hard-coded `pre-commit-lint` (ruff) for every project and
ignored cloud selection entirely. Result: a React/TypeScript project got
Python lint hooks; an AWS-only project got no cloud guardrails while any
project that enabled Azure hooks manually got them regardless of its stack.

Stack-aware selection closes that gap by resolving defaults from three
signals — posture, expertise, cloud providers — so hooks line up with the
tech the project actually uses.

## Resolution order

1. If `hooks.packs` is non-empty on the spec, use that explicit selection
   (minus disabled packs). Stack-aware defaults are **not** applied on top.
   Packs that mismatch the stack produce a **warning** but are kept —
   backward compatibility.
2. Otherwise, build the default set from:
   - **Posture base** — the non-stack, non-cloud hooks for the chosen posture
     (branch guards, security scan, compliance gate, post-task-qa).
   - **Expertise layer** — adds lint/test/type-check hooks keyed on the
     primary stack (see table below).
   - **Cloud layer** — adds cloud-specific hooks keyed on selected providers.

## Posture base

| Posture | Always-on packs |
|---------|-----------------|
| `baseline` | `git-commit-branch` |
| `hardened` | `git-commit-branch`, `git-push-feature`, `security-scan` |
| `regulated` | `git-commit-branch`, `git-push-feature`, `security-scan`, `compliance-gate`, `post-task-qa` |

These are stack-independent — they gate git and secrets regardless of
language or cloud.

## Expertise → lint/type-check hooks

The expertise list is scanned in order; the **first** match wins. Matching is
by expertise id. An expertise id not listed below contributes no lint hook.

| Expertise id(s) | Pack added | Rationale |
|-----------------|------------|-----------|
| `python`, `python-qt-pyside6` | `pre-commit-lint` (ruff) | Python lint/format |
| `react`, `typescript`, `node`, `react-native`, `frontend-build-tooling` | `pre-commit-lint-js` (ESLint + Prettier + `tsc --noEmit`) | JS/TS lint + type-check |
| `go` | `pre-commit-lint-go` (`gofmt -l`, `go vet`) | Go lint/format |
| `rust` | `pre-commit-lint-rust` (`cargo fmt --check`, `cargo clippy`) | Rust lint/format |
| anything else | (none) | Silent — no lint hook added |

If multiple language expertises are selected (e.g., `python` + `typescript`),
**both** lint packs are added. The "first match wins" rule applies only when
two expertises map to the **same** pack.

## Cloud provider → cloud hooks

| Provider | Default pack added at `baseline` | Default pack added at `hardened`/`regulated` |
|----------|----------------------------------|-----------------------------------------------|
| `azure` | (none) | `az-limited-ops` |
| `aws` | (none) | `aws-limited-ops` |
| `gcp` | (none) | `gcp-limited-ops` *(reserved — not yet implemented)* |
| `self-hosted` | (none) | (none) |

Rationale: at `baseline` we don't guardrail cloud CLIs at all. At `hardened`
and `regulated` we block destructive operations for **each** provider the
project targets. An Azure hook is never added to an AWS-only project.

When no cloud providers are selected, no cloud hooks are added — regardless
of posture.

## Backward-compatibility / warnings

When a user's explicit `hooks.packs` selection includes a pack that doesn't
match the stack (e.g., `pre-commit-lint` on a TypeScript-only project, or an
Azure hook with no `azure` cloud provider), `safety_writer` emits a warning
on the `StageResult` but still writes the requested pack. This preserves the
power-user escape hatch — maybe a Python tooling script lives alongside a TS
app — while surfacing the likely mismatch.

Warnings are **never** emitted for packs selected automatically by the
stack-aware defaults.

## Registry entries

New packs added for stack-aware selection live in the same `_HOOK_PACK_REGISTRY`
in `safety_writer.py` as the existing packs. Library documentation for each
lives in `ai-team-library/claude/hooks/<pack-id>.md`.

| Pack id | Library doc | Purpose |
|---------|-------------|---------|
| `pre-commit-lint-js` | `pre-commit-lint-js.md` | ESLint + Prettier + `tsc --noEmit` on JS/TS edits |
| `aws-read-only` | `aws-read-only.md` | Block `aws` CLI write verbs |
| `aws-limited-ops` | `aws-limited-ops.md` | Block destructive `aws` verbs (`delete`, `destroy`) |

## Test coverage

`tests/test_safety_writer.py` covers:

- A `python` + `clean-code` composition at `baseline` yields `ruff` lint
  hooks and **no** ESLint/Prettier/tsc hook.
- A `react` + `typescript` composition at `baseline` yields ESLint/Prettier/tsc
  hooks and **no** `ruff` hook.
- An `aws`-only project at `hardened` yields the AWS cloud hook and no
  Azure hook. Conversely for `azure`-only.
- An empty `cloud_providers` list yields no cloud hooks at any posture.
- Explicit `pre-commit-lint` on a TypeScript project produces a warning but
  still emits the ruff hook.
