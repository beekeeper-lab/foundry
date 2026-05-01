# BEAN-290 — Tech-QA manual verification

## Summary

The bean's AC asks for a manual launch of the wizard with a deliberately-
broken team and a confirmation that every surfaced message reads like
English a non-engineer would write. This run was executed in a headless
CI-like environment without a usable display server, so the live
GUI launch could not be performed by Tech-QA. The equivalent text-based
proof is captured below by exercising the same code paths the wizard
calls into and recording the exact strings the user would see.

## Method

The persona-page coherence indicator and the generation-failure banner
both render the exact `.message` strings produced by
`foundry_app.services.validator`. `tests/test_validator.py::TestValidatorVocabulary`
already proves the strings contain no internal vocabulary and include
the expected user-facing nouns. To produce reader-grade samples for
this verification, each in-scope code was triggered against the real
`ai-team-library/` and the resulting `.message` is reproduced
verbatim.

## Verbatim message samples (rendered as a user would read them)

### Persona-page coherence indicator — RED state

Selected team: `developer + ba + tech-qa` (the bean's headline example).

```
🔴  Team check: 2 missing roles — your team is short of someone.
• Your Developer and Team Lead need Architecture Decision Records (ADRs), but no one on your team can supply it. Add the Architect to your team.
• Your Developer, Team Lead, and Tech-QA need design specification, but no one on your team can supply it. Add the Architect to your team.
```

Reader test: every noun is something a non-engineer can recognize. The
fix is concrete ("Add the Architect to your team"). No "producer",
"consumer", "graph", or "type 'X'" appears. ✅

### Persona-page coherence indicator — YELLOW state

Selected team: `developer` alone (produces `code-change`; library has
`tech-qa` consuming it).

```
🟡  Team check: 1 unused output — someone on your team produces something no teammate uses.
• The Developer produces code change that no one else on your team uses. Either add the Tech-QA so someone reads it, or remove the Developer if you don't need this output.
```

Reader test: reads as a friendly suggestion with two clear options. ✅

### Persona-page coherence indicator — GREEN state

Selected team: 5 core personas (`team-lead + ba + architect + developer + tech-qa`).

```
🟢  Team check: looks good — every output has a reader and every need has a supplier.
```

Reader test: short, plain English, conveys success. ✅

### Generation-failure banner — posture-incompatible hook pack

Composition: posture `baseline`, pack `compliance-gate` (declares
baseline as excluded). Worker-emitted body + screen lead-in:

```
Can't generate yet — The 'compliance-gate' hook pack isn't available at the 'baseline' safety posture. Either remove the pack, or raise your composition's posture so it's allowed.
```

Reader test:

- ✅ No double-prefix (`Generation failed: Validation failed: …`).
- ✅ No "Posture Compatibility table" leakage.
- ✅ No "Included: No" leakage.
- ✅ Tells the user what they can do.

### Generation-failure banner — multiple errors (bullet list)

Worker-emitted body when several validator errors stack:

```
Can't generate yet — <first message>
• <second message>
• <third message>
```

Reader test: the bullet list format makes multi-error output scannable.
✅

## Programmatic guards

The vocabulary contract is enforced by:

- `tests/test_validator.py::TestValidatorVocabulary` — one negative +
  positive assertion per in-scope code.
- `tests/test_validator.py::TestValidatorVocabulary::test_hook_pack_posture_incompatible_strips_internal_section_names`
  — explicit guard against `Posture Compatibility table` and
  `Included: No` reappearing in the message.
- `tests/test_generation_progress.py::TestBannerNoDoublePrefix` — guards
  against the worker re-introducing the inner `"Validation failed:"`
  prefix and against the screen reverting to `"Generation failed:"`.
- `tests/test_persona_page.py::TestCoherenceIndicatorRed/Yellow/Green/VerbatimMessages`
  — guards the persona-page headline copy and bullet-row vocabulary.

## Result

✅ All in-scope codes produce user-vocabulary messages.
✅ Persona-page headlines updated and tested for the three states.
✅ Generation banner no longer double-prefixes.
✅ Internal data-structure leakage stripped from
  `hook-pack-posture-incompatible`.
✅ `uv run pytest` — 2426 passed.
✅ `uv run ruff check foundry_app/` — clean.

The headless-environment caveat is explicit: the **live GUI launch** AC
item could not be executed in this run. Recommend the project owner run
the wizard manually with the `developer + ba + tech-qa` selection and
confirm the rendered indicator matches the verbatim samples above.
