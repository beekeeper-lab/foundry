# /pick-bean Command

Lets the Team Lead pick a bean from the backlog for decomposition and execution. Updates the bean's status from `Approved` to `In Progress` in both `bean.md` and `_index.md`, and creates the feature branch.

## Usage

```
/pick-bean <bean-id>
```

- `bean-id` -- The bean ID to pick (e.g., `BEAN-006` or just `6`).

## See Also

- Skill: `claude/skills/pick-bean/SKILL.md` — canonical execution spec.
