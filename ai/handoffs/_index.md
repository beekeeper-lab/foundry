# Handoff Index

Every typed packet emitted by `/handoff` (see
`ai-team-library/claude/skills/handoff/SKILL.md`) is appended here. The
packet itself is stored at the path in the **Packet** column.

## Schema

| Column | Description |
|--------|-------------|
| Date | `YYYY-MM-DD` of the handoff emit |
| From | Sender persona id (e.g., `developer`) |
| To | Receiver persona id (e.g., `tech-qa`) |
| Bean | Owning bean id (e.g., `BEAN-274`) |
| Packet | Relative path to the typed packet under `ai/handoffs/` |

## Handoffs

| Date | From | To | Bean | Packet |
|------|------|----|------|--------|
| 2026-05-01 | developer | tech-qa | BEAN-274 | [developer-to-tech-qa-BEAN-274-task-02.md](developer-to-tech-qa-BEAN-274-task-02.md) |
| 2026-07-03 | developer | tech-qa | BEAN-295 | developer-to-tech-qa-BEAN-295-task-05.md |
