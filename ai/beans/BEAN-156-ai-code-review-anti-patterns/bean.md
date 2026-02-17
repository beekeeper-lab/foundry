# BEAN-156: AI Code Review Anti-Patterns

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-156 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-17 |
| **Started** | 2026-02-17 16:17 |
| **Completed** | 2026-02-17 16:20 |
| **Duration** | 3m |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The ai-team-library stacks collection lacks guidance on AI-assisted code review anti-patterns. A Trello card requests reading and summarizing the CodeRabbit article on 5 code review anti-patterns that AI can eliminate, then adding it as a tech stack option in the library.

## Goal

Add a new stack entry to `ai-team-library/stacks/` that captures the key AI code review anti-patterns and best practices from the referenced article, making this knowledge available as a reusable building block for generated projects.

## Scope

### In Scope
- Read and summarize the article at https://www.coderabbit.ai/blog/5-code-review-anti-patterns-you-can-eliminate-with-ai
- Create a new stack file under `ai-team-library/stacks/` with the summarized content
- Follow existing stack file conventions (markdown format, structure)

### Out of Scope
- Modifying existing stack files
- Adding UI or service layer changes
- Changing the Library Indexer or any application code

## Acceptance Criteria

- [ ] Article has been read and key points extracted
- [ ] New stack file created under `ai-team-library/stacks/` following existing conventions
- [ ] Content accurately reflects the article's main anti-patterns and recommendations
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create AI Code Review Anti-Patterns Stack File | Developer | — | Done |
| 2 | Verify AI Code Review Stack File | Tech-QA | 1 | Done |

> Skipped: BA (default), Architect (default)

## Notes

- Source article: https://www.coderabbit.ai/blog/5-code-review-anti-patterns-you-can-eliminate-with-ai
- This bean modifies `ai-team-library/` by explicit user request from Trello
- Look at existing stacks (e.g., `clean-code/anti-patterns.md`) for format conventions

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6994746028ec623c838773a7 |
| **Card Name** | AI Code Review Anti-Patterns |
| **Card URL** | https://trello.com/c/39PQhbjf/29-ai-code-review-anti-patterns |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create AI Code Review Anti-Patterns Stack File | Developer | 1m | 482,086 | 214 | $0.89 |
| 2 | Verify AI Code Review Stack File | Tech-QA | < 1m | 600,012 | 306 | $1.16 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 1,082,098 |
| **Total Tokens Out** | 520 |
| **Total Cost** | $2.05 |