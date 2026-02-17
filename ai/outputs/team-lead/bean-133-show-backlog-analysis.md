# Analysis: /show-backlog Command

**Bean:** BEAN-133 — Analyze Show Backlog Command
**Date:** 2026-02-16
**Author:** Developer (Process Analysis)

---

## 1. Current Implementation Review

### Location & Format

The `/show-backlog` command exists only as a legacy command file at `.claude/commands/show-backlog.md`. It has **not** been migrated to the structured SKILL.md format used by all other major skills in the `.claude/skills/` directory.

### Functional Summary

The command provides a simple read-only view of the bean backlog:

1. **Parse** `ai/beans/_index.md` to get all beans
2. **Filter** by `--status` or `--category` (optional)
3. **Enrich** by reading each bean's `bean.md` Goal section (first sentence) for a summary
4. **Display** a 3-column markdown table: Bean ID, Summary, Category
5. **Show counts** below the table: `N total, N done, N open`

### Supported Filters

| Flag | Values | Default |
|------|--------|---------|
| `--status` | `Unapproved`, `Approved`, `In Progress`, `Done`, `Deferred`, `open` (shortcut for all non-Done) | Show all |
| `--category` | `App`, `Process`, `Infra` (case-insensitive) | Show all |

### Strengths

- **Simple and focused** — does one thing (display backlog) without side effects
- **Useful `open` shortcut** — the `--status open` filter is a convenient way to see all actionable beans
- **Category filter** — allows quick filtering by work type, useful during focused sessions
- **Summary enrichment** — reading the Goal section from each bean.md adds context beyond just the title

### Weaknesses

- **No structured SKILL.md** — lacks the standardized sections (Trigger, Inputs, Process, Outputs, Quality Criteria, Error Conditions) that all peer skills have
- **Sparse output columns** — only shows Bean ID, Summary, Category. Missing: Priority, Status, Owner
- **No error handling defined** — what happens if `_index.md` is missing, or a bean.md doesn't exist?
- **No sorting options** — no way to sort by priority, status, or creation date
- **No dependency visibility** — no way to see bean dependencies

---

## 2. SKILL.md Format Comparison

### Reference Skills Analyzed

| Skill | File | Sections Present |
|-------|------|-----------------|
| `/bean-status` | `.claude/skills/bean-status/SKILL.md` | Description, Trigger, Inputs, Process (6 steps), Outputs, Quality Criteria (5), Error Conditions (2), Dependencies |
| `/backlog-refinement` | `.claude/skills/backlog-refinement/SKILL.md` | Description, Trigger, Inputs, Process (4 phases, 12 steps), Outputs, Quality Criteria (7), Error Conditions (4), Dependencies |
| `/backlog-consolidate` | `.claude/skills/backlog-consolidate/SKILL.md` | Description, Trigger, Inputs, Process (4 phases, 17 steps), Outputs, Quality Criteria (8), Error Conditions (4), Dependencies |

### Gap Analysis: show-backlog vs. SKILL.md Standard

| Section | SKILL.md Standard | show-backlog Status | Gap Severity |
|---------|-------------------|---------------------|-------------|
| Description | 1-2 sentence skill summary | Present (line 1 of command file) | Low — exists but informal |
| Trigger | When/how the skill is invoked | Missing | Medium |
| Inputs | Typed input table with Required flag | Partially present as CLI flags in Usage section | Medium — format differs |
| Process | Numbered steps with detail | Present (5 steps) | Low — content exists, format differs |
| Outputs | Typed output table | Missing | High — no formal output definition |
| Quality Criteria | Testable quality checklist | Missing entirely | High |
| Error Conditions | Table of error → cause → resolution | Missing entirely | High |
| Dependencies | List of required files/resources | Missing | Medium |
| Examples | Usage examples | Present (3 examples) | Low — good coverage |

### Missing Sections (High Priority)

1. **Outputs** — No formal output type defined. Should specify that the output is console text (a markdown table displayed in conversation).

2. **Quality Criteria** — No testable quality standards. Peer skills define 5-8 criteria. Suggested criteria:
   - All beans in `_index.md` are represented in unfiltered output
   - Filtered output includes only beans matching the filter
   - Summary text is the first sentence of the Goal section, not the title
   - Count line accurately reflects the displayed set
   - Output renders as a valid markdown table

3. **Error Conditions** — No error handling specified. Minimum needed:
   - `IndexNotFound` — `_index.md` does not exist
   - `EmptyBacklog` — Index has no bean rows
   - `BeanFileMissing` — A bean referenced in `_index.md` has no `bean.md` file (graceful degradation needed)

---

## 3. Functional Gaps

### 3.1 Missing Output Columns

The current 3-column table (Bean ID, Summary, Category) omits critical information:

| Missing Column | Importance | Rationale |
|----------------|-----------|-----------|
| **Priority** | High | Users need to see priority to make decisions about what to work on next |
| **Status** | High | Without status, the table is just a list with no lifecycle context |
| **Owner** | Medium | Useful when multiple agents work in parallel to see who owns what |

