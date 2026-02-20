# /telemetry-report — Deep Dive

How Foundry tracks time, tokens, and cost for every bean and task — from automatic data collection through the PostToolUse hook to aggregate reporting.

## What It Does

`/telemetry-report` reads telemetry data embedded in every `bean.md` file and produces an aggregate summary: total time invested, token usage, estimated dollar cost, breakdowns by category and owner, and outlier identification.

## Usage

```
/telemetry-report                          # All Done beans
/telemetry-report --category App           # App beans only
/telemetry-report --since 2026-02-09       # Beans since a date
/telemetry-report --status all             # All beans, any status
```

| Flag | Default | Description |
|------|---------|-------------|
| `--category <cat>` | All | Filter by `App`, `Process`, or `Infra` |
| `--status <status>` | `Done` | Filter by bean status. Use `all` for everything |
| `--since YYYY-MM-DD` | None | Only beans created on or after this date |

---

## The Three-Layer Telemetry System

Foundry's telemetry isn't a single feature — it's three layers working together:

```
Layer 1: COLLECTION     telemetry-stamp.py (PostToolUse hook)
                         ↓ auto-fires on every Edit/Write to bean/task files
Layer 2: STORAGE         bean.md Telemetry section (per-task rows + summary table)
                         ↓ data lives inside the bean itself
Layer 3: REPORTING       /telemetry-report skill (reads all beans, aggregates)
```

---

## Layer 1: Automatic Data Collection (the Hook)

The heart of telemetry is `.claude/hooks/telemetry-stamp.py` — a Python script that runs automatically as a **PostToolUse hook** every time Claude edits or writes a bean or task file.

### When It Fires

The hook triggers on any `Edit` or `Write` tool call that touches files matching:
- `ai/beans/BEAN-*/bean.md`
- `ai/beans/BEAN-*/tasks/*.md`

### What It Captures

#### Timestamps (from system clock)

```
Task status → "In Progress"  ──→  Hook stamps: Started = 2026-02-19 14:32
Task status → "Done"         ──→  Hook stamps: Completed = 2026-02-19 14:45
                                               Duration = 13m
```

The hook detects status transitions by reading the `Status` field and checking if `Started`/`Completed` still have the sentinel em-dash (`—`). If so, it stamps the current time.

#### Duration (from git or timestamps)

For task files: duration is computed from `Started` → `Completed` timestamps.

For bean files: duration preferentially uses **git timestamps** — it finds the first commit on the feature branch and computes elapsed time to now. This gives second-level precision vs. the minute-level resolution of the metadata timestamps.

```python
# Simplified: git-based duration
merge_base = git merge-base test HEAD
first_commit = git log --format=%aI --reverse {merge_base}..HEAD | head -1
duration = now() - first_commit_timestamp
```

#### Tokens (from Claude's JSONL session log)

This is the most complex part. The hook reads Claude Code's internal conversation log (a `.jsonl` file in `~/.claude/projects/`) and sums token usage from the API responses.

**Watermark system for per-task token tracking:**

```
Task starts ("In Progress")
├─ Hook reads JSONL: total tokens so far = 150,000 in / 12,000 out
├─ Saves watermark to .telemetry.json: {"task_1_start_in": 150000, ...}
│
...Claude does work...
│
Task ends ("Done")
├─ Hook reads JSONL again: total tokens now = 185,000 in / 18,000 out
├─ Loads watermark: start was 150,000 / 12,000
├─ Delta: 35,000 in / 6,000 out  ← THIS TASK'S usage
└─ Writes to bean.md telemetry row: Tokens In = 35,000 | Tokens Out = 6,000
```

The watermark file (`.telemetry.json`) lives in the bean directory and stores the cumulative token count at each task's start. The delta between start and end gives per-task usage.

#### Cost (computed from tokens + pricing config)

```python
cost = (non_cached_input × $0.000015)      # $15/MTok
     + (cache_creation   × $0.00001875)     # $18.75/MTok
     + (cache_read       × $0.0000015)      # $1.50/MTok
     + (output           × $0.000075)       # $75/MTok
```

Rates are read from `ai/context/token-pricing.md`. The hook distinguishes between cache tiers because Claude Code uses prompt caching — most input tokens are cache reads (cheap) not fresh input (expensive).

---

## Layer 2: Where Telemetry Lives

Every `bean.md` has a Telemetry section with two tables:

### Per-Task Breakdown

```markdown
## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Implement feature | developer | 8m | 471,955 | 23,400 | $0.75 |
| 2 | Tech-QA verification | tech-qa | 3m | 1,082,098 | 15,200 | $2.05 |
```

### Summary Totals

```markdown
| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 11m |
| **Total Tokens In** | 1,554,053 |
| **Total Tokens Out** | 38,600 |
| **Total Cost** | $2.80 |
```

Both tables start with sentinel em-dashes (`—`) and get filled in automatically by the hook as tasks progress. The summary totals are computed when the bean is marked Done — either by the hook (summing per-task rows) or by `/internal:merge-bean` (as a pre-merge step).

