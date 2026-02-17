# Analysis: Token Usage Optimization

**Bean:** BEAN-141 | **Date:** 2026-02-16 | **Analyst:** developer

---

## 1. Executive Summary

This analysis examines token usage patterns across the Foundry AI team's 141-bean project history. Only 4 of 141 beans have telemetry data with actual token counts, representing a **2.8% coverage rate**. The available data reveals that output tokens dominate consumption (95% of total), the developer persona accounts for 89% of cost, and the telemetry capture infrastructure itself consumed $18.40 to build. The most significant optimization opportunity is not in reducing per-task token usage but in **closing the telemetry gap** so data-driven decisions become possible.

---

## 2. Data Inventory

### 2.1 Beans with Telemetry Data

| Bean ID | Title | Category | Tasks | Tokens In | Tokens Out | Cost |
|---------|-------|----------|-------|-----------|------------|------|
| BEAN-121 | Token Usage Capture via JSONL | Process | 3 | 4,789 | 75,708 | $5.70 |
| BEAN-122 | Structured Trello Linkage | Process | 5 | 6,693 | 108,013 | $8.14 |
| BEAN-123 | Project Slug Output Folder Test | App | 1 | 1,811 | 31,127 | $2.34 |
| BEAN-130 | Telemetry Cost Estimation | Process | 4 | 1,201 | 60,862 | $4.58 |
| **Totals** | | | **13** | **14,494** | **275,710** | **$20.76** |

### 2.2 Beans without Telemetry Data

**137 beans** (97.2%) have only em-dash sentinels in their telemetry tables. These fall into three groups:

1. **Pre-infrastructure beans (BEAN-001 through BEAN-120):** Created before BEAN-121 implemented the JSONL capture system. No retroactive data is available.
2. **Analysis beans (BEAN-131 through BEAN-135, BEAN-136+):** Created after the capture system but show empty telemetry. Likely cause: the telemetry-stamp hook fires on Edit/Write of bean.md and task files, but analysis beans that produce output documents in `ai/outputs/` may not trigger the hook on the right files at the right time.
3. **In-progress beans:** Currently being worked on; data may be stamped at completion.

---

## 3. Token Usage Patterns

### 3.1 Input vs. Output Token Ratio

| Metric | Value |
|--------|-------|
| Total Input Tokens | 14,494 |
| Total Output Tokens | 275,710 |
| Output/Input Ratio | **19:1** |
| Input as % of Total | 5.0% |
| Output as % of Total | 95.0% |

**Interpretation:** Claude generates approximately 19 tokens of output for every 1 token of input in this workflow. This is expected for a code-generation and document-production workload where the context (input) is relatively compact but the generated code, tests, and documentation (output) are verbose.

**Cost Implication:** At $15/MTok input vs. $75/MTok output, the 19:1 ratio means output tokens dominate cost even more heavily than volume:
- Input cost: 14,494 × $0.000015 = **$0.22** (1.1% of total)
- Output cost: 275,710 × $0.000075 = **$20.68** (98.9% of total)

**Takeaway:** Optimizing input tokens has near-zero ROI. All optimization effort should focus on output token reduction.

### 3.2 Per-Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks (with data) | 13 |
| Average Tokens In per Task | 1,115 |
| Average Tokens Out per Task | 21,208 |
| Average Cost per Task | $1.60 |
| Min Task Cost | $0.02 (BEAN-122 Task 1: template addition) |
| Max Task Cost | $2.34 (BEAN-123 Task 1: test implementation) |
| Median Task Cost | ~$1.90 |

**Observation:** The cheapest task ($0.02) was a minimal template edit; the most expensive ($2.34) was writing a full test. This suggests test-writing tasks are the most token-intensive activity type per unit of work.

### 3.3 Per-Bean Statistics

| Metric | Value |
|--------|-------|
| Average Cost per Bean | $5.19 |
| Min Bean Cost | $2.34 (BEAN-123: 1 task) |
| Max Bean Cost | $8.14 (BEAN-122: 5 tasks) |
| Average Cost per Task within a Bean | $1.60 |

**Observation:** Bean cost scales roughly linearly with task count. No bean showed disproportionate cost per task, suggesting task decomposition granularity is consistent.

---

## 4. Breakdown by Persona

| Persona | Tasks | Tokens In | Tokens Out | Cost | % of Total Cost |
|---------|-------|-----------|------------|------|-----------------|
| developer | 10 | 12,576 | 232,414 | $17.52 | 84.4% |
| tech-qa | 3 | 1,918 | 43,296 | $3.28 | 15.6% |
| team-lead | 0 | — | — | — | 0% |
| ba | 0 | — | — | — | 0% |
| architect | 0 | — | — | — | 0% |

**Key Findings:**

1. **Developer dominance:** The developer persona handles the bulk of work and cost, which is expected in a code-heavy project.
2. **Tech QA overhead:** Verification tasks consume ~16% of total cost. These tasks primarily run tests and lint checks — the actual token consumption comes from Claude reading the full codebase context, not from the verification actions themselves.
3. **Team Lead invisible:** The team-lead persona's token usage (decomposition, coordination, verification) is not captured because those activities happen as part of the orchestration conversation, not as discrete Edit/Write operations on bean files.
4. **BA/Architect skipped:** For the 4 beans with data, no BA or architect tasks were created. These were all Process and small App beans where requirements and architecture were already clear.

