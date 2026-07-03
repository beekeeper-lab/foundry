# Skill: Generate Screen

## Description

Generates responsive UI screens/pages from diverse inputs including freeform text, field definitions, Mermaid diagrams, and style references. This is a higher-level orchestration skill — Claude performs the analysis, planning, and code generation directly. Generated code lands in the project's actual source tree.

## Trigger

Use this skill when the user asks to:
- Generate a UI screen, page, form, dashboard, or wizard
- Build a responsive layout from field definitions or requirements
- Create a page based on a Mermaid diagram or data model
- Build a screen that matches an existing style or reference image
- Generate a page using existing project components and patterns
- Create a UI from a CSV/JSON field list

Also used programmatically by higher-level skills.

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| (description) | Yes | — | Freeform description of the screen to build |
| `--platform` | No | auto-detect | `react`, `pyside6`, `tkinter`, `flutter` |
| `--framework` | No | — | Refinement: `tailwind`, `mui`, `shadcn`, `material` |
| `--mode` | No | `full-screen` | `plan-only`, `full-screen`, `full-screen-plus-assets` |
| `--with-tests` | No | false | Generate tests alongside the screen |
| `--screen-name` | No | inferred | Name for the screen/page |
| `--style-ref` | No | — | Repeatable. Path to reference image or code file |
| `--fields` | No | — | Path to CSV or JSON field definitions |
| `--mermaid` | No | — | Path to Mermaid diagram file |
| `--reuse` | No | `prefer-existing` | `strict`, `prefer-existing`, `mixed` |
| `--responsive` | No | `balanced` | `desktop-first`, `mobile-first`, `balanced` |
| `--image-policy` | No | `only-if-needed` | `none`, `only-if-needed`, `aggressive` |
| `--density` | No | `comfortable` | `compact`, `comfortable`, `spacious` |
| `--output-dir` | No | auto-detect | Override where generated files land |

## Process

Follow these phases in order. **Do not skip the planning phase.**

---

### Phase 1: Ingest & Normalize

Parse the user's request and gather all context.

1. Extract the freeform description from the prompt.
2. If `--fields` was provided, read the CSV or JSON file:
   - CSV: expect columns like `name`, `label`, `type`, `required`, `validation`, `group`, `help_text`
   - JSON: expect an array of field objects with similar keys
   - Missing columns are fine — infer what you can.
3. If `--mermaid` was provided, read the `.mmd` file as structural context (ERDs, flows, state diagrams).
4. If `--style-ref` was provided, read each file:
   - Image files (png, jpg): analyze visually for style signals
   - Code files (tsx, py, dart, vue): analyze for patterns, structure, component usage
5. Validate all referenced files exist. If any are missing, report the error clearly and stop.

---

### Phase 2: Detect Platform

Determine the target UI platform.

**If `--platform` was specified:** use it, skip detection.

**Otherwise, inspect the repo:**

| Signal | Platform |
|--------|----------|
| `package.json` with `react` | `react` |
| `package.json` with `next` | `react` (Next.js) |
| `pyproject.toml` with `PySide6` | `pyside6` |
| `pubspec.yaml` with `flutter` | `flutter` |
| `tailwind.config.*` present | Note: Tailwind available |
| Theme files (`theme.ts`, `theme.js`, `theme.py`) | Note: theme system exists |

**If no platform detected:** ask the user. Do not guess.

```
I couldn't detect a UI framework in this project. Which platform should I target?
- react (optionally with: tailwind, mui, shadcn)
- pyside6
- flutter
```

---

### Phase 3: Repo Inspection

Before planning or generating anything, inspect the repository for existing patterns. This prevents duplication and maintains consistency.

**Search for:**

1. **Existing pages/screens** — to follow the same file structure and patterns
   - Use Glob to find files like `**/pages/**`, `**/screens/**`, `**/views/**`
2. **Shared components** — form controls, cards, tables, modals, tabs, layout primitives
   - Use Glob to find `**/components/**`
   - Read a few key components to understand their API/props
3. **Theme and design tokens** — CSS variables, Tailwind config, theme files, spacing/typography systems
   - Look for: `theme.*`, `tailwind.config.*`, `tokens.*`, `variables.css`, `_variables.scss`
