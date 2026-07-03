# /vdd Command

Runs the programmatic Verification-Driven Development gate for a bean.
Parses the bean's `## Acceptance Criteria` section, dispatches each
criterion's evidence type (test, lint, file, file-contains, or manual)
to the matching runner, and writes a structured pass/fail report at
`ai/outputs/tech-qa/vdd-<NNN>.md`.

## Usage

```
/vdd <bean-id> [--manual pending|pass]
```

- `bean-id` -- The bean ID to verify (e.g., `BEAN-277` or just `277`).
- `--manual pending` (default) -- Unprefixed criteria leave the verdict
  as `PARTIAL` until a human signs off.
- `--manual pass` -- Treat unprefixed criteria as passing (use only
  after Tech-QA has manually confirmed them).

Exit codes: `0` PASS, `1` FAIL/PARTIAL, `2` EMPTY (no AC), `3` usage error.

## See Also

- Skill: `claude/skills/vdd/SKILL.md` — canonical execution spec and
  the criterion-prefix convention.
- `ai/context/vdd-policy.md` — the prose VDD policy this gate enforces.
- `claude/skills/merge-bean/SKILL.md` — pre-merge VDD gate.