---

## 5. Breakdown by Category

| Category | Beans | Tasks | Tokens In | Tokens Out | Cost | % of Total |
|----------|-------|-------|-----------|------------|------|------------|
| Process | 3 | 12 | 12,683 | 244,583 | $18.42 | 88.7% |
| App | 1 | 1 | 1,811 | 31,127 | $2.34 | 11.3% |
| Infra | 0 | 0 | — | — | — | 0% |

**Caveat:** This breakdown is heavily skewed by the sample. The 3 Process beans were all telemetry infrastructure work (meta-beans that built the telemetry system itself). The project's 82 App beans have no telemetry data, so we cannot draw conclusions about relative category costs.

---

## 6. Telemetry Infrastructure Assessment

### 6.1 JSONL Capture System (BEAN-121)

The telemetry-stamp hook (`telemetry-stamp.py`, 1021 lines) implements a watermark-based token tracking system:

**How it works:**
1. Hook fires on Edit/Write of bean.md or task files
2. When a task moves to "In Progress," it reads cumulative tokens from the Claude Code JSONL conversation log and saves a watermark
3. When a task moves to "Done," it reads current cumulative tokens and computes the delta
4. Delta is written to the task's telemetry row in bean.md

**Strengths:**
- Watermark approach correctly isolates per-task token usage within a single conversation session
- Automatic — no manual token counting required
- Git-based duration calculation provides precise timing

**Weaknesses and Gaps:**

| Issue | Severity | Impact |
|-------|----------|--------|
| Hook only fires on Edit/Write of bean/task files | High | Tasks that produce outputs elsewhere (e.g., `ai/outputs/`) don't trigger token capture at the right moment |
| Worktree isolation | High | In parallel long-run mode (BEAN-010), each bean runs in a git worktree. The JSONL session file may not map correctly to the worktree's Claude Code instance |
| Pre-BEAN-121 beans have no data | Medium | 120+ beans lack retroactive data; historical analysis impossible |
| Cross-session loss | Medium | If a bean spans multiple Claude Code sessions, watermarks from session 1 are lost in session 2 |
| No aggregate tracking beyond bean.md | Low | Token data is scattered across individual bean files; only `/telemetry-report` aggregates them |

### 6.2 Coverage Gap Root Causes

The 97.2% coverage gap has these root causes:

1. **Temporal:** 85% of beans (BEAN-001 to BEAN-120) predate the telemetry system. This is a one-time gap that shrinks over time.
2. **Hook trigger mismatch:** Analysis/Process beans (BEAN-131+) that don't modify bean.md status fields via Edit/Write don't trigger the watermark lifecycle. The hook expects a status → "In Progress" write to set the watermark and a status → "Done" write to compute the delta.
3. **Worktree context:** Beans processed via `/long-run` in isolated worktrees may not have the JSONL session file accessible at the expected path.
4. **Orchestrator-driven workflows:** When an orchestrator script manages the bean lifecycle externally (updating status files, managing git worktrees), the telemetry-stamp hook may not fire in the right context.

### 6.3 Pricing Model Accuracy

The current pricing config uses Claude Opus 4 rates:
- Input: $15/MTok ($0.000015/token)
- Output: $75/MTok ($0.000075/token)

**Assessment:** These rates should be verified against Anthropic's current pricing. The config file approach (`ai/context/token-pricing.md`) is well-designed — a single update propagates to all cost calculations. However:
- No support for multiple model tiers (e.g., Haiku for simple tasks)
- No support for batch API pricing (50% discount)
- Cache read/write pricing not tracked (significant for long conversations)

---

## 7. Optimization Opportunities

### 7.1 High Priority — Close the Telemetry Gap

**Problem:** Without data on 97% of beans, optimization is guesswork.

**Recommendations:**

| # | Action | Expected Impact |
|---|--------|-----------------|
| 1 | **Fix worktree JSONL path resolution** — Update `find_session_jsonl()` in telemetry-stamp.py to handle git worktree scenarios by checking both the worktree root and the main repo root for session files | Enables capture in parallel long-run mode |
| 2 | **Add hook triggers for output files** — Extend the PostToolUse matcher to also fire on writes to `ai/outputs/**/*.md`, linking them to the current active bean/task | Captures analysis bean telemetry |
| 3 | **Add explicit watermark commands** — Provide a utility function that agents can call at task start/end boundaries regardless of which files they edit | Decouples capture from file-edit patterns |

### 7.2 High Priority — Reduce Output Token Waste

**Problem:** Output tokens are 95% of volume and 99% of cost.

**Recommendations:**

