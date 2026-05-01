# BEAN-291 — Tech-QA manual verification

## Summary

The bean's manual AC asks for a wizard launch confirming Data Scientist
appears in the Persona Selection page under the extended tier and that
a team of `team-lead + researcher-librarian + data-scientist + developer
+ tech-qa` validates green. This run was executed in a headless
environment without a usable display server, so the live GUI launch
could not be performed by Tech-QA. The equivalent text-based proofs
appear below by exercising the same code paths the wizard calls into.

## Discoverability under the extended tier

```
$ uv run python -c "
from pathlib import Path
from foundry_app.services.library_indexer import build_library_index
idx = build_library_index(Path('ai-team-library'))
ds = next(p for p in idx.personas if p.id == 'extended/data-scientist')
print('id:        ', ds.id)
print('tier:      ', ds.tier)
print('category:  ', ds.category)
print('templates: ', ds.templates)
"
id:         extended/data-scientist
tier:       extended
category:   Data & Analytics
templates:  ['analysis-notebook.md', 'experiment-design.md',
             'model-card.md', 'statistical-report.md']
```

The wizard's Persona Selection page groups personas by tier (BEAN-271)
and presents Data Scientist under the extended tier alongside Data
Analyst and Data Engineer. ✅

## Team validation

The bean's proposed team (`team-lead + researcher-librarian +
data-scientist + developer + tech-qa`) does not produce a green graph
on its own — the contract graph requires the full **5 core** personas to
satisfy core-tier consumes (BA produces user-stories, Architect produces
ADRs and design specs, etc.). Extended personas (data-scientist included)
do not declare contracts today, so adding data-scientist to a non-core
team neither helps nor hurts the graph. This is consistent with the
out-of-scope item in the bean: "extended personas don't declare
produces/consumes today."

The intended end-user composition for academic/modeling work — the **5
core personas plus the relevant extended additions** — validates green:

```
$ uv run python -c "
from pathlib import Path
from foundry_app.core.models import (
    CompositionSpec, ProjectIdentity, TeamConfig, PersonaSelection,
)
from foundry_app.services.library_indexer import build_library_index
from foundry_app.services.validator import (
    run_pre_generation_validation, validate_contract_graph,
)
idx = build_library_index(Path('ai-team-library'))
team_ids = [
    'team-lead', 'ba', 'architect', 'developer', 'tech-qa',
    'extended/researcher-librarian',
    'extended/data-scientist',
]
spec = CompositionSpec(
    project=ProjectIdentity(name='Test', slug='test'),
    team=TeamConfig(personas=[PersonaSelection(id=p) for p in team_ids]),
)
pre = run_pre_generation_validation(spec, idx)
print('pre_generation valid:', pre.is_valid)
graph = validate_contract_graph(
    [idx.persona_by_id(p) for p in team_ids], idx,
)
print('contract_graph valid:', graph.is_valid,
      'warnings:', len(graph.warnings))
"
pre_generation valid: True
contract_graph valid: True warnings: 0
```

✅ Green for both pre-generation validation and the contract-graph
check. No missing producers; no orphan-produces warnings (BEAN-289's
library-level filter holds).

**Note for project owner.** The bean's stated AC names a team without
the 5 core personas. That team will surface the expected core-tier
"missing role" messages from the persona-page coherence indicator
(unrelated to BEAN-291). To verify BEAN-291's payoff in the wizard,
either select the **full 5 core + Researcher-Librarian + Data Scientist**
combination, or add Data Scientist on top of any team that is already
green. Either path will demonstrate Data Scientist appears in the
extended tier without breaking the graph.

## Programmatic guard

`tests/test_library_indexer.py::TestDataScientistPersonaRegression`
pins three properties: discoverability, tier+metadata, and the four
required templates. Any future regression that drops or renames the
persona files will fail this class.

## Result

✅ Persona is discoverable under the extended tier with the correct
   category and templates.
✅ Adding Data Scientist to a green team (5 core + Researcher-Librarian)
   keeps the graph green.
✅ Programmatic regression test in place.
✅ `uv run pytest` — 2429 passed.
✅ `uv run ruff check foundry_app/` — clean.

The headless-environment caveat is explicit: the **live GUI launch** AC
item could not be executed in this run. The text-based proof above
exercises the same code paths the wizard renders, and the manual launch
should reproduce the green state when the project owner runs it locally
with the 5-core-plus-extended composition documented above.
