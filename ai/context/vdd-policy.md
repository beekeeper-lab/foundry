# Verification-Driven Development (VDD) Policy

Every bean must provide concrete, reproducible evidence that its acceptance criteria are met before it can be marked Done. Assertions without evidence are insufficient — the Team Lead must be able to independently verify each criterion.

## Core Principle

**No bean is Done without proof.** Each acceptance criterion requires at least one piece of verifiable evidence. The type of evidence depends on the bean's category.

## Verification by Category

### App Beans

App beans change the Python application — features, services, models, UI, CLI (`foundry_app/`, `tests/`).

| Evidence Type | Required | How to Verify |
|---------------|----------|---------------|
| Tests pass | Yes | `uv run pytest` — zero failures |
| Lint clean | Yes | `uv run ruff check foundry_app/` — zero warnings |
| New tests for new code | Yes | Each new function/method has at least one test |
| Regression tests for bug fixes | Yes | Bug-triggering input covered by a test case |
| Manual smoke test | When UI is affected | Run the app, exercise the changed screen |

**Verification checklist for App beans:**
1. Run `uv run pytest` — all tests pass
2. Run `uv run ruff check foundry_app/` — clean output
3. Confirm new code has corresponding test coverage
4. If UI changed: launch app and verify visually
5. Review acceptance criteria one-by-one with evidence

### Process Beans

Process beans change the AI team workflow — agent instructions, skills, commands, communication patterns (`.claude/`, `ai/`).

| Evidence Type | Required | How to Verify |
|---------------|----------|---------------|
| Document exists | Yes | File path confirmed, content reviewed |
| Cross-references valid | Yes | All referenced files/sections exist |
| Instructions are actionable | Yes | Each instruction has a concrete verb + target |
| No contradictions | Yes | New content does not conflict with existing docs |
| Dry-run walkthrough | When workflow changed | Mentally trace through the workflow with the new instructions |

**Verification checklist for Process beans:**
1. Confirm all new/updated documents exist at their stated paths
2. Verify every cross-reference points to a real file or section
3. Read each instruction — is it specific enough to follow without interpretation?
4. Check for contradictions with existing documentation
5. Walk through the workflow end-to-end with the changes applied

### Infra Beans

Infra beans change git workflow, hooks, branch protection, CI/CD, deployment.

| Evidence Type | Required | How to Verify |
|---------------|----------|---------------|
| Hook/script executes | Yes | Run the hook/script and confirm expected behavior |
| Git operations succeed | Yes | Test the git workflow (branch, commit, merge, push) |
| No regressions | Yes | Existing hooks and workflows still work |
| Configuration valid | Yes | Config files parse without errors |

**Verification checklist for Infra beans:**
1. Execute the new/modified hook or script
2. Verify git operations work as expected
3. Confirm existing hooks still fire correctly
4. Validate configuration file syntax

## VDD Gate

The VDD gate is a mandatory checkpoint before any bean can transition from In Progress to Done. It sits between task completion and bean closure.

**Gate process:**
1. All tasks are marked Done
2. Tech-QA has completed independent verification
3. Team Lead reviews each acceptance criterion against evidence
4. For each criterion, Team Lead records: criterion text, evidence type, pass/fail
5. All criteria must pass — any failure returns the bean for rework

**A bean that fails the VDD gate stays In Progress.** The Team Lead identifies which criteria lack evidence and routes rework to the appropriate persona.

### Programmatic Gate: `/vdd`

The `/vdd <bean-id>` command (skill: `claude/skills/vdd/SKILL.md`,
runtime: `foundry_app/services/vdd.py`) automates the per-criterion
check. It parses the bean's `## Acceptance Criteria` section, runs each
prefixed criterion, and writes a structured report at
`ai/outputs/tech-qa/vdd-<NNN>.md` (zero-padded). `/merge-bean` refuses
to merge when this report is missing or its aggregate verdict is not
`PASS`.

**Criterion-prefix convention.** Each AC checklist item may carry an
evidence-type prefix in parentheses immediately after the checkbox:

| Prefix | Meaning |
|--------|---------|
| `(test:<pytest-pattern-or-path>)` | runs `uv run pytest -q <target>`; pass = exit 0 |
| `(lint:<path>)` | runs `uv run ruff check <path>`; pass = exit 0 |
| `(file:<glob>)` | pass when at least one path matches the glob |
| `(file-contains:<glob>::<substring>)` | pass when at least one matched file contains the substring |
| (no prefix) | manual item — verdict is `PARTIAL` until Tech-QA confirms |

Example:

```
- [ ] (test:tests/test_foo.py::test_bar) Foo behaves correctly
- [ ] (lint:foundry_app/) Lint clean for foundry_app
- [ ] (file:ai/outputs/tech-qa/vdd-277.md) VDD report exists
- [ ] Manual: spot-check the wizard's persona-list scroll behavior
```

Backward-compatible: legacy criteria without prefixes still parse — they
are flagged as `MANUAL`, leaving the verdict `PARTIAL` until a human
sign-off (`/vdd --manual=pass` or a Notes override). A bean with **no
acceptance criteria at all** produces verdict `EMPTY` and the merge gate
refuses unconditionally.

## Evidence Standards

Evidence must be:
- **Concrete** — a specific command output, file path, or observation, not "it works"
- **Reproducible** — another agent could re-run the same check and get the same result
- **Current** — collected after the final code change, not from an earlier iteration
- **Documented** — recorded in the Tech-QA report or the bean closure summary

## Roles

| Role | VDD Responsibility |
|------|-------------------|
| **Developer** | Ensure code is testable; write tests alongside implementation |
| **Tech-QA** | Independent verification of all acceptance criteria; produce evidence report |
| **Team Lead** | Apply VDD gate before closing any bean; reject beans without sufficient evidence |
| **BA** | Write testable acceptance criteria (when included) |
| **Architect** | Design for verifiability (when included) |
