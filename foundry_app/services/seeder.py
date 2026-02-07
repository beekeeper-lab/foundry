"""Seed step: generate a starter task list for a new project.

Creates seeded-tasks.md with the default dependency wave
(BA -> Architect -> Dev -> Tech-QA) plus parallel lanes
(Security, DevOps, Code Quality, Docs).
"""

from __future__ import annotations

from pathlib import Path

from foundry_app.core.models import CompositionSpec, StageResult

# Maps persona IDs to their default task wave and seeded tasks
_TASK_WAVES: dict[str, list[dict[str, str]]] = {
    "ba": [
        {
            "title": "Gather and document initial requirements",
            "goal": "Produce an epic brief and initial user stories with acceptance criteria.",
            "outputs": "ai/outputs/ba/epic-brief.md, ai/outputs/ba/user-stories/",
            "dod": "- [ ] Epic brief written and reviewed\n- [ ] At least 3 user stories with acceptance criteria\n- [ ] Stories are testable and unambiguous",
            "dependencies": "None (first wave)",
        },
        {
            "title": "Review requirements for completeness",
            "goal": "Validate that stories cover the core user flows and edge cases.",
            "outputs": "ai/outputs/ba/ (updated stories)",
            "dod": "- [ ] All stories reviewed against epic brief\n- [ ] Gaps identified and filled\n- [ ] Architect has enough to begin design",
            "dependencies": "Gather and document initial requirements",
        },
    ],
    "architect": [
        {
            "title": "Define system boundaries and initial architecture",
            "goal": "Produce an ADR for the primary architecture decision and a design spec.",
            "outputs": "ai/outputs/architect/adr-001.md, ai/outputs/architect/design-spec.md",
            "dod": "- [ ] ADR documents the key architecture decision with alternatives\n- [ ] Design spec covers component boundaries and data flow\n- [ ] Naming conventions established",
            "dependencies": "BA: Gather and document initial requirements",
        },
        {
            "title": "Review architecture with team",
            "goal": "Ensure all roles understand the boundaries, contracts, and interfaces.",
            "outputs": "ai/outputs/architect/review-checklist.md",
            "dod": "- [ ] Review checklist completed\n- [ ] Feedback from Dev and Tech-QA incorporated\n- [ ] No unresolved open questions blocking implementation",
            "dependencies": "Define system boundaries and initial architecture",
        },
    ],
    "developer": [
        {
            "title": "Implement core feature scaffold",
            "goal": "Set up the application skeleton following the architecture spec.",
            "outputs": "Application code, ai/outputs/developer/implementation-notes.md",
            "dod": "- [ ] Project builds and runs locally\n- [ ] Core structure matches design spec\n- [ ] Unit tests for critical paths\n- [ ] Dev design decisions documented",
            "dependencies": "Architect: Define system boundaries and initial architecture",
        },
        {
            "title": "Implement first user story end-to-end",
            "goal": "Deliver a complete vertical slice demonstrating the architecture.",
            "outputs": "Application code, ai/outputs/developer/pr-description.md",
            "dod": "- [ ] Story acceptance criteria met\n- [ ] Tests pass (unit + integration)\n- [ ] PR description written\n- [ ] Ready for QA verification",
            "dependencies": "Implement core feature scaffold",
        },
    ],
    "tech-qa": [
        {
            "title": "Create test charter and test plan",
            "goal": "Define the testing strategy for the first delivery wave.",
            "outputs": "ai/outputs/tech-qa/test-charter.md",
            "dod": "- [ ] Test charter covers all user stories in wave 1\n- [ ] Risk-based test priority assigned\n- [ ] Test environments identified",
            "dependencies": "BA: Review requirements for completeness",
        },
        {
            "title": "Verify first user story",
            "goal": "Execute tests against the delivered story and report results.",
            "outputs": "ai/outputs/tech-qa/test-report.md",
            "dod": "- [ ] All acceptance criteria verified\n- [ ] Test report written with evidence\n- [ ] Defects filed if found (using BA bug-report template)\n- [ ] Traceability matrix updated",
            "dependencies": "Developer: Implement first user story end-to-end",
        },
    ],
    # Parallel lanes
    "security-engineer": [
        {
            "title": "Initial threat model",
            "goal": "Produce a STRIDE-based threat model for the system.",
            "outputs": "ai/outputs/security-engineer/threat-model.md",
            "dod": "- [ ] STRIDE analysis completed for all trust boundaries\n- [ ] Mitigations defined for High/Medium risks\n- [ ] Review scheduled with Architect",
            "dependencies": "Architect: Define system boundaries and initial architecture",
        },
    ],
    "devops-release": [
        {
            "title": "Set up CI/CD pipeline",
            "goal": "Create a baseline CI pipeline that builds, tests, and lints.",
            "outputs": "ai/outputs/devops-release/pipeline-yaml.md",
            "dod": "- [ ] Pipeline runs on every push\n- [ ] Build, test, and lint stages pass\n- [ ] Release runbook drafted",
            "dependencies": "Developer: Implement core feature scaffold",
        },
    ],
    "code-quality-reviewer": [
        {
            "title": "First code quality review",
            "goal": "Review the initial implementation for code quality and consistency.",
            "outputs": "ai/outputs/code-quality-reviewer/review-report.md",
            "dod": "- [ ] Review report completed\n- [ ] Ship/no-ship checklist for first delivery wave\n- [ ] Actionable feedback provided to Developer",
            "dependencies": "Developer: Implement first user story end-to-end",
        },
    ],
    "technical-writer": [
        {
            "title": "Draft project README and onboarding docs",
            "goal": "Ensure a new contributor can set up and understand the project.",
            "outputs": "README.md (enhanced), ai/outputs/technical-writer/onboarding.md",
            "dod": "- [ ] README covers setup, running, and testing\n- [ ] Architecture overview included or linked\n- [ ] Onboarding doc covers team structure and workflow",
            "dependencies": "Developer: Implement core feature scaffold",
        },
    ],
}


