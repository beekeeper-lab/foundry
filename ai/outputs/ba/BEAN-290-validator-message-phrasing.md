# BEAN-290 — Canonical phrasing for validator messages

This document is the **single source of truth** for the user-facing text
of every validator message in scope for BEAN-290. The Developer reads
this and rewrites `foundry_app/services/validator.py` and the
persona-page coherence-indicator headline 1:1 from the rows below.

Codes and severities are unchanged. Only `.message` text changes.

---

## 1. Tone & shape

| Rule | Why |
|------|-----|
| One sentence preferred; two if the fix needs detail. | Long error text gets ignored. |
| Lead with the symptom (what is wrong), follow with the fix (what to do). | The user is trying to *act*, not read a glossary. |
| Speak to the user (`your team`, `you'll need`), not about them. | The wizard is a conversation, not a status board. |
| Name personas by their **title-cased id** (`Developer`, `Team Lead`, `Tech-QA`). | `PersonaInfo` does not carry a separate display name — title-casing the id is the closest thing today. Helper: `_title_case_persona_id("team-lead") → "Team Lead"`, `tech-qa` stays hyphenated as `"Tech-QA"`. |
| Name artifacts by their human label from §4 — never the slug. | The slug (`adr`, `design-spec`) is internal vocabulary the user has never seen. |
| If no action is available (library-data integrity error), say so explicitly and tell the user this is a library bug, not their composition. | The user can't fix `expertise-no-files` by changing their team — they need to know that. |

## 2. Vocabulary blocklist

The following terms **must not appear** in any user-facing `.message`
or in the persona-page coherence-indicator headline:

- `producer`, `producers`
- `consumer`, `consumers`
- `orphan`, `orphan-produces`
- `node`, `graph`
- `type 'X'` (the literal pattern with quoted slug)

Allowed neutral substitutes:

| Avoid | Use |
|-------|-----|
| "missing producer" | "no one on your team can supply ___" / "a missing role" |
| "consumed by" | "needs ___" / "your ___ are waiting on" |
| "orphan produces" | "outputs no one is using" / "produces ___ that no one reads" |
| "type 'adr'" | "Architecture Decision Records (ADRs)" (see §4) |

## 3. Persona-page headline copy

`persona_page._update_coherence_indicator` assembles a headline from
one of three states. Replace the existing strings with these:

| State | New headline |
|-------|--------------|
| 🔴 errors > 0 | `f"\U0001f534  Team check: {error_count} missing role{'s' if error_count != 1 else ''} — your team is short of someone."` |
| 🟡 warnings > 0 | `f"\U0001f7e1  Team check: {warning_count} unused output{'s' if warning_count != 1 else ''} — someone on your team produces something no teammate uses."` |
| 🟢 clean | `"\U0001f7e2  Team check: looks good — every output has a reader and every need has a supplier."` |

Notes for the Developer:
- Keep the `{error_count}` / `{warning_count}` interpolation pattern.
- Drop the trailing `"— add producers or remove consumers."` clause
  entirely; the bullet rows below already tell the user what to do.

## 4. Artifact-id → human label

Source: `ai-team-library/contracts/artifact-types.yml`. The
`ArtifactTypeInfo.description` field is sentence-length, so we keep a
small overrides map next to the validator (or in a new
`foundry_app/services/artifact_labels.py`). Lookup order at call time:

1. Overrides table (this section).
2. Fallback: title-case the slug (`code-change` → `"code change"`).

The Developer chooses the placement; either is acceptable.

| Artifact id | Human label |
|-------------|-------------|
| `bean-spec` | `bean specification` |
| `task-spec` | `task specification` |
| `user-story` | `user stories` |
| `acceptance-criteria` | `acceptance criteria` |
| `scope-definition` | `scope definition` |
| `risk-register` | `risk register` |
| `adr` | `Architecture Decision Records (ADRs)` |
| `design-spec` | `design specification` |
| `dev-decision` | `development-decision note` |
| `code-change` | `code change` |
| `test-suite` | `test suite` |
| `traceability-matrix` | `traceability matrix` |
| `vdd-report` | `verification report` |
| `merge-summary` | `merge summary` |

`handoff-packet` is never surfaced (it lives in
`_CONTRACT_GRAPH_IGNORED_TYPES`).

## 5. Per-code message rewrites

Variable conventions used below:

- `{persona}` — title-cased persona id (e.g., `"Software Architect"`
  if a display name existed; today `"Architect"`).
- `{persona_list}` — comma-separated list of title-cased persona ids
  joined with Oxford-comma rules where natural; for two items use
  `"X and Y"`, for three+ use `"X, Y, and Z"`. A small
  `_join_personas()` helper is fine.
- `{type_label}` — the human label from §4.
- `{producer_options}` — comma-separated list of suggested persona
  display names (from the library) the user can add.

### 5.1 ERROR codes

