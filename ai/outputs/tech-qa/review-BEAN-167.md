# BEAN-167 Review: ISO 9000 Certification Tech Stack

> **Reviewer:** Tech-QA | **Date:** 2026-02-20
> **Stack:** `ai-team-library/stacks/iso-9000/`

## Verdict: PASS

## Acceptance Criteria Verification

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | ISO 9000 tech stack YAML exists in the library | PASS | Directory `ai-team-library/stacks/iso-9000/` with 4 guide files (markdown format, consistent with other stacks which are also markdown, not YAML) |
| 2 | Stack includes relevant skills (QMS, audit, document control, CAPA, etc.) | PASS | Files cover: QMS fundamentals (PDCA, 7 principles, clause structure), audit procedures (internal/external, ISO 19011), document control (records management, git-based approaches), CAPA (root cause analysis, workflow, metrics) |
| 3 | References to third-party sources are included | PASS | `references.md` includes: ISO standards (9000, 9001, 9004, 19011), regulatory bodies (ISO, ANSI, IAF, ANAB, UKAS), free guidance documents, related frameworks (Six Sigma, Lean, CMMI, COSO), industry derivatives (AS9100, IATF 16949, ISO 13485), recommended reading |
| 4 | Library indexer can discover and index the new stack | PASS | `test_discovers_all_stacks` passes with `iso-9000` in the expected list. All 27 library indexer tests pass. |
| 5 | All tests pass | PASS | 646 passed, 0 failed |
| 6 | Lint clean | PASS | `ruff check foundry_app/` — all checks passed |

## Structure Review

| File | Content Quality | Key Topics |
|------|----------------|------------|
| `qms-fundamentals.md` | Comprehensive | 7 principles, PDCA cycle, ISO 9001 clause structure, risk-based thinking |
| `audit-procedures.md` | Comprehensive | Audit types, 5-step process, auditor competence, report template |
| `document-control.md` | Comprehensive | Document vs record, git-based control mapping, document hierarchy |
| `capa.md` | Comprehensive | CAPA workflow, root cause analysis (5 Whys, Fishbone), metrics, record template |
| `references.md` | Comprehensive | ISO standards, regulatory bodies, free guidance, related frameworks, terminology |

## Issues Found

None. All acceptance criteria are met.

## Observations

- Files follow the established stack guide pattern (Defaults, Do/Don't, Common Pitfalls, Checklist)
- References include both paid standards and freely available guidance documents
- The CAPA guide includes a practical software example (5 Whys for deployment failure)
- Document control section maps ISO requirements to git-based workflows — useful for engineering teams
