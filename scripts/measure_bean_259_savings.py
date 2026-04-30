"""Measure the per-persona prompt size savings from BEAN-259 / ADR-012.

Compares two write_agents passes against the real ai-team-library:

1. **Before** — every expertise's ``applies_to`` is forced to ``[]`` so the
   filter is a pass-through (pre-BEAN-259 behavior — every persona gets every
   expertise inlined).
2. **After**  — applies_to is read from the indexer (the curated lists added
   in BEAN-259).

Reports the byte and line count for each generated agent file under both
passes and prints the percentage reduction. The acceptance target in the
bean is ≥20% reduction for at least one non-Developer persona.

Run with::

    uv run python scripts/measure_bean_259_savings.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Make `foundry_app` importable when invoked as a plain script.
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from foundry_app.core.models import (  # noqa: E402
    CompositionSpec,
    ExpertiseSelection,
    PersonaSelection,
    ProjectIdentity,
    TeamConfig,
)
from foundry_app.services.agent_writer import write_agents  # noqa: E402
from foundry_app.services.library_indexer import build_library_index  # noqa: E402

LIBRARY_ROOT = _REPO_ROOT / "ai-team-library"


def _spec() -> CompositionSpec:
    """A React + Python + TypeScript composition with a multi-discipline team
    that exercises the curated applies_to lists added in BEAN-259."""
    return CompositionSpec(
        project=ProjectIdentity(name="BEAN-259 Savings Demo", slug="bean-259-demo"),
        team=TeamConfig(personas=[
            PersonaSelection(id="developer"),
            PersonaSelection(id="tech-qa"),
            PersonaSelection(id="architect"),
            PersonaSelection(id="devops-release"),
            PersonaSelection(id="ux-ui-designer"),
            PersonaSelection(id="ba"),
            PersonaSelection(id="security-engineer"),
        ]),
        expertise=[
            ExpertiseSelection(id="python", order=10),
            ExpertiseSelection(id="typescript", order=20),
            ExpertiseSelection(id="react", order=30),
            ExpertiseSelection(id="accessibility-compliance", order=40),
        ],
    )


def _measure(out_dir: Path) -> dict[str, tuple[int, int]]:
    """Return {persona_id: (bytes, lines)} for every agent file in *out_dir*."""
    sizes: dict[str, tuple[int, int]] = {}
    for agent in sorted((out_dir / ".claude" / "agents").glob("*.md")):
        text = agent.read_text(encoding="utf-8")
        sizes[agent.stem] = (len(text), text.count("\n") + 1)
    return sizes


def main() -> int:
    spec = _spec()

    with tempfile.TemporaryDirectory() as before_root, \
         tempfile.TemporaryDirectory() as after_root:
        before_path = Path(before_root)
        after_path = Path(after_root)

        # ----- BEFORE: applies_to forced to [] on every expertise -----
        index_before = build_library_index(LIBRARY_ROOT)
        for e in index_before.expertise:
            e.applies_to = []
        write_agents(spec, index_before, LIBRARY_ROOT, before_path)
        before = _measure(before_path)

        # ----- AFTER: applies_to read from the curated library files -----
        index_after = build_library_index(LIBRARY_ROOT)
        write_agents(spec, index_after, LIBRARY_ROOT, after_path)
        after = _measure(after_path)

    print("BEAN-259 / ADR-012 — agent prompt size impact")
    print(f"Library: {LIBRARY_ROOT}")
    print(
        f"Composition: {len(spec.team.personas)} personas, "
        f"{len(spec.expertise)} expertise"
    )
    print()
    print(
        f"{'Persona':<25} {'Before B':>10} {'After B':>10} "
        f"{'Δ B':>10} {'%':>7}  | {'Before L':>9} {'After L':>9}"
    )
    print("-" * 96)

    biggest_reduction_pct = 0.0
    biggest_reduction_persona = ""
    for pid in sorted(before):
        bb, bl = before[pid]
        ab, al = after.get(pid, (0, 0))
        delta_b = bb - ab
        pct = (delta_b / bb * 100.0) if bb else 0.0
        if pct > biggest_reduction_pct and pid != "developer":
            biggest_reduction_pct = pct
            biggest_reduction_persona = pid
        print(
            f"{pid:<25} {bb:>10d} {ab:>10d} {delta_b:>10d} {pct:>6.1f}%  "
            f"| {bl:>9d} {al:>9d}",
        )

    print()
    print(
        f"Largest reduction (non-Developer): {biggest_reduction_persona} "
        f"= {biggest_reduction_pct:.1f}%"
    )
    print("Acceptance target (BEAN-259): >=20% for at least one non-Developer")
    if biggest_reduction_pct >= 20.0:
        print("RESULT: PASS")
        return 0
    print("RESULT: FAIL — no non-Developer persona reaches the 20% threshold")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
