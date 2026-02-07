# Bean Workflow

A **Bean** is a unit of work — a feature, enhancement, bug fix, or epic. Beans replace ad-hoc task tracking with a structured, persona-aware workflow.

## Directory Structure

```
ai/beans/
  _index.md                    # Master backlog index
  _bean-template.md            # Template for creating new beans
  BEAN-NNN-<slug>/
    bean.md                    # Bean definition (problem, goal, scope, criteria)
    tasks/                     # Task files created during decomposition
      01-<owner>-<slug>.md     # Individual task assigned to a persona
```

## Bean Lifecycle

### 1. Creation

Anyone can create a bean:

1. Copy `ai/beans/_bean-template.md` to `ai/beans/BEAN-NNN-<slug>/bean.md`
2. Fill in all fields: Problem Statement, Goal, Scope, Acceptance Criteria
3. Set Status to `New` and assign a Priority
4. Add the bean to `ai/beans/_index.md`

Bean IDs are sequential: BEAN-001, BEAN-002, etc.

### 2. Picking

The Team Lead reviews the backlog (`ai/beans/_index.md`) and picks 1-3 beans to work on:

1. Assess priority and dependencies between beans
2. Update bean status from `New` to `Picked`
3. Update the index table

### 3. Decomposition

The Team Lead breaks each picked bean into tasks:

1. Read the bean's problem statement, goal, and acceptance criteria
2. Create task files in `BEAN-NNN-<slug>/tasks/` with sequential numbering
3. Assign each task an owner (persona) and define dependencies
4. Follow the natural wave: BA → Architect → Developer → Tech-QA
5. Skip personas that aren't needed for a given bean
6. Update bean status to `In Progress`

Each task file should include:
- **Owner:** Which persona handles it
- **Depends on:** Which tasks must complete first
- **Goal:** What this task produces
- **Inputs:** What the owner needs to read
- **Definition of Done:** Concrete checklist

### 4. Execution

Each persona claims their task(s) in dependency order:

1. Read the task file and all referenced inputs
2. Produce the required outputs in `ai/outputs/<persona>/`
3. Update the task file with completion status
4. Create a handoff note for downstream tasks if needed

### 5. Verification

The Team Lead reviews completed work:

1. Check each task's Definition of Done
2. Verify outputs match the bean's Acceptance Criteria
3. Run tests (`uv run pytest`) and lint (`uv run ruff check foundry_app/`)
4. Flag any gaps for rework

### 6. Closure

Once all acceptance criteria are met:

1. Update bean status to `Done`
2. Update `ai/beans/_index.md`
3. Note any follow-up beans spawned during execution

## Status Values

| Status | Meaning |
|--------|---------|
| `New` | Created, not yet reviewed by Team Lead |
| `Picked` | Team Lead has selected it for work |
| `In Progress` | Tasks have been created and execution is underway |
| `Done` | All acceptance criteria met |
| `Deferred` | Intentionally postponed |