def seed_tasks(
    composition: CompositionSpec,
    tasks_dir: Path,
    mode: str = "detailed",
) -> StageResult:
    """Generate a seeded task list based on selected personas.

    Args:
        composition: The project composition spec.
        tasks_dir: Directory to write task files (e.g., ai/tasks/).
        mode: Seed mode — "detailed" for full wave tasks, "kickoff" for
            a single Team Lead kickoff task.

    Returns:
        A StageResult listing created files and warnings.
    """
    tasks_dir.mkdir(parents=True, exist_ok=True)
    result = StageResult()

    if mode == "kickoff":
        return _seed_kickoff(composition, tasks_dir, result)

    selected_ids = {p.id for p in composition.team.personas}
    lines: list[str] = [
        f"# Seeded Tasks: {composition.project.name}",
        "",
        "> Generated by Foundry. Edit freely — this is a starting point.",
        "",
        "## Dependency Wave",
        "",
        "```",
        "BA (requirements) → Architect (design) → Developer (implementation) → Tech-QA (verification)",
        "                                       ↘ Security (threat model)",
        "                                       ↘ DevOps (CI/CD)",
        "                   Developer done       → Code Quality Review",
        "                   Developer done       → Technical Writer (docs)",
        "```",
        "",
    ]

    task_number = 1

    # Primary wave order
    primary_wave = ["ba", "architect", "developer", "tech-qa"]
    parallel_lanes = [
        "security-engineer",
        "devops-release",
        "code-quality-reviewer",
        "technical-writer",
    ]

    all_roles = primary_wave + parallel_lanes

    for role_id in all_roles:
        if role_id not in selected_ids:
            continue
        if role_id not in _TASK_WAVES:
            continue

        role_title = role_id.replace("-", " ").title()
        lines.append(f"---\n\n## {role_title}\n")

        for task in _TASK_WAVES[role_id]:
            lines.extend([
                f"### Task {task_number}: {task['title']}",
                "",
                f"**Owner:** {role_id}",
                f"**Goal:** {task['goal']}",
                f"**Outputs:** `{task['outputs']}`",
                f"**Dependencies:** {task['dependencies']}",
                "",
                "**Definition of Done:**",
                task["dod"],
                "",
            ])
            task_number += 1

    content = "\n".join(lines)
    out_file = tasks_dir / "seeded-tasks.md"
    out_file.write_text(content)
    result.wrote.append("seeded-tasks.md")

    return result


def _seed_kickoff(
    composition: CompositionSpec,
    tasks_dir: Path,
    result: StageResult,
) -> StageResult:
    """Generate a single kickoff task for the Team Lead to decompose."""
    personas_str = ", ".join(p.id for p in composition.team.personas) or "none"
    stacks_str = ", ".join(s.id for s in composition.stacks) or "none"

    content = f"""\
# Seeded Tasks: {composition.project.name}

> Generated by Foundry (kickoff mode). The Team Lead should decompose
> the project objectives into detailed tasks using `/seed-tasks`.

## Kickoff Task

### Task 1: Decompose project objectives and seed initial tasks

**Owner:** team-lead
**Goal:** Review the project composition, understand the team structure and
tech stack, then decompose the high-level objectives into actionable tasks
for each team member.

**Team:** {personas_str}
**Stacks:** {stacks_str}

**Steps:**
1. Review `ai/team/composition.yml` and `ai/context/project.md`
2. Identify the key deliverables for each persona
3. Run `/seed-tasks` to generate the detailed task breakdown
4. Assign priorities and dependencies across the team

**Definition of Done:**
- [ ] Project objectives documented
- [ ] Tasks created for each team member
- [ ] Dependencies mapped between tasks
- [ ] Team briefed on priorities and workflow
"""
    out_file = tasks_dir / "seeded-tasks.md"
    out_file.write_text(content)
    result.wrote.append("seeded-tasks.md")
    return result
