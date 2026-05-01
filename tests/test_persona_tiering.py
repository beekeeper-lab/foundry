"""Tier-coverage tests for the BEAN-271 persona tiering reorg (ADR-014).

These tests lock in the contract introduced by BEAN-271:

* ``_scan_personas`` walks ``personas/core/`` and ``personas/extended/`` in
  that order and tags each ``PersonaInfo`` with ``tier="core"`` or
  ``tier="extended"`` (with the ``extended/`` prefix on the canonical id).
* A composition that supplies an empty ``team.personas`` block defaults to
  exactly the library's core tier.
* A composition referencing an extended persona via the ADR-014 syntax
  (``extended/<name>``) compiles successfully and the persona appears in
  the output.
* Unknown and wrong-tier persona references surface the verbatim ADR-014
  error messages.
* When either tier directory is missing, the indexer logs a warning and
  treats the tier as empty rather than crashing — matching the existing
  graceful-degradation behaviour for a missing top-level ``personas/`` dir.

The contract these tests defend is "default = core only; extended = explicit
opt-in." If a future change weakens that contract, these tests should fail
loudly.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from foundry_app.core.models import (
    CompositionSpec,
    ExpertiseSelection,
    LibraryIndex,
    PersonaSelection,
    ProjectIdentity,
    TeamConfig,
)
from foundry_app.io.composition_io import load_composition
from foundry_app.services.compiler import compile_project
from foundry_app.services.generator import _apply_default_team, generate_project
from foundry_app.services.library_indexer import (
    _scan_personas,
    build_library_index,
    format_unknown_persona_error,
)
from foundry_app.services.validator import run_pre_generation_validation

REPO_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_ROOT = REPO_ROOT / "ai-team-library"

# Closed core set per ADR-014. If this list ever needs to change the bean
# requires a new ADR — these names are the wire format, not implementation
# detail.
CORE_PERSONA_IDS = frozenset(
    {"architect", "ba", "developer", "team-lead", "tech-qa"}
)


# ---------------------------------------------------------------------------
# Test 1 — _scan_personas reports the right tier for every real persona
# ---------------------------------------------------------------------------


class TestScanPersonasTier:
    """End-to-end coverage of the indexer's tier behaviour against the real
    library. The two on-disk subdirectories must yield exactly the expected
    counts and the ``PersonaInfo.tier`` field must match the source dir."""

    def test_scans_real_library_into_two_tiers(self):
        personas = _scan_personas(LIBRARY_ROOT / "personas", set())
        core = [p for p in personas if p.tier == "core"]
        extended = [p for p in personas if p.tier == "extended"]
        assert len(core) == 5, (
            f"core tier must contain exactly 5 personas; got {len(core)}: "
            f"{sorted(p.id for p in core)}"
        )
        assert len(extended) == 19, (
            f"extended tier must contain exactly 19 personas; got "
            f"{len(extended)}: {sorted(p.id for p in extended)}"
        )

    def test_core_personas_have_core_tier_and_bare_id(self):
        personas = _scan_personas(LIBRARY_ROOT / "personas", set())
        core_ids = {p.id for p in personas if p.tier == "core"}
        assert core_ids == CORE_PERSONA_IDS, (
            "core/<id> directories must produce bare ids matching the "
            "closed core set"
        )

    def test_extended_personas_have_extended_tier_and_prefixed_id(self):
        personas = _scan_personas(LIBRARY_ROOT / "personas", set())
        for persona in personas:
            if persona.tier != "extended":
                continue
            assert persona.id.startswith("extended/"), (
                f"extended persona {persona.id!r} must carry the "
                f"'extended/' prefix per ADR-014"
            )

    def test_no_persona_appears_in_both_tiers(self):
        personas = _scan_personas(LIBRARY_ROOT / "personas", set())
        leafs_by_tier = {"core": set(), "extended": set()}
        for persona in personas:
            leaf = (
                persona.id.split("/", 1)[1]
                if persona.id.startswith("extended/")
                else persona.id
            )
            leafs_by_tier[persona.tier].add(leaf)
        overlap = leafs_by_tier["core"] & leafs_by_tier["extended"]
        assert overlap == set(), (
            f"Persona leaf names must not appear in both tiers; collision: "
            f"{sorted(overlap)}"
        )


# ---------------------------------------------------------------------------
# Test 2 — Default composition (no `personas:` block) → core tier only
# ---------------------------------------------------------------------------


class TestDefaultCompositionResolvesCoreTier:
    """``_apply_default_team`` is the single hook ADR-014 wires for the
    "default = core" contract. The integration test goes one step further
    and runs the whole pipeline to make sure the rest of the stack honours
    the populated team."""

    def test_apply_default_team_fills_with_real_core_personas(self):
        # Empty team.personas → expect every core persona to be selected.
        spec = CompositionSpec(
            project=ProjectIdentity(name="Default Team", slug="default-team"),
            team=TeamConfig(personas=[]),
        )
        library = build_library_index(LIBRARY_ROOT)
        _apply_default_team(spec, library)
        selected_ids = sorted(p.id for p in spec.team.personas)
        assert selected_ids == sorted(CORE_PERSONA_IDS), (
            "Empty personas list must inherit exactly the library's core "
            "tier (ADR-014). Selected: " + repr(selected_ids)
        )

    def test_apply_default_team_does_not_touch_explicit_selection(self):
        # An explicit selection must short-circuit the default-team hook.
        spec = CompositionSpec(
            project=ProjectIdentity(name="Explicit", slug="explicit"),
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
        )
        library = build_library_index(LIBRARY_ROOT)
        _apply_default_team(spec, library)
        assert [p.id for p in spec.team.personas] == ["developer"], (
            "Explicit selection must not be overridden by the default-team "
            "hook"
        )

    def test_default_composition_compiles_to_core_team_only(
        self, tmp_path: Path,
    ):
        # End-to-end: a composition with no personas block goes through the
        # whole pipeline and the only agent files emitted are the core five.
        spec = CompositionSpec(
            project=ProjectIdentity(name="Default Team", slug="default-team"),
            team=TeamConfig(personas=[]),
        )
        manifest, validation, _ = generate_project(
            spec, LIBRARY_ROOT, output_root=tmp_path / "out",
        )
        assert validation.is_valid, (
            f"default-team composition must validate; errors: "
            f"{[m.message for m in validation.errors]}"
        )
        agents = sorted(
            f.stem for f in (tmp_path / "out" / ".claude" / "agents").glob("*.md")
        )
        assert agents == sorted(CORE_PERSONA_IDS), (
            f"default composition must emit exactly the 5 core agent files; "
            f"got {agents}"
        )


# ---------------------------------------------------------------------------
# Test 3 — Composition with an extended persona compiles successfully
# ---------------------------------------------------------------------------


class TestExtendedPersonaReferenceCompiles:
    """Spec referencing ``extended/<name>`` per ADR-014 must compile and
    write the persona's member file alongside the core team."""

    def test_extended_persona_appears_in_compile_output(
        self, tmp_path: Path,
    ):
        # Include the full core team so BEAN-274's contract-graph
        # validator is satisfied; the test's intent is "extended persona
        # is resolved + emitted alongside core", not "minimal team".
        spec = CompositionSpec(
            project=ProjectIdentity(name="Mixed", slug="mixed"),
            expertise=[ExpertiseSelection(id="python", order=10)],
            team=TeamConfig(personas=[
                PersonaSelection(id="team-lead"),
                PersonaSelection(id="ba"),
                PersonaSelection(id="architect"),
                PersonaSelection(id="developer"),
                PersonaSelection(id="tech-qa"),
                PersonaSelection(id="extended/security-engineer"),
            ]),
        )
        manifest, validation, _ = generate_project(
            spec, LIBRARY_ROOT, output_root=tmp_path / "out",
        )
        assert validation.is_valid, (
            f"extended-persona composition must validate; errors: "
            f"{[m.message for m in validation.errors]}"
        )
        # The on-disk leaf name strips the ``extended/`` prefix (ADR-014).
        member = (
            tmp_path / "out" / "ai" / "generated" / "members"
            / "security-engineer.md"
        )
        assert member.is_file(), (
            "Extended persona member file must be written to "
            "ai/generated/members/<leaf>.md"
        )
        agent = tmp_path / "out" / ".claude" / "agents" / "security-engineer.md"
        assert agent.is_file(), (
            "Extended persona agent file must be written to "
            ".claude/agents/<leaf>.md"
        )

    def test_real_examples_with_extended_personas_load_and_validate(self):
        # Sanity check: every ADR-014-migrated example yml resolves cleanly.
        library = build_library_index(LIBRARY_ROOT)
        for name in (
            "small-python-team.yml",
            "foundry-dogfood.yml",
            "full-stack-web.yml",
            "security-focused.yml",
        ):
            path = REPO_ROOT / "examples" / name
            spec = load_composition(path)
            _apply_default_team(spec, library)
            result = run_pre_generation_validation(spec, library)
            assert result.is_valid, (
                f"{name} must validate against the post-reorg library; "
                f"errors: {[m.message for m in result.errors]}"
            )


