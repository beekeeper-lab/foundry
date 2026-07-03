# Skill: Orchestration Report

## Description

Aggregates the per-bean **Orchestration Telemetry** blocks (BEAN-278) across
recent Done beans and produces a markdown report that answers the
architecture-aware-evaluation question: **is the orchestration paying for
itself?** Distinct from `/telemetry-report` (which aggregates raw cost,
duration, and tokens); this skill aggregates the orchestration-quality
metrics layered on top — bounces, persona activations, contract
violations, escape-hatch usage, dispatch-mode mix.

The report is meant to be read by the Team Lead (and any human reviewer)
when deciding whether to keep, tune, or roll back orchestration changes
introduced by the BEAN-269 / 270 / 272 / 274 cluster.

## Trigger

- Invoked by the `/orchestration-report` slash command.
- Should be run periodically by the Team Lead (cadence at their discretion;
  monthly is a reasonable default).
- Useful immediately after a wave of orchestration-related beans lands —
  the verdict paragraph is the honest answer to "did this help?"

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `--since YYYY-MM-DD` | String | No | Lower bound on the bean's `Completed` date. Default: 30 days before today. |
| `--until YYYY-MM-DD` | String | No | Upper bound on the bean's `Completed` date. Default: today. |
| `--out PATH` | Path | No | Override the output path. Default: `ai/outputs/team-lead/orchestration-report-YYYY-MM-DD.md` (today's date). |
| `--include-incomplete` | Flag | No | Include beans whose Orchestration Telemetry block is partly populated (default: only include beans where every field has a non-sentinel value). |

## Process

### 1. Identify the candidate beans

- Read `ai/beans/_index.md` to enumerate beans.
- Filter to `Status: Done`.
- Filter to `Completed` (or `Started` when `Completed` missing) within
  the `[--since, --until]` window.
- For each candidate, open the bean's `bean.md` and locate the
  `## Orchestration Telemetry` section.
  - If the section is missing → bucket as **legacy** (counted in
    coverage stats, otherwise excluded).
  - If the section exists but has any sentinel `—` field AND
    `--include-incomplete` is not set → bucket as **partial**
    (counted in coverage stats, excluded from aggregations).
  - If the section is fully populated → bucket as **eligible**.

### 2. Parse the Orchestration Telemetry fields

For each eligible bean, parse:

- `Personas activated` → comma-separated list. Strip whitespace, lowercase.
- `Bounces` → integer (strip the `(hint)` suffix).
- `Scope changes` → integer.
- `Contract violations` → integer.
- `Inputs escape-hatch invocations` → integer.
- `Dispatch mode` → one of `in-process`, `tmux-worker`, `mixed`.

Also parse the bean's regular Telemetry summary so cost can be cross-cut:

- `Total Cost`, `Total Duration`, `Total Tokens In/Out`, `Total Tasks`.

### 3. Compute aggregations

The report MUST compute at minimum the following aggregations across the
eligible-bean set. Each is a table or a one-liner in the rendered report.

| Aggregation | Computation |
|-------------|-------------|
| **Coverage** | `eligible / (eligible + partial + legacy)` Done beans in window have a fully-populated Orchestration Telemetry block. |
| **Persona-set frequency** | Group beans by their sorted `Personas activated` set. Show count and average bounces per group. Highlights whether 4-persona waves bounce more than 2-persona waves. |
| **Average bounces by persona-set** | Mean of `Bounces` within each persona-set group. |
| **Average cost-per-bean by persona count** | Group beans by `len(Personas activated)`. Show count, mean Total Cost, median Total Cost. Tells whether more personas systematically cost more. |
| **Dispatch-mode mix** | Count of beans by Dispatch mode. Cross-cut: mean Total Cost per dispatch mode (does `tmux-worker` cost less or more than `in-process` per bean?). |
| **Contract violations caught** | Sum of `Contract violations`. Compare to total bounces — when a contract caught the issue, no bounce was needed. |
| **Escape-hatch trend** | Sum of `Inputs escape-hatch invocations`. If `--since` covers ≥60 days, also compute the by-month series so a trend is visible. A rising trend signals BEAN-272's `Inputs:` requirement may be too strict. |
| **Outliers** | Top 3 highest-bounces beans and top 3 highest-cost beans, with bean ID, title, and the offending value. |

### 4. Render the report

Render to the `--out` path (or the dated default). The rendered markdown
has these sections in order:

```
# Orchestration Report — YYYY-MM-DD

| Field | Value |
|-------|-------|
| **Window** | YYYY-MM-DD → YYYY-MM-DD |
| **Eligible beans** | N (out of M Done beans in window) |
| **Coverage** | N / M (P%) |

## Verdict

<one-paragraph verdict — see template below>

## Persona-set frequency

<table>

## Average cost-per-bean by persona count

<table>

## Dispatch-mode mix

<table>

## Contract violations vs bounces

<one-liner with both totals + ratio>

## Escape-hatch trend

<by-month table when window ≥60 days, else single total>

## Outliers

<two short tables: highest bounces, highest cost>

## Coverage caveats

<explicit list of bean IDs that were partial or legacy and therefore
excluded from aggregations>
```

### 5. Verdict-paragraph template

The verdict is the most-load-bearing prose in the report. It MUST cite at
least two specific metrics with values, and it MUST be willing to deliver
bad news. Use this template (substitute bracketed slots with computed
values):

> Across the [N] eligible beans completed [WINDOW], the orchestration
> changes [HELPED / DID NOT HELP / WERE NEUTRAL]. Bounces averaged
> [X] per bean overall and [Y] per bean for the [persona-set] wave —
> [interpretation]. Contract violations caught [Z] issues at compose
> time, [meaningful fraction] of the [Z + bounces] places where the
> contract layer or a bounce intervened. Dispatch-mode-mix shows
> [tmux-worker / in-process / mixed] beans cost [more / less / about
> the same] on average ([\$A] vs [\$B]). The honest read: [one
> sentence: keep, tune, or roll back].

If coverage is below 50%, prepend the verdict with a one-line caveat:
"Coverage is [P%]; treat the figures as directional, not conclusive."

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `report` | Markdown file | `ai/outputs/team-lead/orchestration-report-YYYY-MM-DD.md` (or the `--out` override). |
| `console_summary` | Console text | One-line printout of the report path plus the verdict's first sentence. |

## Quality Criteria

- The verdict paragraph cites at least two metrics with concrete values.
- Coverage is reported honestly: if fewer than half the Done beans in the
  window had a fully-populated Orchestration Telemetry block, the report
  says so up front.
- Aggregations exclude the partial/legacy bean buckets; those beans are
  listed in **Coverage caveats** so the omission is auditable.
- The report is reproducible: re-running with the same `--since` /
  `--until` produces the same numbers (no time-of-day dependence beyond
  the dated filename).
- The skill never modifies the source bean.md files; it only reads them.

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `NoEligibleBeans` | Window contains zero beans with a fully-populated Orchestration Telemetry block | Report still emits, with empty aggregation tables and a verdict that says "insufficient data." |
| `BacklogIndexMissing` | `ai/beans/_index.md` does not exist | Fail with a clear message asking the user to run `/show-backlog` first. |
| `MalformedTelemetry` | A bean's Orchestration Telemetry table cannot be parsed | Skip that bean, log it under Coverage caveats, continue. |
| `OutDirNotWritable` | The output directory cannot be written | Fail with the path; suggest checking permissions. |
| `WindowInverted` | `--since` is later than `--until` | Fail with a clear message. |

## Dependencies

- **Bean template** — `ai/beans/_bean-template.md` carries the canonical
  Orchestration Telemetry block (added by BEAN-278).
- **Telemetry stamp hook** — `.claude/hooks/telemetry-stamp.py` populates
  `Personas activated` and `Dispatch mode` automatically; this skill
  consumes those values, it does not re-derive them.
- **`/spawn-task`** — writes the per-task dispatch-mode markers under
  `ai/beans/<BEAN-ID>-<slug>/.orchestration/`. Workers MUST emit those
  markers for `Dispatch mode` to be accurate.
- **`/handoff`** — increments the `Bounces` counter on Tech-QA→Developer
  hand-backs.
- **Backlog index** — `ai/beans/_index.md` for the candidate-bean list.
- **Companion skill** — `/telemetry-report` covers raw cost/duration/token
  aggregations; this skill layers the orchestration-quality metrics on
  top. Run them together for a complete picture.
