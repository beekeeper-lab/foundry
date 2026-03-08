# Skill Specification: `generate-screen` (v1)

## Overview

A shared Claude Code skill for generating responsive UI screens/pages from diverse inputs. This is a **higher-level orchestration skill** — Claude itself is the engine for analysis, planning, and code generation. No Python script backend; the skill is entirely instruction-driven via SKILL.md.

Can be:
- Invoked directly via `/generate-screen`
- Called by other skills
- Shared across projects via the claude-kit submodule

---

## Architecture

Unlike `generate-image` (which wraps a Python script calling an external API), this skill has no external API — Claude does the work directly using its native capabilities: reading code, analyzing structure, reasoning about layout, and generating implementation.

```
/generate-screen command
  -> SKILL.md (structured workflow for Claude)
    -> Phase 1: Ingest & normalize context
    -> Phase 2: Inspect repo for existing patterns
    -> Phase 3: Plan screen (field grouping, layout, responsiveness)
    -> Phase 4: Generate code into project source tree
    -> Phase 5: Generate assets via generate-image (if needed)
    -> Phase 6: Write screen manifest
```

---

## File Layout

### Skill files (in claude-kit submodule)

```
.claude/shared/
  skills/
    generate-screen/
      SKILL.md
  commands/
    generate-screen.md
```

Minimal footprint: one SKILL.md, one command file. No scripts, templates, or examples.

### Output files

**Generated code** lands in the **project's actual source tree** — wherever pages/screens live in that project (e.g., `src/pages/`, `foundry_app/ui/screens/`, `lib/screens/`). The skill determines the correct location by inspecting existing project structure.

**Screen manifest** is saved alongside the generated code:

```
<project-source-dir>/
  <screen-name>/
    SCREEN-MANIFEST.md        # plan, assumptions, decisions
    <implementation files>     # .tsx, .py, .dart, etc.
```

---

## Platform Detection

### Auto-detection (default)

The skill inspects the repo to determine the target platform:

| Signal | Detected Platform |
|--------|-------------------|
| `package.json` with `react` dependency | `react` |
| `package.json` with `next` | `react` (Next.js) |
| `pyproject.toml` with `PySide6` | `pyside6` |
| `pyproject.toml` with `tkinter` usage | `tkinter` |
| `pubspec.yaml` with `flutter` | `flutter` |
| `tailwind.config.*` present | `react` + Tailwind |
| `src/theme.ts` or `theme.js` | Note theme system for reuse |

### When auto-detection fails

If no platform can be detected (empty repo, new project), the skill **must ask the user** rather than guess. Prompt:

```
I couldn't detect a UI framework in this project. Which platform should I target?
- react (with optional framework: tailwind, mui, shadcn)
- pyside6
- flutter
```

### Explicit override

`--platform` always overrides auto-detection. Optional `--framework` refines it (e.g., `--platform react --framework tailwind`).

---

## Inputs

The skill accepts multiple forms of context, mixed freely.

### From the command line

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| (positional) | Yes | — | Freeform description of the screen to build |
| `--platform` | No | auto-detect | `react`, `pyside6`, `tkinter`, `flutter` |
| `--framework` | No | — | Framework refinement (e.g., `tailwind`, `mui`, `shadcn`, `material`) |
| `--mode` | No | `full-screen` | `plan-only`, `full-screen`, `full-screen-plus-assets` |
| `--with-tests` | No | false | Generate tests alongside the screen |
| `--screen-name` | No | inferred from prompt | Name for the screen/page |
| `--style-ref` | No | — | Repeatable. Path to reference image, screenshot, or code file |
| `--fields` | No | — | Path to CSV or JSON field definitions |
| `--mermaid` | No | — | Path to Mermaid diagram file (.mmd) |
| `--reuse` | No | `prefer-existing` | `strict`, `prefer-existing`, `mixed` |
| `--responsive` | No | `balanced` | `desktop-first`, `mobile-first`, `balanced` |
| `--image-policy` | No | `only-if-needed` | `none`, `only-if-needed`, `aggressive` |
| `--density` | No | `comfortable` | `compact`, `comfortable`, `spacious` |
| `--output-dir` | No | auto-detect | Override where generated files land |

