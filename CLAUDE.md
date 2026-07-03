# Foundry

Foundry is a PySide6 desktop application and Python service layer that generates Claude Code project folders from reusable building blocks. Version 1.0.0.

## Repository Structure

```
foundry_app/          # Application source (core/, services/, ui/, io/)
tests/                # pytest test suite (1811 tests)
ai-team-library/      # Reusable library: personas, expertise, templates, workflows
ai/                   # AI team workspace (context, outputs, beans, tasks)
.claude/              # Claude Code config — git submodule from beekeeper-lab/claude-kit
examples/             # Example composition YAMLs
```

## AI Team

| Persona | Role | Agent | Output Directory |
|---------|------|-------|------------------|
| Team Lead | Coordinates work, decomposes beans, assigns tasks | `.claude/agents/team-lead.md` | `ai/outputs/team-lead/` |
| BA | Requirements, user stories, acceptance criteria | `.claude/agents/ba.md` | `ai/outputs/ba/` |
| Architect | System design, ADRs, module boundaries | `.claude/agents/architect.md` | `ai/outputs/architect/` |
| Developer | Implementation, refactoring, code changes | `.claude/agents/developer.md` | `ai/outputs/developer/` |
| Tech QA | Test plans, test implementation, quality gates | `.claude/agents/tech-qa.md` | `ai/outputs/tech-qa/` |

## Beans Workflow

A **Bean** is a unit of work (feature, enhancement, bug fix, or epic). Beans live in `ai/beans/BEAN-NNN-<slug>/`.

**Lifecycle:** Unapproved → Approved → In Progress → Done

1. Create a bean from `ai/beans/_bean-template.md` (status: `Unapproved`)
2. User reviews and approves beans (status: `Approved`)
3. Team Lead picks approved beans from the backlog (`ai/beans/_index.md`)
4. Team Lead decomposes into tasks. Default wave: Developer → Tech-QA. BA and Architect are opt-in when criteria are met. Tech-QA is mandatory for every bean.
5. Team Lead dispatches each task with `/spawn-task` (preferred per-task dispatch — supervisor pattern, ADR-008). Each task's `Inputs:` is enforced at dispatch by `validate-task-inputs.py` (BEAN-272).
6. Each persona produces typed artifacts per its `contracts.yml` (BEAN-273) and hands off to the next persona via `/handoff` (typed packets, BEAN-276).
7. Before merge, `/vdd <bean-id>` runs the programmatic VDD gate (BEAN-277); `/merge-bean` refuses to merge without a passing report.
8. Bean marked Done; per-bean Orchestration Telemetry rolls up via `/orchestration-report` (BEAN-278).

See `ai/context/bean-workflow.md` for the full lifecycle specification and `ai/context/orchestration-architecture.md` for the orchestration model (supervisor pattern, context engineering, specialist contracts, architecture-aware evaluation).

## Tech Stack

- **Python** >=3.11 (running 3.14.2), **PySide6**, **Pydantic**, **Jinja2**, **PyYAML**
- **Build:** `hatchling` (note: `packages = ["foundry_app"]` because package name != project name)
- **Deps:** `uv` for dependency management
- **Lint:** `ruff` (line-length 100, target py311, select E/F/I/W)
- **Tests:** `pytest` (testpaths = tests/)

## Key Commands

```bash
uv run pytest                          # Run all tests
uv run pytest tests/test_foo.py -v     # Run one test file
uv run ruff check foundry_app/         # Lint check
uv run ruff check foundry_app/ --fix   # Lint auto-fix
uv run foundry                         # Launch GUI
uv run foundry-cli generate <yml> --library ai-team-library  # CLI generation
/bg <command> [args...]                # Run any slash command in a background tmux window
```

@.claude/shared/CLAUDE.md

## Media Skills

Foundry distributes two plan-driven media generators to projects that opt in (`generation.include_media_skills: true` in `composition.yml`). Both live in the kit (`.claude/shared/skills/`) and reach generated projects via subtree mode or the asset_copier kit-distribution path (see ADR-009).

| Skill | Plan file | Purpose |
|---|---|---|
| `generate-image` | `IMAGE-PLAN.md` | Routes Gemini (Nanobanana) or OpenAI (gpt-image) per `**Generator:**` frontmatter; unified `--quality low/medium/high`; sidecar JSON per asset. See `.claude/shared/skills/generate-image/SKILL.md` and ADR-010. |
| `generate-audio` | `NARRATION-PLAN.md` + inline `> 🎙️` blocks in source markdown | ElevenLabs MP3 narration; per-source manifest with stripped-text invariant for content-hash dedup. See `.claude/shared/skills/generate-audio/SKILL.md` and ADR-011. |

### Required environment variables

| Variable | Required for | Notes |
|---|---|---|
| `GEMINI_API_KEY` | Default `generate-image` routing | |
| `OPENAI_API_KEY` | `generate-image` when `**Generator:**` resolves to OpenAI | |
| `ELEVENLABS_API_KEY` | All `generate-audio` runs (skipped under `--dry-run`) | |

Both skills discover `.env` via `_media_lib.env.load_env`, which walks **cwd → parents → `$HOME`** and loads the first `.env` found. Existing process environment values always win, so a CI secret or shell export beats a stale checked-in `.env`. See `.env.example` at the repo root for the template.

### Cost discipline

ElevenLabs is **1 credit per character** (`eleven_multilingual_v2`); every audio run prints `chars sent = credits` so the user can pace work against the monthly cap. Image cost rates live in `_COST_TABLE` at the top of `generate_image.py` (the source of truth — do not duplicate the table in docs).

## Claude Kit Submodule

```bash
# First clone / fresh checkout
git submodule update --init --recursive
scripts/claude-sync.sh

# Pull latest kit changes
scripts/claude-sync.sh

# Edit shared assets inside .claude/shared/, then push both repos
scripts/claude-publish.sh
```

## Rules

- **Do not modify** files in `ai-team-library/` — that is the shared library
- **All AI outputs** go to `ai/outputs/<persona>/`
- **Run tests** before marking any task done (`uv run pytest`)
- **Run ruff** before committing (`uv run ruff check foundry_app/`)
- **Bean tasks** live in `ai/beans/BEAN-NNN-<slug>/tasks/`
- **ADRs** go in `ai/context/decisions/ADR-NNN-<slug>.md` (register in the `ai/context/decisions.md` index)