| # | Action | Expected Impact |
|---|--------|-----------------|
| 4 | **Constrain output verbosity in agent prompts** — Add instructions to persona agents: "Prefer concise implementations. Avoid redundant comments. Omit boilerplate explanations." | 10-20% output reduction per task |
| 5 | **Break large tasks into smaller ones** — BEAN-122 used 108K output tokens across 5 tasks (avg 21.6K each). Smaller tasks with focused scope reduce context accumulation | 5-15% output reduction through less context drift |
| 6 | **Use Haiku for verification tasks** — Tech QA tasks that only run `pytest` and `ruff check` don't need Opus-level reasoning. Route these to Claude Haiku at ~10% of the cost | 80% cost reduction on verification tasks (~$2.60 saved per bean with QA) |

### 7.3 Medium Priority — Improve Data Quality

**Recommendations:**

| # | Action | Expected Impact |
|---|--------|-----------------|
| 7 | **Add cache token tracking** — Claude Code's conversation cache can significantly reduce effective input costs. Track `cache_creation_input_tokens` and `cache_read_input_tokens` from JSONL messages to understand cache hit rates | Better cost modeling |
| 8 | **Add model tier to telemetry** — Record which model was used per task (Opus vs. Sonnet vs. Haiku) to enable per-model cost analysis | Enables model-routing optimization |
| 9 | **Backfill duration data from git** — Even without token data, beans BEAN-001 through BEAN-120 could have Duration backfilled from git commit timestamps on their feature branches | Partial historical analysis |

### 7.4 Low Priority — Infrastructure Improvements

**Recommendations:**

| # | Action | Expected Impact |
|---|--------|-----------------|
| 10 | **Add multi-model pricing** — Extend `token-pricing.md` to include Sonnet and Haiku rates; update cost calculations to use the correct rate based on model tier | Accurate cost when using multiple models |
| 11 | **Create a cost budget system** — Define per-bean cost budgets in bean.md and alert when a bean exceeds its budget | Prevent runaway costs on complex beans |
| 12 | **Export telemetry to CSV/JSON** — Add a `/telemetry-export` command that extracts all bean telemetry into a structured format for external analysis tools | Enables trend analysis and dashboards |

---

## 8. Projected Savings

Based on the available data (4 beans, $20.76 total):

| Optimization | Estimated Savings | Beans Affected |
|--------------|-------------------|----------------|
| Use Haiku for verification (#6) | ~$2.60/bean with QA | All beans with tech-qa tasks |
| Constrain output verbosity (#4) | ~15% on developer tasks | All beans |
| Smaller task decomposition (#5) | ~10% on multi-task beans | Beans with 3+ tasks |
| **Combined** | **~25-30% cost reduction** | **All future beans** |

**Projected impact at scale:** If the project continues at ~10 beans/week at the current average of $5.19/bean:
- Current weekly cost: ~$52
- After optimizations: ~$36-39/week
- Annual savings: ~$680-830

**Note:** These projections are based on only 4 data points and should be revised as telemetry coverage improves.

---

## 9. Comparison with Industry Patterns

While we lack external benchmarks for AI-assisted software development workflows specifically, some general observations:

1. **Token ratio (19:1 output/input)** is high compared to typical chat interactions (2-5:1) but expected for code generation tasks where input is a brief instruction and output is full source code.
2. **Cost per task ($1.60 average)** is low in absolute terms but adds up across hundreds of tasks. The key lever is not per-task cost but task count — better decomposition that avoids unnecessary tasks saves more than per-task optimization.
3. **Verification overhead (16% of cost)** is reasonable for a quality-gated workflow. This could be reduced with model routing (Haiku for QA) without sacrificing quality.

---

## 10. Recommendations Summary

| Priority | # | Recommendation | Type |
|----------|---|---------------|------|
| **High** | 1 | Fix worktree JSONL path resolution | Infrastructure |
| **High** | 2 | Add hook triggers for output files | Infrastructure |
| **High** | 3 | Add explicit watermark commands | Infrastructure |
| **High** | 4 | Constrain output verbosity in agent prompts | Workflow |
| **High** | 5 | Break large tasks into smaller ones | Workflow |
| **High** | 6 | Use Haiku for verification tasks | Model routing |
| **Medium** | 7 | Add cache token tracking | Data quality |
| **Medium** | 8 | Add model tier to telemetry | Data quality |
| **Medium** | 9 | Backfill duration data from git | Data quality |
| **Low** | 10 | Add multi-model pricing | Infrastructure |
| **Low** | 11 | Create a cost budget system | Infrastructure |
| **Low** | 12 | Export telemetry to CSV/JSON | Tooling |

---

## 11. Conclusion

The most impactful finding is not about token optimization per se — it's that **the telemetry system has insufficient coverage to support data-driven optimization**. With only 4 of 141 beans captured, any conclusions about usage patterns carry low confidence. The top priority is fixing the capture infrastructure (recommendations 1-3) so that future beans automatically record their token usage.

Among the patterns visible in the available data, output tokens are overwhelmingly dominant (99% of cost). The two highest-impact optimizations are: (1) routing verification tasks to cheaper models, and (2) constraining output verbosity in agent prompts. Together, these could reduce per-bean costs by 25-30%.

The telemetry infrastructure itself (BEAN-121 + BEAN-130) was a worthwhile investment at $10.28, as it enables all future cost visibility. The priority now is making that visibility comprehensive by closing the coverage gap.