### Context types

1. **Freeform text** — the primary prompt describing what to build
2. **CSV/JSON field definitions** — field name, label, type, required, validation, grouping hints
3. **Mermaid diagrams** — ERDs, flows, state diagrams used as structural context
4. **Style references** — screenshots, images, or existing code files for visual direction
5. **Existing application context** — auto-discovered from the repo (theme files, components, tokens, patterns)

---

## Workflow

### Phase 1: Ingest & Normalize

1. Parse the user's prompt and any CLI arguments
2. If `--fields` provided, read and parse CSV/JSON field definitions
3. If `--mermaid` provided, read Mermaid source as structural context
4. If `--style-ref` provided, read/analyze each reference (images via vision, code files via Read)
5. Validate all referenced files exist; fail clearly if any are missing

### Phase 2: Repo Inspection

Inspect the repository for existing patterns. This is critical for consistency.

**Discover:**
- Project structure and file/folder conventions
- Existing pages/screens (to follow the same patterns)
- Shared components (form controls, cards, tables, modals, tabs, layout primitives)
- Theme files, design tokens, CSS variables
- Validation patterns and utilities
- Typography and spacing systems
- Icon libraries in use
- Routing/navigation patterns
- Naming conventions

**Goal:** Build an inventory of what exists before creating anything new.

### Phase 3: Screen Planning

Before writing any code, produce a screen plan. This is the most important phase.

**Determine:**

1. **Page purpose** — what is this screen for, what are the primary user tasks
2. **Field grouping** — semantically group related fields even if the source data is flat
3. **Information hierarchy** — what's prominent, what's secondary, what's above the fold
4. **Layout regions** — header, main content, sidebar, footer, summary strips
5. **Component mapping** — which existing components to reuse, what new ones to create
6. **Interaction model** — read-only vs editable, inline vs modal editing, CTAs
7. **Responsive strategy** — how each region adapts across desktop/tablet/mobile
8. **Image needs** — does this screen need generated visual assets
9. **Assumptions** — document every inference made

**Field grouping intelligence:**

The skill must infer logical groups even from flat field lists:
- `first_name`, `last_name`, `middle_name` -> Personal Information
- `street`, `city`, `state`, `zip`, `country` -> Address
- `phone`, `email`, `contact_preference` -> Contact Information
- `created_at`, `updated_at`, `created_by` -> Audit / Metadata (read-only, secondary)
- `balance`, `rate`, `total` -> Financial Summary

**Component inference:**

Map data characteristics to UI components:
- Short text -> text input
- Bounded options -> select/dropdown
- Boolean -> toggle or checkbox
- Long text -> textarea
- Date -> date picker
- List of records -> table, card list, or accordion
- Summary metrics -> stat cards or summary strip
- Multi-step workflow -> stepper/wizard

### Phase 4: Code Generation

Map the screen plan into the detected/selected platform.

**Code lands in the project's source tree** — determine the correct location by inspecting where existing pages/screens live.

**Style precedence (strict order):**
1. Existing application components and styles
2. Existing theme / design tokens / project conventions
3. Reference images/screenshots/code files
4. Sensible defaults

**Reuse modes:**
- `strict` — only existing patterns/components unless impossible
- `prefer-existing` — prefer existing, create new reusable components only when necessary (default)
- `mixed` — reuse what exists, more freedom to create new abstractions

**Responsive behavior must be explicit:**
- How multi-column sections collapse
- When grids become stacks
- Where actions move at smaller sizes
- How tables degrade for narrow screens
- What becomes tabs/accordions/drawers on mobile

**Accessibility (built-in, not optional):**
- Fields have labels
- Sections have headings
- Related fields are visually grouped
- Validation messages are clear
- Touch targets are usable on mobile
- Keyboard navigation works
- Contrast is maintained

### Phase 5: Asset Generation (if needed)

When `--image-policy` is not `none` and the plan identifies image needs:

