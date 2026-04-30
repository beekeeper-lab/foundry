# /build-traceability Command

Builds a requirements-to-tests traceability matrix. Maps every acceptance criterion to the test cases that verify it, computes coverage, and identifies gaps and orphan tests.

## Usage

```
/build-traceability [--stories <dir>] [--tests <dir>] [--update <path>] [--output <path>] [--format <table|list>]
```

- `--stories <dir>` -- Stories directory (default: `ai/outputs/ba/user-stories/`).
- `--tests <dir>` -- Tests directory (default: `ai/outputs/tech-qa/`).
- `--update <path>` -- Update an existing matrix incrementally.
- `--output <path>` -- Override the output file path.
- `--format <table|list>` -- `table` for small sets, `list` for large sets. Default `table`.

## See Also

- Skill: `claude/skills/build-traceability/SKILL.md` — canonical execution spec.