4. **Validation patterns** — existing form validation utilities or patterns
5. **Icon libraries** — what icon system is in use
6. **Routing patterns** — how pages are registered/connected
7. **Naming conventions** — PascalCase components? kebab-case files? Barrel exports?

**Build a mental inventory** of what exists. Reference this inventory throughout the remaining phases.

If `--reuse` is `strict`: you may ONLY use existing components unless truly impossible.
If `--reuse` is `prefer-existing` (default): prefer existing components, create new ones only when needed.
If `--reuse` is `mixed`: reuse what fits, create new abstractions freely.

---

### Phase 4: Screen Planning

**This is the most important phase. Do not rush it.**

Think carefully about the screen before writing any code. Produce a screen plan covering:

#### 4a. Purpose & User Tasks
- What is this screen for?
- What are the primary user tasks?
- What are the key actions/CTAs?

#### 4b. Field Grouping

Group related fields semantically, even if the source data is flat:

| Pattern | Inferred Group |
|---------|---------------|
| `first_name`, `last_name`, `middle_name` | Personal Information |
| `street`, `city`, `state`, `zip`, `country` | Address |
| `phone`, `email`, `contact_preference` | Contact Information |
| `created_at`, `updated_at`, `created_by` | Audit / Metadata (read-only, secondary) |
| `balance`, `rate`, `total` | Financial Summary |
| `notes`, `comments`, `history` | Notes / Activity |

Think about:
- Which fields belong together by domain meaning
- Which information should be prominent vs secondary
- What belongs above the fold
- Which content is summary vs detail
- Read-only vs editable sections

#### 4c. Component Mapping

Map data to UI components:

| Data Characteristic | Component |
|----|-----------|
| Short text | Text input |
| Bounded options | Select / dropdown |
| Boolean | Toggle or checkbox |
| Long text | Textarea |
| Date | Date picker or formatted display |
| List of records | Table, card list, or accordion |
| Summary metrics | Stat cards or summary strip |
| Multi-step flow | Stepper / wizard |

**Check the repo inventory first** — if a `TextField`, `SelectField`, or `DataTable` component already exists, use it.

#### 4d. Layout Plan

Determine major layout regions:
- Header / title area
- Summary strip (if applicable)
- Main content area
- Sidebar (if applicable)
- Actions / footer

Decide on the layout pattern:
- Single column form
- Two-column form with sidebar
- Dashboard grid
- Tabs with sub-sections
- Wizard steps

#### 4e. Responsive Strategy

Explicitly plan for three breakpoints:

**Desktop:** Full layout as designed.
**Tablet:** How columns collapse, what moves.
**Mobile:** Single column, what becomes accordion/drawer/tabs.

Specific decisions needed:
- How multi-column sections collapse
- When grids become stacks
- Where actions move at smaller sizes
- How tables degrade (horizontal scroll, card view, hide columns)
- What becomes tabs, accordions, or drawers on small screens

#### 4f. Image Needs

If `--image-policy` is not `none`, evaluate whether the screen needs generated images:
- Hero/banner image
- Empty-state illustration
- Onboarding artwork
- Decorative branded graphic

Most screens do NOT need generated images. Only flag images that add real value.

#### 4g. Assumptions

Document every inference:
- Why fields were grouped a certain way
- Why a component was chosen
- Why certain data is secondary/read-only
- What was assumed about the data model

---

### Phase 5: Code Generation

If `--mode` is `plan-only`, skip this phase and go to Phase 7.

#### 5a. Determine Output Location

Find where screens/pages live in this project:
- Check existing page file locations from Phase 3
- Follow the project's file/folder conventions
- If `--output-dir` was specified, use that instead

#### 5b. Generate Implementation

Generate the screen code following the plan from Phase 4.

**Style precedence (strict order):**
1. Existing application components and styles
2. Existing theme / design tokens / project conventions
3. Style references provided by the user
4. Sensible defaults

**Code quality rules:**
- Reuse existing components per the `--reuse` mode
- Follow the project's naming conventions
- Follow the project's file structure patterns
- Labels on all fields
- Sections have headings
- Validation messages are clear
- Keyboard navigation works
- Touch targets are usable on mobile
- Contrast is maintained

**Platform-specific guidance:**

**React:**
- Use existing shared components and theme
- Follow the project's routing/page pattern
- Use responsive breakpoints (CSS/Tailwind/styled-components — whatever the project uses)
- Generate reusable child components when appropriate