1. Prepare arguments for the `generate-image` skill's Python script
2. Invoke via `uv run --with google-genai --with pillow .claude/shared/skills/generate-image/generate_image.py`
3. Pass relevant context: screen purpose, style/tone, aspect ratio, palette
4. Wire resulting image paths into the generated screen code
5. Record image paths in the manifest

**Typical cases for generated images:**
- Hero/banner image
- Empty-state illustration
- Onboarding artwork
- Decorative branded graphic

### Phase 6: Screen Manifest

Write `SCREEN-MANIFEST.md` alongside the generated code.

```markdown
# Screen Manifest: <screen-name>

## Purpose
<what the screen is for>

## Platform
<detected/selected platform and framework>

## Inputs Used
- Prompt: <user's description>
- Fields: <path if provided>
- Mermaid: <path if provided>
- Style references: <paths if provided>

## Repo Inspection Summary
- Existing components reused: <list>
- Theme/tokens found: <list>
- New components created: <list>

## Field Groupings
| Group | Fields |
|-------|--------|
| Personal Information | first_name, last_name, ... |
| Address | street, city, state, zip |
| ... | ... |

## Layout Plan
### Desktop
<description>

### Tablet
<description>

### Mobile
<description>

## Responsive Decisions
- <how sections collapse>
- <how tables degrade>
- <where actions move>

## Image Assets
- <none, or list of generated images with paths>

## Assumptions
- <every inference documented>

## Generated Files
- <list of files created with paths>
```

---

## Test Generation (`--with-tests`)

When `--with-tests` is specified, generate platform-appropriate tests:

**React:** Component tests (React Testing Library / Vitest)
**PySide6:** pytest tests for widget behavior
**Flutter:** Widget tests

**Test coverage targets:**
- Fields render with correct labels
- Field groupings are visually grouped
- Required field validation works
- Responsive layout changes at breakpoints
- Existing components are used (not duplicated)
- Actions/CTAs are present and functional

---

## Error Handling

| Condition | Behavior |
|-----------|----------|
| No usable context (empty prompt, no fields, no refs) | Ask user for more detail |
| Referenced file not found (--fields, --mermaid, --style-ref) | Fail with clear path error |
| Platform not detectable and not specified | Ask user to specify |
| Conflicting conventions in repo | Document in manifest, pick the dominant pattern, warn |
| generate-image fails | Warn, continue without assets, note in manifest |
| Mermaid syntax invalid | Warn, continue with other context, note in manifest |

---

## Scope Boundaries

### In scope (v1)
- Freeform text prompt input
- CSV/JSON field definitions
- Mermaid diagram context
- Style references (images, code files)
- Auto-detect platform from repo
- Repo inspection for reusable components/patterns
- Screen planning with field grouping and layout reasoning
- Code generation into project source tree
- Responsive layout (desktop/tablet/mobile)
- Integration with generate-image for assets
- Screen manifest (markdown)
- Optional test generation
- Three output modes: plan-only, full-screen, full-screen-plus-assets

### Out of scope (v1)
- Excel/xlsx parsing (CSV/JSON only)
- URL fetching for style references (local files only)
- Backend/API generation
- Database schema generation
- Multi-screen flows or navigation generation
- Visual preview rendering
- Sub-agent parallelization
- Post-generation linting/formatting hooks

---

## Acceptance Criteria

1. `/generate-screen` command triggers the skill
2. Freeform text prompt produces a screen plan
3. CSV field definitions are parsed and fields grouped intelligently
4. Mermaid diagrams are used as structural context
5. Platform is auto-detected from repo; user asked when ambiguous
6. Repo is inspected and existing components/patterns are reused
7. Generated code lands in the project's source tree (not a staging area)
8. Responsive layout is planned explicitly for desktop/tablet/mobile
9. Style references (images, code files) influence the output
10. `generate-image` is invoked when assets are needed
11. Screen manifest documents all assumptions and decisions
12. `--with-tests` generates platform-appropriate tests
13. `plan-only` mode produces plan + manifest without generating code
14. Errors are clear and actionable
