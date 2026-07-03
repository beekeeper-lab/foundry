# MEMORY — Durable Lessons

Curated, small, and load-bearing: one line per lesson, appended by the
bean-closure retro step (see `/close-loop`). When a lesson implicates a
persona, expertise pack, or kit asset, also draft an improvement bean.
Delete entries that stop being true.

## Process

- Honor-system gates get skipped at scale: across 294 beans, /handoff fired once and /vdd three times until the VDD gate became a PreToolUse hook (2026-07 audit, SPEC-008). Prefer hooks over prose for anything that must happen.
- Telemetry that is never aggregated silently corrupts: the branch-age Duration bug survived 60+ beans because nothing consumed the numbers (SPEC-005/009). Run `/orchestration-report` on cadence.
- Telemetry blocks carrying template defaults (all zeros, in-process) are copy-pasted, not measured — the 2026-07 baseline found 9 of 10 such blocks.

## Personas

- (none yet)

## Expertise

- Pack content only reaches prompts through the compiler's entry-file contract; 19 of 42 packs were silently inert for months because they lacked conventions.md (SPEC-003). Validate reachability when authoring packs.

## Kit

- Assets without YAML frontmatter are invisible to Claude Code discovery — 157 kit/library files were prose, not registrable artifacts, until SPEC-002.
- Whole-file local overrides permanently fork from upstream; prefer the kit-contribute.sh patch-upstream flow (ADR-016).