# ---------------------------------------------------------------------------
# Test 4 — Unknown / wrong-tier references emit the ADR-014 error verbatim
# ---------------------------------------------------------------------------


class TestUnknownAndWrongTierErrorMessages:
    """The error strings in ADR-014 are the user-facing contract for the
    migration. These tests bind both the format and the wording so a future
    refactor can't quietly soften the diagnostic."""

    def test_unknown_persona_message_lists_both_tiers(self):
        library = build_library_index(LIBRARY_ROOT)
        msg = format_unknown_persona_error("totally-bogus", library)
        # Verbatim opening per ADR-014.
        assert msg.startswith(
            "Unknown persona 'totally-bogus' in composition.yml. "
        )
        # Both tier listings appear, exact labels per ADR-014.
        assert "Core personas (bare names): " in msg
        assert "Extended personas (tier-prefixed): " in msg
        # Live core ids round-trip into the message (proves it's not a
        # hard-coded list that drifts).
        for core_id in CORE_PERSONA_IDS:
            assert core_id in msg
        # Extended ids appear with the prefix.
        assert "extended/security-engineer" in msg

    def test_wrong_tier_bare_extended_name_suggests_prefixed_form(self):
        library = build_library_index(LIBRARY_ROOT)
        msg = format_unknown_persona_error("security-engineer", library)
        # Verbatim wording from ADR-014 § Loader behavior #5.
        assert msg == (
            "Persona 'security-engineer' not found at expected tier. "
            "Did you mean 'extended/security-engineer'? Extended personas "
            "must be referenced as 'extended/<name>'; core personas use "
            "the bare name."
        )

    def test_wrong_tier_prefixed_core_name_suggests_bare_form(self):
        library = build_library_index(LIBRARY_ROOT)
        msg = format_unknown_persona_error("extended/developer", library)
        # Verbatim wording from ADR-014 § Loader behavior #5.
        assert msg == (
            "Persona 'extended/developer' not found at expected tier. "
            "Did you mean 'developer'? Extended personas must be "
            "referenced as 'extended/<name>'; core personas use the "
            "bare name."
        )

    def test_validator_emits_unknown_persona_error_with_adr014_message(self):
        library = build_library_index(LIBRARY_ROOT)
        spec = CompositionSpec(
            project=ProjectIdentity(name="Bad", slug="bad"),
            team=TeamConfig(personas=[PersonaSelection(id="totally-bogus")]),
        )
        result = run_pre_generation_validation(spec, library)
        assert not result.is_valid
        assert len(result.errors) == 1
        err = result.errors[0]
        assert err.code == "missing-persona"
        assert err.message.startswith(
            "Unknown persona 'totally-bogus' in composition.yml. "
        )

    def test_validator_emits_wrong_tier_error_with_adr014_message(self):
        library = build_library_index(LIBRARY_ROOT)
        spec = CompositionSpec(
            project=ProjectIdentity(name="Bad Tier", slug="bad-tier"),
            team=TeamConfig(personas=[PersonaSelection(id="security-engineer")]),
        )
        result = run_pre_generation_validation(spec, library)
        assert not result.is_valid
        assert any(
            "not found at expected tier" in m.message
            and "extended/security-engineer" in m.message
            for m in result.errors
        )

    def test_compiler_warning_uses_same_adr014_message(self, tmp_path: Path):
        # The compile path also surfaces the ADR-014 message — same source
        # of truth, different code path. Asserting both keeps any future
        # divergence loud.
        library = build_library_index(LIBRARY_ROOT)
        spec = CompositionSpec(
            project=ProjectIdentity(name="Bad", slug="bad"),
            team=TeamConfig(personas=[PersonaSelection(id="totally-bogus")]),
        )
        result = compile_project(spec, library, LIBRARY_ROOT, tmp_path / "out")
        assert any(
            w.startswith("Unknown persona 'totally-bogus' in composition.yml. ")
            for w in result.warnings
        ), f"compile warnings: {result.warnings}"


