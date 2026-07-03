# ADR-007: Planning-Only Scaffolding — Foundry Does Not Generate App Code

| Field | Value |
|-------|-------|
| **Date** | 2026-04-17 |
| **Status** | Accepted |
| **Bean** | BEAN-251, BEAN-253 |
| **Deciders** | Architect |

## Context

External audit (2026-04-17): *"No code scaffolding despite claiming React/TS. No `package.json`, `tsconfig.json`, `vite.config.ts`, `src/`, `.eslintrc`, no lockfile. A Developer cannot run anything on day 1."*

The audit is factually correct: Foundry generates the AI-team scaffold (`.claude/`, `ai/`, `CLAUDE.md`, agent/member files, starter bean, project charter) but not the application-code scaffold (`package.json`, `pyproject.toml`, `src/`, `tsconfig.json`, lockfiles, etc.). A persona opening the generated project cannot run `npm test` or `uv run pytest` until a human initializes the app.

The audit frames this as a bug. We frame it as a scope question: *should* Foundry scaffold app code, and if so, how far should that scope extend? Three stances were considered.

1. **Planning-only** — Foundry scaffolds the AI-team context only; the user initializes their app with the stack-appropriate command (`npm create vite@latest`, `uv init`, `cargo new`, …).
2. **Minimal stub per stack** — Foundry emits a tiny stack-specific skeleton (e.g. `package.json` + `src/index.ts` for React/TS, `pyproject.toml` + module dir for Python) alongside the AI-team scaffold.
3. **Delegate to ecosystem tools** — Foundry shells out to `cookiecutter` / `npm create` / `yo` / … at generation time.

## Decision

**Stance 1 — Planning-only.** Foundry does not scaffold stack-specific app code. The generated `CLAUDE.md` includes a Scope section stating this explicitly; the generated `README.md` points users at `docs/starter-stacks.md` in the Foundry repo, a cheat sheet of canonical init commands per supported expertise. Paired with ADR-relevant work in BEAN-251 (narrow `Edit(ai/**)` permission model), the two decisions produce a single coherent posture: *Foundry manages planning artifacts under `ai/`; humans initialize and implement the app.*

## Consequences

**Positive:**
- Foundry stays small and focused. The unique contribution is the AI team, not a competing starter-template generator.
- Dodges the stack-template treadmill: React/Vite/Next/Vue/Python/Rust/Go each evolve their own canonical generators on their own cadence. Bundling scaffolders means inheriting every one of those churns indefinitely.
- Aligns with the permission model already shipped: the generated `settings.local.json` grants `Edit(ai/**)` only, which is exactly right for a Planning-only scope.
- The reversal direction is cheap: any future bean can add Stance 2 or 3 on top of the existing core without breaking any project generated under Stance 1. Generated output is a strict subset of any future expansion.

**Negative:**
- Day-1 gap: the generated project has no `package.json` or `pyproject.toml`, so a persona cannot "run the app" until a human runs one init command. Mitigated by `docs/starter-stacks.md` and by the README's Getting Started pointer.
- Personas that expect stack-specific files (a test harness, a lint config) must degrade gracefully until the human initializes the app. Expected — this is part of what "Planning-only" means.

## Reversibility

The two directions are asymmetric and this decision chooses the reversible one:

- **Planning-only → scaffolders (reversible).** Any future bean can add stack-specific generation on top of the current core. No existing generated project breaks because the current output is a strict subset of what an expanded Foundry would produce.
- **Scaffolders → Planning-only (irreversible in practice).** Once Foundry ships a `package.json` generator and users depend on it, removing it later deprecates every project that relied on the shipped stub. Either users keep the stale stub or migrate off it — both are support burden.

Choose the reversible direction. The audit's complaint is real, but it does not force scaffolders; it forces *explicitness* about the scope. That is what this ADR and its paired generator changes provide.

## Alternatives Rejected

1. **Stance 2 — Minimal stub per stack:** Rejected. A true minimum-viable stub for a modern stack is never one file (React/TS alone needs `package.json` + `tsconfig.json` + `vite.config.ts` + `index.html` + `src/main.tsx` to boot). Shipping stubs commits Foundry to tracking upstream format changes forever. Once shipped, users depend on the stubs, and removing them later is a breaking change. The surface Foundry would take on is not justified by the audit's complaint.
2. **Stance 3 — Delegate to ecosystem tools:** Rejected. Adds runtime dependencies Foundry does not otherwise need (Node, `cookiecutter`, `yo`). Introduces a new configuration surface in the composition spec (which ecosystem tool per expertise?). Error paths multiply (missing PATH entries, upstream tool version skew). Still coupled to upstream template drift — just laundered through another layer.
3. **Add `spec.generation.scaffold_app_code` toggle:** Rejected. A toggle implies both modes are supported; supporting both means Foundry owns both, which defeats the point of this ADR. A toggle is a commitment, not a hedge.
4. **Retrofit existing generated projects:** Out of scope. This ADR governs new generations; existing projects in the wild are unaffected.

