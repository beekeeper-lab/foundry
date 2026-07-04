# ADR-005: Declarative `Conflicts With` in Hook Pack Metadata

| Field | Value |
|-------|-------|
| **Date** | 2026-04-17 |
| **Status** | Accepted |
| **Bean** | BEAN-262 |
| **Deciders** | Architect |

## Context

External review (2026-04-17) found that `az-read-only` and `az-limited-ops` silently cancel each other when both are selected: the read-only guard blocks every mutating verb while the limited-ops guard is trying to permit deployment verbs. The generator today composes hook packs from whatever the user selects without checking whether any pair is contradictory. Result: a project that *appears* to allow deploys but actually blocks them at every `PreToolUse:Bash` hook — a silent misconfiguration that only surfaces when someone tries to deploy.

The same pattern applies to the AWS pair (`aws-read-only` ⇄ `aws-limited-ops`) and is latent in any future "strict vs. permissive" hook pair that may land in the library.

Two detection strategies were considered:

1. **Declare conflicts in hook pack metadata** — add a `## Conflicts With` section to each hook pack markdown file, parsed by the library indexer and enforced by the pre-generation validator.
2. **Hard-code pairs in `safety_writer.py`** — maintain a Python-side list of conflict pairs next to the existing `_HOOK_PACK_REGISTRY`.

## Decision

Declare conflicts in the hook pack markdown files (Option 1). Each hook pack that conflicts with another lists the conflicting pack id under a `## Conflicts With` section (one id per bullet). The library indexer parses this section into `HookPackInfo.conflicts_with: list[str]`. The pre-generation validator (`foundry_app/services/validator.py`) adds a `_check_hook_conflicts` check that emits a `hook-pack-conflict` **error** when a composition enables both sides of any declared conflict pair.

Conflict declarations are symmetric by convention — each side lists the other — but the validator treats any one-sided declaration as sufficient to flag the pair. This makes the detection robust to declaration drift.

## Consequences

**Positive:**
- Conflict declarations live alongside the behavior they describe (the hook pack markdown), so adding a new conflicting pair is a documentation change, not a Python change.
- The validator surfaces a blocking error with a clear message before any file is written, preventing silent misconfiguration at emit time.
- Extends naturally to future conflict pairs without schema churn.

**Negative:**
- Declaration drift is possible if only one side of a pair is updated. Mitigated by treating one-sided declarations as binding and by covering both sides in tests.
- Pair-level only — does not detect N-way conflict cliques. Acceptable for now; explicitly noted as out-of-scope in the bean.

## Alternatives Rejected

1. **Hard-code pairs in `safety_writer.py` (Option 2):** Keeps Python and markdown out of sync; adding a conflict requires a code change in a file that already holds the hook command strings, bloating an already long module. Rejected because the declaration belongs with the hook pack, not with the emitter.
2. **Runtime detection in the generated project** — have the hooks themselves detect overlap at `PreToolUse` time. Rejected: out of scope per the bean, and detection at generation time is both cheaper and more visible to the author.