# ---------------------------------------------------------------------------
# Test 5 — Missing tier dirs degrade gracefully (warn, don't crash)
# ---------------------------------------------------------------------------


class TestMissingTierDirsGraceful:
    """ADR-014 § Loader behaviour requires that a missing tier directory be
    treated as an empty tier and surface a warning, mirroring the historic
    "personas/ directory missing" behaviour. These tests run against a
    synthetic library so the real one stays untouched."""

    def test_missing_core_tier_treated_as_empty(
        self, tmp_path: Path, caplog,
    ):
        # Only the extended tier exists.
        (tmp_path / "personas" / "extended" / "lone").mkdir(parents=True)
        (tmp_path / "personas" / "extended" / "lone" / "persona.md").write_text(
            "# Lone\n"
        )
        with caplog.at_level(logging.WARNING):
            personas = _scan_personas(tmp_path / "personas", set())
        ids = [p.id for p in personas]
        assert ids == ["extended/lone"], (
            "Missing core tier must not block extended-tier discovery"
        )
        assert any(
            "core" in record.getMessage()
            and "tier directory not found" in record.getMessage().lower()
            for record in caplog.records
        ), "Missing core tier must emit a warning"

    def test_missing_extended_tier_treated_as_empty(
        self, tmp_path: Path, caplog,
    ):
        # Only the core tier exists.
        (tmp_path / "personas" / "core" / "dev").mkdir(parents=True)
        (tmp_path / "personas" / "core" / "dev" / "persona.md").write_text(
            "# Dev\n"
        )
        with caplog.at_level(logging.WARNING):
            personas = _scan_personas(tmp_path / "personas", set())
        ids = [p.id for p in personas]
        assert ids == ["dev"], (
            "Missing extended tier must not block core-tier discovery"
        )
        assert any(
            "extended" in record.getMessage()
            and "tier directory not found" in record.getMessage().lower()
            for record in caplog.records
        ), "Missing extended tier must emit a warning"

    def test_both_tiers_missing_returns_empty_list_no_crash(
        self, tmp_path: Path, caplog,
    ):
        # personas/ exists but is empty (no tier dirs at all).
        (tmp_path / "personas").mkdir()
        with caplog.at_level(logging.WARNING):
            personas = _scan_personas(tmp_path / "personas", set())
        assert personas == []
        # Both tier directories should be flagged.
        msgs = [r.getMessage().lower() for r in caplog.records]
        assert any(
            "core" in m and "tier directory not found" in m for m in msgs
        )
        assert any(
            "extended" in m and "tier directory not found" in m for m in msgs
        )

    def test_top_level_personas_dir_missing_falls_back_to_existing_path(
        self, tmp_path: Path,
    ):
        # Pre-existing graceful-degradation contract: a missing personas/
        # at the top level is logged and yields an empty list. ADR-014 must
        # preserve this behaviour.
        personas = _scan_personas(tmp_path / "no-personas-here", set())
        assert personas == []


