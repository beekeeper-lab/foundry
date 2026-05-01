# Task 01 — BA: Canonical phrasing for validator messages

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-290 / 01 |
| **Owner** | ba |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-05-01 16:33 |
| **Completed** | 2026-05-01 16:35 |
| **Duration** | 2m |

## Goal

Produce a single reference document the Developer can read and translate
1:1 into validator code: every UI-surfaced message code gets one canonical
user-friendly replacement, the persona-page headline gets new copy, and
the artifact-id → human label table is fixed.

## Inputs

- `ai/beans/BEAN-290-user-friendly-validator-messages/bean.md` — full
  problem statement, observed examples, vocabulary blocklist, scope,
  acceptance criteria.
- `foundry_app/services/validator.py` — current message strings for the
  codes in scope (`missing-producer`, `orphan-produces`, `no-personas`,
  `no-expertise`, `duplicate-persona`, `duplicate-expertise`,
  `missing-persona`, `persona-no-persona-md`, `missing-expertise`,
  `expertise-no-files`, `missing-hook-pack`, `hook-pack-conflict`,
  `hook-pack-posture-incompatible`).
- `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` — current
  `_coherence_label` headline strings (around `_update_coherence_indicator`).
- `ai-team-library/contracts/artifact-types.yml` — source of truth for
  artifact identifiers and their long descriptions; mine the descriptions
  for the human-readable label or pick a short one.

## Acceptance Criteria

- [ ] Reference doc lives at
      `ai/outputs/ba/BEAN-290-validator-message-phrasing.md` and contains:
      - **Tone & shape** rules (one sentence preferred, lead with symptom,
        no internal jargon, name the actionable persona by display name).
      - **Vocabulary blocklist** — explicit "do NOT use" terms with the
        approved replacements.
      - **Per-code table** with one row per message code in the In Scope
        list. Each row: `code`, `current text` (verbatim), `proposed text`,
        and a one-line rationale. Use `{persona}`, `{type-label}`,
        `{consumers}`, `{producers}` etc. as placeholders so the Developer
        knows the variables.
      - **Persona-page headline copy** — one cleaned headline string for
        each of the three coherence states (red / amber / green) that the
        `_coherence_label` assembles in `_update_coherence_indicator`.
      - **Artifact-id → human label** table covering every artifact id
        referenced from in-scope messages (at minimum: `adr`, `user-story`,
        `design-spec`, `code-change`, `test-suite`, `bean-spec`). Prefer a
        label drawn from `artifact-types.yml` description; if the description
        is too long, give a short label and note "from description: …".
- [ ] No proposed text contains any of: `producer`, `consumer`, `orphan`,
      `node`, `graph`, `type '` — verified by reading the doc end-to-end.
- [ ] Each proposed text answers both questions stated in the bean Goal:
      *what is wrong* and *what can the user do*. If no action exists
      (library-data integrity errors), the text says so explicitly.
- [ ] The `hook-pack-posture-incompatible` proposed text does not contain
      the substrings `Posture Compatibility table` or `Included: No`.
- [ ] Banner-prefix decision is documented: the doc states what lead-in
      (if any) the generation-failure banner should use after the inner
      `"Validation failed:"` is dropped (e.g., `"Can't generate yet — "`
      or no prefix at all).

## Definition of Done

- Reference doc committed to `ai/outputs/ba/`.
- Cross-checked against bean.md acceptance criteria — every UI-surfaced
  code in scope has a row.
- Status updated to Done; the telemetry hook stamps Completed/Duration.
