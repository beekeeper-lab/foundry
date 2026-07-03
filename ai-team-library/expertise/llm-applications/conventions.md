---
id: llm-applications
category: Data & AI
entry: true
last-reviewed: 2026-07
---

# LLM Application & Agent Development Conventions

## Category

Data & AI

Non-negotiable defaults for building applications on large language
models: agents, tool use, RAG, evals, and cost/latency discipline. An
AI-team factory that ships no agent-development expertise would be
selling what it doesn't practice — this pack encodes what Foundry's own
process learned.

## Defaults

| Concern | Default |
|---------|---------|
| Model ids | Config-driven, never hardcoded in source |
| Model choice | Strongest model for judgment; cheaper tiers for mechanical steps |
| Tool interface | Typed schemas (JSON Schema / Pydantic) with strict validation |
| Agent-tool boundary | MCP for cross-app tools; in-process tools for app-internal ones |
| Prompt storage | Versioned files in the repo, not inline strings |
| Eval harness | Required before prompt/model changes ship; golden sets in-repo |
| Cost tracking | Log tokens per call; budget per feature, alert on drift |
| Retries | Exponential backoff on 429/5xx; idempotent tool design |
| Secrets | Provider keys from env/secret manager only; never in prompts or logs |
| Structured output | Schema-enforced (tool-call or response-format), never regex-parsed prose |

## 1. Architecture

- Separate the **agent loop** (model, tools, termination) from **domain
  logic** (what the tools do). Tools are ordinary, unit-testable functions
  with a thin schema wrapper.
- One agent with good tools beats a swarm with vague roles. Add subagents
  only when context isolation or parallelism demonstrably pays — each new
  agent multiplies prompt surface, cost, and failure modes.
- Every agent needs an explicit termination condition (max turns, budget,
  or goal predicate). Unbounded loops are incidents waiting.
- Keep conversation state replayable: log the full request/response stream
  (redacted) so failures can be reproduced offline.

## 2. Tool design

- Small, composable, described for the MODEL: the description says when to
  use the tool and what it returns, not how it's implemented.
- Validate inputs at the boundary; return actionable errors ("date must be
  ISO-8601") — the model reads them and retries.
- Prefer idempotent tools; destructive operations take a confirmation
  parameter or run behind a permission gate/hook.
- MCP servers for tools shared across applications; keep credentials in
  env passthrough (`${VAR}`), never in the server config itself.

## 3. Prompt & context engineering

- Prompts are code: versioned, reviewed, diffable files with a changelog.
- Spend context deliberately — retrieval and summaries over full-document
  stuffing; measure quality vs tokens for the top few call sites.
- System prompts state behavior contracts (role, constraints, output
  shape), not personality prose. Examples beat adjectives.
- For agent workflows, gate side-effecting behavior with enforcement
  (hooks, permission checks) rather than instructions alone — instruction
  adherence degrades under long contexts.

## 4. Evals

- Every prompt or model change runs the eval suite first. No evals, no
  ship — the LLM analogue of "no tests, no merge."
- Golden sets live in-repo, small and curated (20-200 cases); grade with
  exact-match/assertions where possible, LLM-as-judge with a rubric where
  not, and spot-audit the judge itself.
- Track eval scores over time next to cost; a "cheaper model" that drops
  quality below threshold isn't cheaper.

## 5. Cost & latency

- Log input/output/cache tokens per call with a request id; roll up per
  feature daily.
- Exploit prompt caching: stable prefixes first, volatile content last.
- Batch/queue non-interactive work; stream interactive responses.
- Set per-feature budgets and alert on drift — silent cost regressions are
  the LLM analogue of memory leaks.

## Do / Don't

- **Do** pin behavior with evals before refactoring prompts.
- **Do** treat model output as untrusted input downstream (injection,
  malformed data).
- **Don't** hardcode model ids or prices in application code — both churn
  quarterly; load from config.
- **Don't** parse free-text model output with regex when schema-enforced
  output exists.
- **Don't** let an agent's instructions be your only safety layer — pair
  with permissions/hooks for anything destructive.

## Common Pitfalls

- Prompt changes shipped without evals: quality regressions surface as
  user complaints weeks later, unattributable.
- Tool descriptions written for humans ("wrapper around FooService")
  instead of the model ("look up a customer's open orders by email").
- Retrying non-idempotent tools on timeout — duplicate side effects.
- Conversation history growing unbounded — cap turns and summarize.
- Evaluating on the demo cases the prompt was tuned against.

## Checklist

- [ ] Model ids and rates in config, not source
- [ ] Tools schema-validated, unit-tested, idempotent-or-gated
- [ ] Prompts versioned in-repo with a changelog
- [ ] Eval suite exists and runs on every prompt/model change
- [ ] Token/cost logging per call; per-feature budget with drift alerts
- [ ] Termination condition on every agent loop
- [ ] Destructive actions gated by enforcement, not instructions