# ---------------------------------------------------------------------------
# Test 6 — Wizard tier groups smoke check (skipped if persona_page changes)
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("qapp")
class TestWizardTierGroupsRender:
    """Smoke check: the persona_page wizard groups by tier (ADR-014). Both
    tier sections must render when the library has personas in both."""

    def test_both_tier_sections_render(self):
        # Uses the session-scoped qapp fixture from tests/conftest.py.
        from foundry_app.core.models import PersonaInfo
        from foundry_app.ui.screens.builder.wizard_pages.persona_page import (
            PersonaSelectionPage,
        )

        lib = LibraryIndex(
            library_root="/fake",
            personas=[
                PersonaInfo(
                    id="developer",
                    path="/fake/personas/core/developer",
                    tier="core",
                    has_persona_md=True,
                ),
                PersonaInfo(
                    id="extended/security-engineer",
                    path="/fake/personas/extended/security-engineer",
                    tier="extended",
                    has_persona_md=True,
                ),
            ],
        )
        page = PersonaSelectionPage(library_index=lib)
        try:
            groups = page.tier_groups
            assert "core" in groups, "core tier section must render"
            assert "extended" in groups, "extended tier section must render"
            assert "Core team" in groups["core"].title()
            assert "Extended specialists" in groups["extended"].title()
        finally:
            page.close()