---

## Layer 3: The Report

`/telemetry-report` reads all `bean.md` files and aggregates across the project.

### Report Structure

```
===================================================
TELEMETRY REPORT
===================================================
Pricing:  Claude Opus 4 — $15/MTok in, $75/MTok out
          (from ai/context/token-pricing.md)
Beans:    110 total (95 with data, 15 without)
Time:     23h 8m total
Average:  14m per bean
Median:   11m per bean
Cost:     $182.90 total ($1.93 avg per bean)
===================================================

BY CATEGORY
| Category | Beans | Total Time | Avg Time | Total Cost | Avg Cost |
|----------|-------|------------|----------|------------|----------|
| App      | 80    | 18h 30m    | 13m      | $142.50    | $1.78    |
| Process  | 20    | 3h 10m     | 9m       | $28.30     | $1.42    |
| Infra    | 10    | 1h 28m     | 8m       | $12.10     | $1.21    |

BY OWNER
| Owner     | Beans | Total Time | Avg Time | Total Cost | Avg Cost |
|-----------|-------|------------|----------|------------|----------|
| team-lead | 95    | 20h 5m     | 12m      | $155.00    | $1.63    |
| developer | 15    | 3h 3m      | 12m      | $27.90     | $1.86    |

MOST EXPENSIVE BEANS
| Bean     | Title                    | Cost   | Tokens      |
|----------|--------------------------|--------|-------------|
| BEAN-156 | AI Code Review Patterns  | $2.05  | 1,082,098   |
| BEAN-154 | Trello Test              | $0.75  | 471,955     |
| ...      | ...                      | ...    | ...         |

LONGEST BEANS
| Bean     | Title                    | Duration |
|----------|--------------------------|----------|
| BEAN-100 | Parallel Mode            | 45m      |
| BEAN-089 | UI Wizard Overhaul       | 38m      |
| ...      | ...                      | ...      |
===================================================
```

### How Cost Is Computed

For each bean, the report either:
1. Uses the pre-computed `Total Cost` from the bean's telemetry summary (if populated by the hook), or
2. Computes it from token totals: `(tokens_in x input_rate) + (tokens_out x output_rate)`

Rates come from `ai/context/token-pricing.md` — a single config file so pricing updates propagate everywhere.

---

## Call Chain

```
YOU type: /telemetry-report
│
├─ READ  ai/context/token-pricing.md     (get $/token rates)
├─ READ  ai/beans/_index.md              (get bean list)
├─ Apply filters (--category, --status, --since)
│
├─ For EACH matching bean:
│   └─ READ  ai/beans/BEAN-NNN-<slug>/bean.md
│       └─ Parse: Duration, Started, Completed, Category, Owner
│       └─ Parse: per-task telemetry rows (Duration, Tokens In/Out, Cost)
│       └─ Parse: summary totals (Total Tasks, Duration, Tokens, Cost)
│
├─ Compute aggregates:
│   ├─ Total/avg/median duration
│   ├─ Total/avg tokens (in + out)
│   ├─ Total/avg cost
│   ├─ Breakdown by category
│   ├─ Breakdown by owner
│   └─ Outlier identification (top 5 expensive, longest, cheapest)
│
└─ Render report to console
```

**No other skills or commands are called.** This is a pure read-and-compute operation.

---

## Data Flow: End to End

```
Claude edits a task file (status → "In Progress")
    │
    ▼
PostToolUse hook fires (telemetry-stamp.py)
    ├─ Stamps Started timestamp
    ├─ Reads JSONL → records token watermark in .telemetry.json
    │
Claude does work (writes code, runs tests, etc.)
    │
Claude edits the task file (status → "Done")
    │
    ▼
PostToolUse hook fires again
    ├─ Stamps Completed timestamp
    ├─ Computes Duration (Completed - Started)
    ├─ Reads JSONL → computes token delta from watermark
    ├─ Computes cost from tokens × rates
    ├─ Writes Duration, Tokens In, Tokens Out, Cost to task's telemetry row in bean.md
    │
Bean marked Done → hook computes summary totals
    │
    ▼
/telemetry-report reads all bean.md files → aggregate report
```

---

## Real Data from This Project

Actual telemetry from completed Foundry beans:

| Bean | Title | Duration | Tokens In | Tokens Out | Cost |
|------|-------|----------|-----------|------------|------|
| BEAN-156 | AI Code Review Anti-Patterns | — | 1,082,098 | — | $2.05 |
| BEAN-155 | Trello Lifecycle E2E Test | — | 1,204,845 | — | $0.50 |
| BEAN-154 | Trello Test | — | 471,955 | — | $0.75 |
| BEAN-122 | Structured Trello Linkage | — | 6,693 | — | — |
| BEAN-130 | Telemetry Cost Estimation | — | 1,201 | — | — |
| BEAN-157 | Test Generator Stage Callback | 1m | 30 | 187 | $0.01 |