**Recommendation:** Add Priority and Status columns at minimum. Consider Owner as optional (shown when `--verbose` or when any bean has an owner).

### 3.2 No Sorting

The command displays beans in index order (by Bean ID). No option to sort by:
- Priority (High → Medium → Low)
- Status (In Progress → Approved → Unapproved → Done)
- Category

**Recommendation:** Add `--sort <field>` flag. Default sort by Bean ID is fine for most use cases.

### 3.3 No Count Breakdown by Status

The count line shows only `N total, N done, N open`. This could be richer:

**Current:** `166 total, 130 done, 36 open`
**Improved:** `166 total | 130 Done | 5 In Progress | 11 Approved | 6 Unapproved | 14 Deferred`

### 3.4 No Grouping Option

The `/bean-status` skill groups beans by status (In Progress first, then Approved, etc.). The `/show-backlog` command shows a flat list. For large backlogs (166+ beans), grouped output is much more scannable.

**Recommendation:** Add `--group` flag to group by status (like `/bean-status`) or by category.

### 3.5 Graceful Handling of Missing Bean Files

The command reads each bean's `bean.md` to extract the Goal summary. If a bean directory or file is missing (e.g., deleted or corrupted), the behavior is undefined.

**Recommendation:** Fall back to using the title from `_index.md` if `bean.md` cannot be read. Log a warning.

### 3.6 No Pagination or Limit

With 166+ beans, the full unfiltered output is very long. No `--limit N` or `--recent N` option exists.

**Recommendation:** Consider `--limit N` to show only the first N results, or `--recent N` to show the N most recently created beans.

---

## 4. Overlap Analysis: /show-backlog vs. /bean-status

### Feature Comparison

| Feature | /show-backlog | /bean-status |
|---------|--------------|-------------|
| **Primary purpose** | Display backlog table with summaries | Dashboard with status grouping |
| **Output format** | Flat table | Grouped by status with headers |
| **Columns** | Bean ID, Summary, Category | Bean ID, Title, Priority, Owner, Tasks, Duration, Tokens |
| **Filters** | `--status`, `--category` | `--filter` (by status) |
| **Enrichment** | Reads Goal section for summary | Reads tasks table, telemetry (verbose mode) |
| **Counts** | Total/done/open | Per-status counts |
| **Actionable items** | No | Yes — "Next Actions" section |
| **Verbose mode** | No | Yes — task-level detail |

### Overlap Assessment

These two commands serve **different but complementary** purposes:

- **`/show-backlog`** is a **catalog view** — "What exists?" Quick scan of all beans with summaries and category filtering.
- **`/bean-status`** is a **dashboard view** — "What's happening?" Status-focused with task progress and telemetry.

The overlap is modest: both read `_index.md` and both can filter by status. But their output formats, enrichment strategies, and intended audiences differ.

### Recommendation

**Keep both commands.** They serve different use cases:
- `/show-backlog` for discovery and browsing (especially with category filter)
- `/bean-status` for operational awareness and work planning

However, `/show-backlog` should be enhanced to include Priority and Status columns so users don't have to switch to `/bean-status` just to see basic metadata.

---

## 5. Recommendations

### Priority 1: Migrate to SKILL.md Format (High)

Create `.claude/skills/show-backlog/SKILL.md` with all standard sections:
- Description, Trigger, Inputs (typed table), Process, Outputs, Quality Criteria, Error Conditions, Dependencies
- Deprecate or remove `.claude/commands/show-backlog.md` after migration

### Priority 2: Add Missing Output Columns (High)

Expand the output table from 3 columns to 5:

```
| Bean | Summary | Category | Priority | Status |
|------|---------|----------|----------|--------|
```

### Priority 3: Add Error Conditions (High)

Define graceful handling for:
- Missing `_index.md`
- Empty backlog
- Missing individual `bean.md` files (fall back to title)

### Priority 4: Add Quality Criteria (Medium)

Define 5+ testable quality standards for the output.

### Priority 5: Enhanced Count Line (Medium)

Show per-status breakdown instead of just total/done/open.

### Priority 6: Add Grouping Option (Low)

Add `--group` flag to group output by status or category, with an option for flat list (current behavior as default).

### Priority 7: Add Sorting (Low)

Add `--sort` flag for priority or status-based sorting.

### Priority 8: Add Limit/Pagination (Low)

Add `--limit N` for large backlogs.

---

## 6. Suggested Bean Scope for Enhancement

A future enhancement bean should cover Priorities 1-4 at minimum:

**Title:** Migrate Show Backlog to SKILL.md Format
**Category:** Process
**Estimated Complexity:** Small (1 task, Developer only)
**Scope:**
- Create `.claude/skills/show-backlog/SKILL.md` with full structured format
- Add Priority and Status columns to output table
- Add error conditions (missing index, empty backlog, missing bean files)
- Add quality criteria
- Enhanced count line with per-status breakdown
- Remove legacy `.claude/commands/show-backlog.md`

Priorities 5-8 (grouping, sorting, pagination) could be deferred to a separate bean or bundled if scope permits.