| Code | Current text | Proposed text | Rationale |
|------|--------------|---------------|-----------|
| `missing-persona` | `format_unknown_persona_error(ps.id, library_index)` | **Keep** — already user-friendly per ADR-014. Verify by reading the helper; if it leaks `producer`/`type`, file a follow-up. | Not in our scope per AC; the helper is the canonical message. |
| `missing-expertise` | `f"Expertise '{ss.id}' not found in library"` | `f"The '{ss.id}' expertise pack isn't in the library — check the spelling, or remove it from your selection."` | Tells the user what to do. |
| `missing-hook-pack` | `f"Hook pack '{hp.id}' not found in library"` | `f"The '{hp.id}' hook pack isn't in the library — check the spelling, or remove it from your selection."` | Symmetrical to `missing-expertise`. |
| `hook-pack-conflict` | `f"Hook packs '{a}' and '{b}' are mutually exclusive and cannot both be enabled in the same composition. Remove one of them."` | `f"The '{a}' and '{b}' hook packs can't be used together — pick one and remove the other."` | Drops "mutually exclusive" jargon. |
| `hook-pack-posture-incompatible` | `f"Hook pack '{hp.id}' declares posture '{posture_key}' as incompatible (Posture Compatibility table says Included: No). Remove the pack, lower enforcement, or raise the composition's posture."` | `f"The '{hp.id}' hook pack isn't available at the '{posture_key}' safety posture. Either remove the pack, or raise your composition's posture so it's allowed."` | **Drops the parenthetical** referencing the internal Posture Compatibility table. The Developer should keep that detail in a `logger.info(...)` line for debugging. |
| `missing-producer` | `f"Missing producer for type '{artifact}'. Consumed by: {consumer_list}. Producers in library: {producer_list}. Add one to your team."` | `f"Your {team_consumers_label} need {type_label}, but no one on your team can supply it. Add {producer_options_label} to your team."` Where `team_consumers_label` is the joined consumer display names ("`Developer and Team Lead`") and `producer_options_label` joins the library suggestions ("`the Architect`" or "`the Architect or the BA`"). When library has none, use: `f"Your {team_consumers_label} need {type_label}, but no persona in the library can supply it — this is a library gap, not a team-composition issue."` | Names the affected team members in plain English; names the actionable persona by display name; gives a concrete *what to do*. Handles the no-library-producer edge case explicitly. |
| `duplicate-persona` | `f"Persona '{pid}' is selected more than once"` (note: WARNING in code, listed under ERROR header in bean — preserve current severity) | `f"You've added the {pid_titlecased} more than once — extra copies have no effect, you can remove the duplicates."` | Tells the user the duplicate is harmless and what to do. |
| `duplicate-expertise` | `f"Expertise '{sid}' is selected more than once"` | `f"You've added the '{sid}' expertise pack more than once — extra copies have no effect, you can remove the duplicates."` | Symmetrical to `duplicate-persona`. |

### 5.2 WARNING codes

| Code | Current text | Proposed text | Rationale |
|------|--------------|---------------|-----------|
| `persona-no-persona-md` | `f"Persona '{ps.id}' has no persona.md file"` | `f"The {pid_titlecased} persona is in the library but its profile file (persona.md) is missing — this is a library-data issue, not your composition. Generation will continue but the agent file will be sparse."` | Library-data integrity errors must explicitly tell the user "not your fault" so they don't try to fix it from the wizard. |
| `expertise-no-files` | `f"Expertise '{ss.id}' has no convention files"` | `f"The '{ss.id}' expertise pack is in the library but has no convention files — this is a library-data issue, not your composition. Generation will continue but the expertise will contribute nothing."` | Symmetrical to `persona-no-persona-md`. |
| `no-personas` | `"No personas selected — the generated project will have no team"` | `"You haven't selected any team members yet. Pick at least one persona on the Persona Selection page so the generated project has a team."` | Names the page they need to act on. |
| `no-expertise` | `"No expertise selected — no convention files will be included"` | `"You haven't selected any expertise packs. The generated project will work, but it won't carry any technology-specific conventions. If that's intentional, you can ignore this."` | Tells the user it's OK if intentional. |
| `orphan-produces` | `f"Persona '{producer_id}' produces type '{artifact}' but no persona on the team consumes it."` | `f"The {producer_pid_titlecased} produces {type_label} that no one else on your team uses. Either add {consumer_options_label} so someone reads it, or remove the {producer_pid_titlecased} if you don't need this output."` Where `consumer_options_label` joins the title-cased ids of library personas that consume this artifact ("`the Tech-QA`" or "`the Tech-QA or the BA`"). | Names the suggested fix-direction persona (currently dropped from the message). The validator already computes `library_consumers` for the suppression check (see `validate_contract_graph`); reuse that data to populate this. |

## 6. Generation-failure banner copy

Two sites participate in the banner:

- `foundry_app/ui/generation_worker.py:49` — currently emits
  `f"Validation failed: {errors}"`. **Drop** the inner `"Validation failed: "`
  prefix. Pass the joined errors through verbatim.
- `foundry_app/ui/screens/generation_progress.py:502` — wraps with
  `f"Generation failed: {message}"`. **Replace** with
  `f"Can't generate yet — {message}"`. The new lead-in is friendlier, is
  not redundant with the validator-message wording, and tells the user
  the situation is recoverable (they can fix and retry).

Joined errors: when multiple validator errors fire, today they are
likely string-joined into one `errors` value. If the join character is
a comma, switch it to `"\n• "` (a bullet on a new line), so the banner
reads as a list. Final banner shape:

```
Can't generate yet — <first message>
• <second message>
• <third message>
```

If the `errors` value is a list at the call site, build the lead-in
plus bullet list there. If it is already a single string, the
Developer can split-and-rejoin or leave the joining as-is and revisit
in a follow-up bean.

## 7. Test-vocabulary contract for Tech-QA

Tech-QA uses the negative-assertion pattern:

```python
BLOCKLIST = ("producer", "consumer", "orphan", "node", "graph", "type '")

for msg in surfaced_messages:
    for term in BLOCKLIST:
        assert term not in msg.message.lower(), (
            f"Internal vocabulary leaked into {msg.code}: {msg.message!r}"
        )
```

Plus, for each in-scope code, at least one positive assertion that the
expected human label or persona display name appears in the message.

---

**Open question for follow-up (out of scope here):** the
`ArtifactTypeInfo` registry could carry a short `display_label` field
so the overrides map in §4 isn't needed. File a backlog bean if the
Developer agrees during implementation; the override map is fine for
now.