The wide range (30 tokens to 1.2M tokens) reflects the difference between simple process beans and complex code beans.

---

## Validating Token Accuracy

The token numbers come from Claude Code's JSONL session log — but how do you know they're accurate? Here are strategies to validate:

### 1. Cross-Reference with Anthropic's Usage Dashboard

Anthropic provides a usage dashboard at `console.anthropic.com` that shows API token consumption by day, by model, and by API key. Compare:
- Pick a day where you ran a single bean in isolation
- Sum the Tokens In + Tokens Out from that bean's telemetry
- Compare against the Anthropic dashboard's usage for that day
- They should be in the same ballpark (dashboard may include overhead from system prompts)

### 2. Spot-Check the JSONL Directly

The hook reads from `~/.claude/projects/<project-hash>/<session>.jsonl`. You can manually inspect it:

```bash
# Find the most recent session file
ls -lt ~/.claude/projects/-home-gregg-Nextcloud-workspace-foundry/*.jsonl | head -1

# Sum tokens from all assistant messages
cat <file>.jsonl | python3 -c "
import json, sys
tin, tout = 0, 0
for line in sys.stdin:
    msg = json.loads(line)
    if msg.get('type') == 'assistant':
        u = msg.get('message',{}).get('usage',{})
        tin += u.get('input_tokens',0) + u.get('cache_creation_input_tokens',0) + u.get('cache_read_input_tokens',0)
        tout += u.get('output_tokens',0)
print(f'Total In: {tin:,}  Total Out: {tout:,}')
"
```

Compare this against what the hook wrote to the bean's telemetry. If you ran only one bean in that session, the session total should match the bean total.

### 3. Watermark Delta Sanity Check

The `.telemetry.json` watermark file in each bean directory stores the start/end snapshots:

```bash
cat ai/beans/BEAN-NNN-<slug>/.telemetry.json
```

```json
{
  "task_1_start_in": 150000,
  "task_1_start_out": 12000,
  "task_2_start_in": 185000,
  "task_2_start_out": 18000
}
```

Verify that:
- Task 2's start equals Task 1's end (no gap between tasks)
- The deltas (task 2 start - task 1 start) match what's in the telemetry table
- The final task's end minus its start matches its reported tokens

### 4. Run a Known-Cost Operation

Run a minimal bean with a predictable workload — e.g., a bean that only adds a single comment to a file. The token count should be low and roughly predictable:
- System prompt + CLAUDE.md + agent file = ~X tokens input (measurable)
- A simple edit = low output tokens
- Compare actual vs. expected to calibrate your confidence

### 5. Compare Parallel vs Sequential for the Same Work

If you run similar beans both ways (one via `/long-run` sequential, one via `/long-run --fast`), the per-bean token counts should be roughly comparable for similar-sized beans. Large discrepancies would suggest the watermark system is miscounting in one mode.

### 6. Check for Cache Tier Accuracy

The hook distinguishes three input token tiers: non-cached, cache creation, and cache read. But the telemetry table only shows a single "Tokens In" number (the sum). To verify tier breakdown:

```bash
# Read the watermark and compute tier costs manually
python3 -c "
import json
wm = json.load(open('ai/beans/BEAN-NNN-slug/.telemetry.json'))
# Look at the cache creation and cache read watermarks
print('Cache creation:', wm.get('task_1_start_cc', 'N/A'))
print('Cache read:', wm.get('task_1_start_cr', 'N/A'))
"
```

Most input tokens should be cache reads (cheap at $1.50/MTok) rather than fresh input ($15/MTok). If the cost seems high relative to token count, the cache tier split may be off.

### 7. Build a Reconciliation Script

For production-grade validation, build a script that:
1. Reads all `bean.md` telemetry totals
2. Sums them for a total project cost
3. Compares against the Anthropic billing dashboard for the same period
4. Reports the delta as a percentage

A delta under 10-15% is expected (dashboard includes system overhead, retries, and non-bean work). A delta over 30% warrants investigation.

### Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Watermark relies on JSONL file discovery | If the wrong session file is found, token counts are wrong | The hook uses `git rev-parse --git-common-dir` for worktree support, but edge cases exist |
| No watermark = full session attributed to first task | If the hook can't save a watermark at task start, the entire session's tokens go to that task | Check `.telemetry.json` exists after task starts |
| Cache tier split is estimated | The "Tokens In" number is the sum of all three tiers, but cost computation uses tier-specific rates | Verify via Anthropic dashboard that cache hit rates look reasonable |
| Minute-level timestamp resolution | Duration computed from timestamps has 1-minute granularity; sub-minute tasks show "< 1m" | Git-based duration (used for bean-level) has second-level precision |
| Parallel mode token isolation | Each worker has its own JSONL session, so watermarks work correctly — but the orchestrator's tokens (dashboard loop, merging) are not attributed to any bean | Orchestrator overhead is typically small relative to worker tokens |
