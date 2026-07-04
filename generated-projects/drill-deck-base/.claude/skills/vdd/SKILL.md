# Skill: VDD (Verification-Driven Development) Gate

## Description

Runs the programmatic VDD gate for a bean: parses the bean's
`## Acceptance Criteria` section, dispatches each criterion's evidence
type to the matching runner (test, lint, file, file-contains, or
manual), aggregates the results into a pass/fail verdict, and writes
a structured markdown report at
`ai/outputs/tech-qa/vdd-<NNN>.md` (zero-padded NNN).

This is the machine-checkable counterpart to the prose VDD policy in
`ai/context/vdd-policy.md`. The policy still governs *what* counts as
evidence; this skill enforces it programmatically so `/merge-bean` can
refuse beans whose acceptance criteria are unverified.

## Trigger

- Invoked by the `/vdd` slash command.
- Called automatically by `/merge-bean` as a pre-merge gate.
- Tech-QA may call it during the verification wave to confirm an AC sweep.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| bean_id | String | Yes | Bean identifier (`BEAN-277` or just `277`) |
| --manual | Enum | No | `pending` (default) or `pass` — see Aggregate Verdict |
| --repo-root | Path | No | Repo root override (default: cwd) |

## Process

### Phase 1: Locate the bean

1. Normalize the bean ID to canonical zero-padded form (`277` → `BEAN-277`).
2. Resolve `ai/beans/BEAN-NNN-<slug>/` by globbing for `BEAN-NNN-*`.
   - If no directory matches: exit code `3`, error message names the bean.
3. Read `bean.md`. If absent, the same error path applies.

### Phase 2: Parse acceptance criteria

4. Locate the `## Acceptance Criteria` heading (case-insensitive).
   Stop at the next `## ` heading.
5. For every line matching the prefixed checklist regex
   `^- \[[ xX]\] \(([a-z-]+):([^)]+)\) (.+)$`, capture:
   - `kind` — the evidence type (`test`, `lint`, `file`, `file-contains`).
   - `target` — the raw target string after the `:`.
   - `text` — the human-readable criterion text.
6. Lines matching the plain checklist regex `^- \[[ xX]\] (.+)$` (no
   prefix) are recorded as **manual** criteria.
7. If no checklist items are found in the section (or the section is
   missing), produce verdict `EMPTY` and exit code `2`.
   `/merge-bean` interprets `EMPTY` as a hard failure — a bean with no
   acceptance criteria cannot pass the gate.

### Phase 3: Dispatch per criterion

For each criterion, dispatch by `kind`:

| Kind | Runner | Pass condition |
|------|--------|----------------|
| `test` | `subprocess.run(["uv","run","pytest","-q",target], cwd=repo_root)` | exit code 0 |
| `lint` | `subprocess.run(["uv","run","ruff","check",target], cwd=repo_root)` | exit code 0 |
| `file` | `Path(repo_root).glob(target)` | at least one match |
| `file-contains` | split target on `::` → `<glob>::<substring>`; glob then read each file | substring present in any matched file |
| (none) | record as `MANUAL` | n/a — see Aggregate Verdict |

All `subprocess` calls use **argument lists, never shell strings** — no
shell metacharacter interpolation is possible. On failure, the runner
captures the last few lines of stderr/stdout into the report's `details`
column for quick diagnosis.

### Phase 4: Aggregate verdict

8. Compute the aggregate verdict from the per-criterion results:

| Verdict | Condition | Exit code |
|---------|-----------|-----------|
| `PASS` | all results are `PASS`, no manual items | 0 |
| `FAIL` | any result is `FAIL` | 1 |
| `PARTIAL` | all programmatic results pass but at least one manual item remains | 1 |
| `EMPTY` | no checklist items found | 2 |

`--manual=pass` upgrades `PARTIAL` to `PASS`. Use this after Tech-QA
has manually confirmed the unprefixed criteria; the merge gate still
requires the upgraded run to be on disk.

### Phase 5: Render report

9. Write `ai/outputs/tech-qa/vdd-<NNN>.md` with:
   - Title: `# VDD Report — BEAN-NNN`
   - Aggregate verdict line.
   - One row per criterion: index, result, kind, target, criterion text,
     short details.
   - For `EMPTY` verdict, include a one-line note.
10. Re-running overwrites the previous report (idempotent).

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| report | Markdown file | `ai/outputs/tech-qa/vdd-<NNN>.md` |
| stdout | Text | Report path and aggregate verdict |
| exit_code | Int | See Phase 4 table |

## Quality Criteria

- The runner never invokes `subprocess` with a shell string — all
  external commands are passed as argument lists.
- The report file is fully overwritten on every run (no append, no
  stale data).
- A bean with no `## Acceptance Criteria` section produces an `EMPTY`
  verdict and a non-zero exit so the merge gate refuses.
- A bean whose criteria all use prefixes can produce a `PASS` without
  human interaction.
- A bean with only unprefixed criteria produces `PARTIAL` (or `PASS`
  with `--manual=pass`), never an unjustified `PASS`.

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `BeanNotFound` | No directory matches `BEAN-NNN-*` | Verify the bean ID |
| `BeanMissingAC` | Bean has no AC section or it is empty | Add criteria; exit 2 makes `/merge-bean` refuse |
| `UnknownKind` | Prefix is not in the recognized set | Fix the prefix; the criterion is reported as `FAIL` |
| `MalformedFileContains` | `file-contains:` target lacks the `::` separator | Fix the target |
| `RunnerNonZero` | `pytest`/`ruff` returned non-zero | Investigate the failing command; the report's details column shows the tail of stderr |

## Dependencies

- Bean directory at `ai/beans/BEAN-NNN-<slug>/bean.md`
- `uv` available on `PATH` (used to invoke `pytest` / `ruff` for
  `test:` and `lint:` criteria)
- Python module `foundry_app.services.vdd` (the runtime executor)

## Invocation Paths

The skill can be invoked two ways from a generated project:

1. **CLI:** `uv run foundry-cli vdd <bean-id>` — wires through
   `foundry_app/cli.py` and dispatches to `foundry_app.services.vdd`.
2. **Module:** `python3 -m foundry_app.services.vdd <bean-id>` — calls
   `main()` directly. Useful when invoking from a hook or a script
   that does not have `uv` resolved yet.

Both paths accept the same `--manual` and `--repo-root` flags.

## Criterion-Prefix Convention

Authors annotate each acceptance-criterion checklist item with an
evidence-type prefix in parentheses immediately after the checkbox:

```
- [ ] (test:tests/test_foo.py::test_bar) Foo behaves correctly
- [ ] (lint:foundry_app/) Lint clean for foundry_app
- [ ] (file:ai/outputs/tech-qa/vdd-277.md) VDD report exists
- [ ] (file-contains:ai/context/vdd-policy.md::criterion-prefix) Policy mentions the prefix
- [ ] Manual: spot-check the wizard's persona-list scroll behavior
```

Backward-compatible: criteria without a prefix become `MANUAL` items.
The aggregate verdict flags them as `PARTIAL` so reviewers know human
sign-off is still required.