**PySide6:**
- Use QVBoxLayout/QHBoxLayout/QGridLayout/QFormLayout for structure
- Create reusable widget classes for repeated patterns
- Support resize-aware behavior with layout managers
- Group fields with QGroupBox or equivalent

**Flutter:**
- Follow Material conventions unless the repo uses another approach
- Organize widgets for reuse
- Use LayoutBuilder / MediaQuery for responsive behavior
- Preserve logical grouping with Card / ExpansionTile

#### 5c. Generate Tests (if `--with-tests`)

Generate platform-appropriate tests alongside the screen:

**React:** Component tests with React Testing Library / Vitest
**PySide6:** pytest tests for widget behavior
**Flutter:** Widget tests

Test coverage targets:
- Fields render with correct labels
- Field groupings are visually grouped
- Required field validation works
- Responsive layout changes at breakpoints
- Existing components are used (not duplicated)
- Actions/CTAs are present

---

### Phase 6: Asset Generation

If `--mode` is not `full-screen-plus-assets`, or if no image needs were identified in Phase 4f, skip this phase.

For each identified image need:

1. Build the CLI command for generate-image:
```bash
uv run --with google-genai --with pillow \
  .claude/shared/skills/generate-image/generate_image.py \
  --prompt "<description based on screen context>" \
  --style "<derived from screen style>" \
  --aspect-ratio "<appropriate for placement>" \
  --output-dir "<same directory as generated screen>" \
  --asset-name "<descriptive name>"
```

2. Execute the command.
3. Wire the resulting image path into the generated screen code (import, src attribute, etc.).
4. Record the image in the manifest.

---

### Phase 7: Screen Manifest

Write `SCREEN-MANIFEST.md` in the same directory as the generated code.

Use this format:

```markdown
# Screen Manifest: <screen-name>

## Purpose
<what this screen is for and the primary user tasks>

## Platform
- Detected/selected: <platform>
- Framework: <framework if any>
- Detection method: <auto-detected from X / specified by user>

## Inputs Used
- Prompt: <user's description>
- Fields: <path or "none">
- Mermaid: <path or "none">
- Style references: <paths or "none">

## Repo Inspection Summary
- Existing components reused: <list>
- Theme/tokens found: <list>
- New components created: <list with rationale>

## Field Groupings

| Group | Fields | Rationale |
|-------|--------|-----------|
| Personal Information | first_name, last_name | Name fields grouped together |
| Address | street, city, state, zip | Location fields grouped |

## Layout Plan

### Desktop
<description of desktop layout>

### Tablet
<description of tablet adaptations>

### Mobile
<description of mobile adaptations>

## Responsive Decisions
- <specific decision about how layout adapts>
- <how tables degrade>
- <where actions move>

## Component Mapping

| Field/Section | Component | Source |
|--------------|-----------|--------|
| first_name | TextField | existing (src/components/TextField) |
| status | StatusBadge | existing (src/components/StatusBadge) |
| address group | AddressForm | new (created for this screen) |

## Image Assets
<none, or list with paths and rationale>

## Assumptions
- <every inference documented>
- <why fields were grouped this way>
- <what was assumed about data model>

## Generated Files
- <list of all files created with full paths>
```

---

## Error Handling

| Condition | Behavior |
|-----------|----------|
| No usable context (empty prompt, no fields) | Ask user for more detail |
| Referenced file not found | Fail with clear path error |
| Platform not detectable and not specified | Ask user to specify |
| Conflicting conventions in repo | Document in manifest, use dominant pattern, warn |
| generate-image fails | Warn, continue without assets, note in manifest |
| Invalid Mermaid syntax | Warn, continue with other context, note in manifest |
| Invalid CSV/JSON fields file | Fail with clear parse error |

## Key Rules

- **Plan before coding.** Never skip Phase 4. The plan is the most valuable output.
- **Repo conventions win.** Existing project style always beats skill defaults.
- **Reuse first.** Check what exists before creating new components.
- **Responsive by design.** Plan all three breakpoints explicitly, not as an afterthought.
- **Document assumptions.** Every inference goes in the manifest.
- **Code goes in the source tree.** Never write to a staging area or AI output folder.
- **Images are rare.** Most screens don't need generated images. Only invoke generate-image when it adds real value.
