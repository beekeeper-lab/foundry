"""Tests for foundry_app.services.validator — pre-generation validation."""

from foundry_app.core.models import (
    CompositionSpec,
    ExpertiseInfo,
    ExpertiseSelection,
    HookPackInfo,
    HookPackSelection,
    HooksConfig,
    LibraryIndex,
    PersonaInfo,
    PersonaSelection,
    Posture,
    ProjectIdentity,
    Severity,
    Strictness,
    TeamConfig,
    ValidationResult,
)
from foundry_app.services.validator import (
    run_pre_generation_validation,
    validate_contract_graph,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_library(**kwargs) -> LibraryIndex:
    """Build a LibraryIndex with sensible defaults."""
    defaults = dict(
        library_root="/fake/library",
        personas=[
            PersonaInfo(id="developer", path="/fake/library/personas/developer",
                        has_persona_md=True, has_outputs_md=True, has_prompts_md=True,
                        templates=["task.md"]),
            PersonaInfo(id="architect", path="/fake/library/personas/architect",
                        has_persona_md=True),
            PersonaInfo(id="tech-qa", path="/fake/library/personas/tech-qa",
                        has_persona_md=True),
        ],
        expertise=[
            ExpertiseInfo(id="python", path="/fake/library/stacks/python",
                      files=["conventions.md", "tools.md", "patterns.md"]),
            ExpertiseInfo(id="react", path="/fake/library/stacks/react",
                      files=["conventions.md"]),
        ],
        hook_packs=[
            HookPackInfo(id="pre-commit-lint", path="/fake/library/claude/hooks/pre-commit-lint.md",
                         files=["pre-commit-lint.md"]),
            HookPackInfo(id="security-scan", path="/fake/library/claude/hooks/security-scan.md",
                         files=["security-scan.md"]),
        ],
    )
    defaults.update(kwargs)
    return LibraryIndex(**defaults)


def _make_spec(**kwargs) -> CompositionSpec:
    """Build a CompositionSpec with sensible defaults."""
    defaults = dict(
        project=ProjectIdentity(name="Test Project", slug="test-project"),
        expertise=[ExpertiseSelection(id="python")],
        team=TeamConfig(personas=[PersonaSelection(id="developer")]),
    )
    defaults.update(kwargs)
    return CompositionSpec(**defaults)


# ---------------------------------------------------------------------------
# Valid composition — no issues expected
# ---------------------------------------------------------------------------


class TestValidComposition:

    def test_valid_spec_passes(self):
        result = run_pre_generation_validation(_make_spec(), _make_library())
        assert result.is_valid
        assert result.errors == []

    def test_valid_spec_with_multiple_personas_and_expertise(self):
        spec = _make_spec(
            expertise=[ExpertiseSelection(id="python"), ExpertiseSelection(id="react")],
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
            ]),
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert result.is_valid

    def test_valid_spec_with_hook_packs(self):
        spec = _make_spec(
            hooks=HooksConfig(packs=[HookPackSelection(id="pre-commit-lint")]),
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert result.is_valid


# ---------------------------------------------------------------------------
# Missing references — errors expected
# ---------------------------------------------------------------------------


class TestMissingReferences:

    def test_missing_persona_is_error(self):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="nonexistent")]),
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "missing-persona"
        assert "nonexistent" in result.errors[0].message

    def test_missing_expertise_is_error(self):
        spec = _make_spec(expertise=[ExpertiseSelection(id="cobol")])
        result = run_pre_generation_validation(spec, _make_library())
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "missing-expertise"
        assert "cobol" in result.errors[0].message

    def test_missing_hook_pack_is_error(self):
        spec = _make_spec(
            hooks=HooksConfig(packs=[HookPackSelection(id="nonexistent-hook")]),
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert not result.is_valid
        assert result.errors[0].code == "missing-hook-pack"

    def test_multiple_missing_references(self):
        spec = _make_spec(
            expertise=[ExpertiseSelection(id="cobol")],
            team=TeamConfig(personas=[PersonaSelection(id="nonexistent")]),
            hooks=HooksConfig(packs=[HookPackSelection(id="bad-hook")]),
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert not result.is_valid
        error_codes = {e.code for e in result.errors}
        assert "missing-persona" in error_codes
        assert "missing-expertise" in error_codes
        assert "missing-hook-pack" in error_codes


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


class TestWarnings:

    def test_no_personas_is_warning(self):
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = run_pre_generation_validation(spec, _make_library())
        assert result.is_valid  # warnings don't block
        assert any(m.code == "no-personas" for m in result.warnings)

    def test_persona_without_persona_md_is_warning(self):
        library = _make_library(personas=[
            PersonaInfo(id="bare", path="/fake/library/personas/bare",
                        has_persona_md=False),
        ])
        spec = _make_spec(team=TeamConfig(personas=[PersonaSelection(id="bare")]))
        result = run_pre_generation_validation(spec, library)
        assert result.is_valid
        assert any(m.code == "persona-no-persona-md" for m in result.warnings)

    def test_expertise_with_no_files_is_warning(self):
        library = _make_library(expertise=[
            ExpertiseInfo(id="empty-stack", path="/fake/library/stacks/empty-stack", files=[]),
        ])
        spec = _make_spec(expertise=[ExpertiseSelection(id="empty-stack")])
        result = run_pre_generation_validation(spec, library)
        assert result.is_valid
        assert any(m.code == "expertise-no-files" for m in result.warnings)

    def test_duplicate_persona_is_warning(self):
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="developer"),
            ]),
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert result.is_valid
        assert any(m.code == "duplicate-persona" for m in result.warnings)

    def test_duplicate_expertise_is_warning(self):
        spec = _make_spec(
            expertise=[ExpertiseSelection(id="python"), ExpertiseSelection(id="python")],
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert result.is_valid
        assert any(m.code == "duplicate-expertise" for m in result.warnings)


# ---------------------------------------------------------------------------
# Info messages
# ---------------------------------------------------------------------------


class TestInfoMessages:

    def test_no_expertise_is_info(self):
        spec = _make_spec(expertise=[])
        result = run_pre_generation_validation(spec, _make_library())
        assert result.is_valid
        assert any(m.code == "no-expertise" for m in result.infos)


# ---------------------------------------------------------------------------
# Strictness levels
# ---------------------------------------------------------------------------


class TestStrictnessLight:

    def test_warnings_become_info_in_light_mode(self):
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = run_pre_generation_validation(
            spec, _make_library(), strictness=Strictness.LIGHT,
        )
        assert result.is_valid
        assert result.warnings == []
        # "no-personas" should now be info, not warning
        assert any(m.code == "no-personas" for m in result.infos)

    def test_errors_remain_errors_in_light_mode(self):
        spec = _make_spec(team=TeamConfig(personas=[PersonaSelection(id="missing")]))
        result = run_pre_generation_validation(
            spec, _make_library(), strictness=Strictness.LIGHT,
        )
        assert not result.is_valid
        assert result.errors[0].code == "missing-persona"


class TestStrictnessStandard:

    def test_standard_is_default(self):
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = run_pre_generation_validation(spec, _make_library())
        assert any(m.severity == Severity.WARNING for m in result.messages)

    def test_standard_keeps_warnings_as_warnings(self):
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = run_pre_generation_validation(
            spec, _make_library(), strictness=Strictness.STANDARD,
        )
        assert any(m.code == "no-personas" and m.severity == Severity.WARNING
                    for m in result.messages)


class TestStrictnessStrict:

    def test_warnings_become_errors_in_strict_mode(self):
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = run_pre_generation_validation(
            spec, _make_library(), strictness=Strictness.STRICT,
        )
        assert not result.is_valid
        assert any(m.code == "no-personas" for m in result.errors)
        assert result.warnings == []

    def test_info_stays_info_in_strict_mode(self):
        spec = _make_spec(expertise=[])
        result = run_pre_generation_validation(
            spec, _make_library(), strictness=Strictness.STRICT,
        )
        assert any(m.code == "no-expertise" and m.severity == Severity.INFO
                    for m in result.messages)


# ---------------------------------------------------------------------------
# ValidationResult model
# ---------------------------------------------------------------------------


class TestValidationResultModel:

    def test_empty_result_is_valid(self):
        result = ValidationResult()
        assert result.is_valid
        assert result.errors == []
        assert result.warnings == []
        assert result.infos == []

    def test_result_categorizes_messages(self):
        from foundry_app.core.models import ValidationMessage
        result = ValidationResult(messages=[
            ValidationMessage(severity=Severity.ERROR, code="e1", message="err"),
            ValidationMessage(severity=Severity.WARNING, code="w1", message="warn"),
            ValidationMessage(severity=Severity.INFO, code="i1", message="info"),
        ])
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert len(result.infos) == 1
        assert not result.is_valid


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:

    def test_empty_library_all_references_fail(self):
        library = LibraryIndex(library_root="/empty")
        spec = _make_spec(
            expertise=[ExpertiseSelection(id="python")],
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
            hooks=HooksConfig(packs=[HookPackSelection(id="pre-commit-lint")]),
        )
        result = run_pre_generation_validation(spec, library)
        assert not result.is_valid
        assert len(result.errors) == 3

    def test_minimal_spec_no_team_no_expertise(self):
        spec = _make_spec(expertise=[], team=TeamConfig(personas=[]))
        result = run_pre_generation_validation(spec, _make_library())
        assert result.is_valid
        # Should have info about no expertise and warning about no personas
        codes = {m.code for m in result.messages}
        assert "no-expertise" in codes
        assert "no-personas" in codes

    def test_mixed_valid_and_invalid_personas(self):
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="nonexistent"),
            ]),
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "missing-persona"


# ---------------------------------------------------------------------------
# Hook pack conflict detection (BEAN-262)
# ---------------------------------------------------------------------------


def _library_with_az_pair() -> LibraryIndex:
    """Library index where az-read-only and az-limited-ops declare mutual conflicts."""
    return LibraryIndex(
        library_root="/fake/library",
        personas=[
            PersonaInfo(id="developer", path="/fake/library/personas/developer",
                        has_persona_md=True),
        ],
        expertise=[
            ExpertiseInfo(id="python", path="/fake/library/stacks/python",
                          files=["conventions.md"]),
        ],
        hook_packs=[
            HookPackInfo(
                id="az-read-only",
                path="/fake/library/claude/hooks/az-read-only.md",
                files=["az-read-only.md"],
                conflicts_with=["az-limited-ops"],
            ),
            HookPackInfo(
                id="az-limited-ops",
                path="/fake/library/claude/hooks/az-limited-ops.md",
                files=["az-limited-ops.md"],
                conflicts_with=["az-read-only"],
            ),
            HookPackInfo(
                id="pre-commit-lint",
                path="/fake/library/claude/hooks/pre-commit-lint.md",
                files=["pre-commit-lint.md"],
            ),
        ],
    )


class TestHookPackConflictDetection:

    def test_az_pair_fails_validation(self):
        spec = _make_spec(hooks=HooksConfig(packs=[
            HookPackSelection(id="az-read-only"),
            HookPackSelection(id="az-limited-ops"),
        ]))
        result = run_pre_generation_validation(spec, _library_with_az_pair())
        assert not result.is_valid
        conflict_errors = [m for m in result.errors if m.code == "hook-pack-conflict"]
        assert len(conflict_errors) == 1
        msg = conflict_errors[0].message
        assert "az-limited-ops" in msg
        assert "az-read-only" in msg
        assert "mutually exclusive" in msg

    def test_single_pack_from_conflicting_pair_passes(self):
        spec = _make_spec(hooks=HooksConfig(packs=[
            HookPackSelection(id="az-limited-ops"),
        ]))
        result = run_pre_generation_validation(spec, _library_with_az_pair())
        assert not any(m.code == "hook-pack-conflict" for m in result.messages)

    def test_non_conflicting_pair_passes(self):
        spec = _make_spec(hooks=HooksConfig(packs=[
            HookPackSelection(id="az-limited-ops"),
            HookPackSelection(id="pre-commit-lint"),
        ]))
        result = run_pre_generation_validation(spec, _library_with_az_pair())
        assert not any(m.code == "hook-pack-conflict" for m in result.messages)

    def test_one_sided_declaration_still_detected(self):
        lib = LibraryIndex(
            library_root="/fake/library",
            personas=[PersonaInfo(id="developer",
                                  path="/fake/library/personas/developer",
                                  has_persona_md=True)],
            expertise=[ExpertiseInfo(id="python",
                                     path="/fake/library/stacks/python",
                                     files=["conventions.md"])],
            hook_packs=[
                HookPackInfo(
                    id="az-read-only",
                    path="/fake/library/claude/hooks/az-read-only.md",
                    files=["az-read-only.md"],
                    conflicts_with=["az-limited-ops"],
                ),
                HookPackInfo(
                    id="az-limited-ops",
                    path="/fake/library/claude/hooks/az-limited-ops.md",
                    files=["az-limited-ops.md"],
                    conflicts_with=[],
                ),
            ],
        )
        spec = _make_spec(hooks=HooksConfig(packs=[
            HookPackSelection(id="az-read-only"),
            HookPackSelection(id="az-limited-ops"),
        ]))
        result = run_pre_generation_validation(spec, lib)
        assert any(m.code == "hook-pack-conflict" for m in result.errors)

    def test_disabled_pack_not_counted_as_conflict(self):
        spec = _make_spec(hooks=HooksConfig(packs=[
            HookPackSelection(id="az-read-only"),
            HookPackSelection(id="az-limited-ops", enabled=False),
        ]))
        result = run_pre_generation_validation(spec, _library_with_az_pair())
        assert not any(m.code == "hook-pack-conflict" for m in result.messages)

    def test_conflict_reported_once_per_pair(self):
        spec = _make_spec(hooks=HooksConfig(packs=[
            HookPackSelection(id="az-read-only"),
            HookPackSelection(id="az-limited-ops"),
        ]))
        result = run_pre_generation_validation(spec, _library_with_az_pair())
        conflict_errors = [m for m in result.errors if m.code == "hook-pack-conflict"]
        assert len(conflict_errors) == 1


# ---------------------------------------------------------------------------
# Hook pack posture compatibility (BEAN-263)
# ---------------------------------------------------------------------------


def _library_with_compliance_gate() -> LibraryIndex:
    """Library where compliance-gate declares baseline/hardened as excluded."""
    return LibraryIndex(
        library_root="/fake/library",
        personas=[PersonaInfo(id="developer",
                              path="/fake/library/personas/developer",
                              has_persona_md=True)],
        expertise=[ExpertiseInfo(id="python",
                                 path="/fake/library/stacks/python",
                                 files=["conventions.md"])],
        hook_packs=[
            HookPackInfo(
                id="compliance-gate",
                path="/fake/library/claude/hooks/compliance-gate.md",
                files=["compliance-gate.md"],
                posture_compatibility={
                    "baseline": {"included": "No", "default_mode": "—"},
                    "hardened": {"included": "No", "default_mode": "—"},
                    "regulated": {
                        "included": "Yes", "default_mode": "enforcing",
                    },
                },
            ),
            HookPackInfo(
                id="pre-commit-lint",
                path="/fake/library/claude/hooks/pre-commit-lint.md",
                files=["pre-commit-lint.md"],
                posture_compatibility={
                    "baseline": {"included": "Yes", "default_mode": "enforcing"},
                    "hardened": {"included": "Yes", "default_mode": "enforcing"},
                    "regulated": {"included": "Yes", "default_mode": "enforcing"},
                },
            ),
        ],
    )


class TestHookPackPostureCompatibility:
    """Error when an active pack declares the composition's posture as excluded."""

    def test_baseline_with_compliance_gate_errors(self):
        spec = _make_spec(hooks=HooksConfig(
            posture=Posture.BASELINE,
            packs=[HookPackSelection(id="compliance-gate")],
        ))
        result = run_pre_generation_validation(
            spec, _library_with_compliance_gate(),
        )
        errors = [
            m for m in result.errors
            if m.code == "hook-pack-posture-incompatible"
        ]
        assert len(errors) == 1
        assert "compliance-gate" in errors[0].message
        assert "baseline" in errors[0].message

    def test_regulated_with_compliance_gate_ok(self):
        spec = _make_spec(hooks=HooksConfig(
            posture=Posture.REGULATED,
            packs=[HookPackSelection(id="compliance-gate")],
        ))
        result = run_pre_generation_validation(
            spec, _library_with_compliance_gate(),
        )
        assert not any(
            m.code == "hook-pack-posture-incompatible" for m in result.messages
        )

    def test_compatible_pack_no_error(self):
        spec = _make_spec(hooks=HooksConfig(
            posture=Posture.BASELINE,
            packs=[HookPackSelection(id="pre-commit-lint")],
        ))
        result = run_pre_generation_validation(
            spec, _library_with_compliance_gate(),
        )
        assert not any(
            m.code == "hook-pack-posture-incompatible" for m in result.messages
        )

    def test_disabled_incompatible_pack_ignored(self):
        spec = _make_spec(hooks=HooksConfig(
            posture=Posture.BASELINE,
            packs=[HookPackSelection(id="compliance-gate", enabled=False)],
        ))
        result = run_pre_generation_validation(
            spec, _library_with_compliance_gate(),
        )
        assert not any(
            m.code == "hook-pack-posture-incompatible" for m in result.messages
        )

    def test_pack_without_metadata_skipped(self):
        """Older library entries with no posture_compatibility don't raise."""
        lib = LibraryIndex(
            library_root="/fake/library",
            personas=[PersonaInfo(id="developer",
                                  path="/fake/library/personas/developer",
                                  has_persona_md=True)],
            expertise=[ExpertiseInfo(id="python",
                                     path="/fake/library/stacks/python",
                                     files=["conventions.md"])],
            hook_packs=[
                HookPackInfo(
                    id="pre-commit-lint",
                    path="/fake/library/claude/hooks/pre-commit-lint.md",
                    files=["pre-commit-lint.md"],
                    # posture_compatibility left empty
                ),
            ],
        )
        spec = _make_spec(hooks=HooksConfig(
            posture=Posture.BASELINE,
            packs=[HookPackSelection(id="pre-commit-lint")],
        ))
        result = run_pre_generation_validation(spec, lib)
        assert not any(
            m.code == "hook-pack-posture-incompatible" for m in result.messages
        )


# ---------------------------------------------------------------------------
# BEAN-274 — Contract-graph validation (validate_contract_graph)
#
# These tests bind the compose-time contract: every artifact-type a team
# member consumes must be produced by some team member, and produces with
# no consumer surface as warnings. ``handoff-packet`` is excluded by the
# implementation (universally produced; see ADR-013 / library_indexer).
# ---------------------------------------------------------------------------


def _persona(
    pid: str,
    *,
    produces: list[str] | None = None,
    consumes: list[str] | None = None,
) -> PersonaInfo:
    """Minimal PersonaInfo with explicit contract lists."""
    return PersonaInfo(
        id=pid,
        path=f"/fake/library/personas/{pid}",
        has_persona_md=True,
        produces=produces or [],
        consumes=consumes or [],
    )


def _registry(*personas: PersonaInfo) -> LibraryIndex:
    """LibraryIndex used as the registry-of-known-producers."""
    return LibraryIndex(library_root="/fake/library", personas=list(personas))


class TestContractGraphValidatorEmptyAndTrivial:
    """Edge cases at the boundary of the function."""

    def test_empty_team_is_valid(self):
        """No team members ⇒ no consumes ⇒ trivially valid."""
        registry = _registry(_persona("developer", produces=["code-change"]))
        result = validate_contract_graph([], registry)
        assert result.is_valid
        assert result.messages == []

    def test_persona_with_neither_produces_nor_consumes(self):
        """A persona with empty contract lists contributes no findings."""
        team = [_persona("noop")]
        result = validate_contract_graph(team, _registry(*team))
        assert result.is_valid
        assert result.messages == []


class TestContractGraphValidatorValidTeam:
    """Happy path — every consumed type is produced by someone on the team."""

    def test_valid_team_returns_success(self):
        """Producer→consumer pairs balance, and the registry agrees."""
        ba = _persona("ba", produces=["user-story"])
        dev = _persona("developer", consumes=["user-story"])
        team = [ba, dev]
        result = validate_contract_graph(team, _registry(ba, dev))
        assert result.is_valid
        assert result.errors == []
        assert result.warnings == []

    def test_self_satisfied_consume_is_valid(self):
        """A persona that produces and consumes the same type is satisfied."""
        p = _persona("solo", produces=["x"], consumes=["x"])
        team = [p]
        result = validate_contract_graph(team, _registry(p))
        assert result.is_valid
        assert result.warnings == []  # not an orphan — there *is* a consumer

    def test_handoff_packet_is_always_satisfied(self):
        """``handoff-packet`` is excluded from contract-graph checks; a
        consumer with no producer for it must NOT raise an error."""
        team_lead = _persona("team-lead", consumes=["handoff-packet"])
        result = validate_contract_graph([team_lead], _registry(team_lead))
        assert result.is_valid
        # And it must not appear as an orphan when produced either:
        producer = _persona("dev", produces=["handoff-packet"])
        result2 = validate_contract_graph(
            [producer], _registry(producer),
        )
        assert result2.is_valid
        assert result2.warnings == []


class TestContractGraphValidatorMissingProducer:
    """The headline ERROR path — consume with no team-member producer."""

    def test_missing_producer_is_error(self):
        ba = _persona("ba", produces=["user-story"])
        dev = _persona("developer", consumes=["user-story"])
        team = [dev]  # ba is in the library, NOT on the team
        result = validate_contract_graph(team, _registry(ba, dev))
        assert not result.is_valid
        assert len(result.errors) == 1
        msg = result.errors[0]
        assert msg.code == "missing-producer"
        # The artifact-type name must appear in the message — that is what
        # the user reads to know what's broken.
        assert "user-story" in msg.message
        # The consuming persona must be named so the user knows who is
        # waiting on the input.
        assert "developer" in msg.message
        # The library producer is listed as an actionable suggestion.
        assert "ba" in msg.message

    def test_missing_producer_lists_all_consumers(self):
        """When several team members consume the same missing type, all
        appear in the message."""
        ba = _persona("ba", produces=["user-story"])
        dev = _persona("developer", consumes=["user-story"])
        qa = _persona("tech-qa", consumes=["user-story"])
        result = validate_contract_graph([dev, qa], _registry(ba, dev, qa))
        errs = [m for m in result.errors if m.code == "missing-producer"]
        assert len(errs) == 1
        assert "developer" in errs[0].message
        assert "tech-qa" in errs[0].message

    def test_missing_producer_lists_library_producers_as_suggestion(self):
        """The remediation hint names every library persona that produces
        the missing type."""
        producer_a = _persona("ba", produces=["user-story"])
        producer_b = _persona("team-lead", produces=["user-story"])
        dev = _persona("developer", consumes=["user-story"])
        result = validate_contract_graph(
            [dev], _registry(producer_a, producer_b, dev),
        )
        msg = result.errors[0].message
        assert "ba" in msg
        assert "team-lead" in msg

    def test_missing_producer_with_no_library_producer_says_none(self):
        """If nobody in the library produces the type either, the message
        should still be informative (not crash)."""
        dev = _persona("developer", consumes=["mystery-type"])
        result = validate_contract_graph([dev], _registry(dev))
        assert len(result.errors) == 1
        assert "mystery-type" in result.errors[0].message
        assert "none" in result.errors[0].message.lower()

    def test_multiple_missing_producers_sorted_by_type(self):
        """Multiple missing types are emitted as separate ERRORs, sorted
        by artifact name for deterministic output."""
        dev = _persona("developer", consumes=["zeta", "alpha", "mu"])
        result = validate_contract_graph([dev], _registry(dev))
        errs = [m for m in result.errors if m.code == "missing-producer"]
        assert len(errs) == 3
        types_in_order = []
        for m in errs:
            for t in ("alpha", "mu", "zeta"):
                if f"'{t}'" in m.message:
                    types_in_order.append(t)
                    break
        assert types_in_order == ["alpha", "mu", "zeta"]

    def test_missing_producer_severity_is_error(self):
        """Severity must be ERROR, not WARNING — this is the standard-mode
        hard-fail signal that the generator pipeline gates on."""
        dev = _persona("developer", consumes=["task-spec"])
        result = validate_contract_graph([dev], _registry(dev))
        assert all(m.severity == Severity.ERROR for m in result.errors)
        assert not result.is_valid


class TestContractGraphValidatorOrphanProduces:
    """Produce with no on-team consumer ⇒ WARNING (in both modes)."""

    def test_orphan_produces_emits_warning(self):
        dev = _persona("developer", produces=["dev-decision"])
        result = validate_contract_graph([dev], _registry(dev))
        assert result.is_valid  # warnings don't break is_valid
        warns = [m for m in result.warnings if m.code == "orphan-produces"]
        assert len(warns) == 1
        assert "developer" in warns[0].message
        assert "dev-decision" in warns[0].message

    def test_orphan_produces_severity_is_warning(self):
        dev = _persona("developer", produces=["dev-decision"])
        result = validate_contract_graph([dev], _registry(dev))
        assert all(m.severity == Severity.WARNING for m in result.warnings)

    def test_orphan_produces_skipped_when_someone_on_team_consumes(self):
        """An orphan only fires when the *team* lacks a consumer — being
        consumed by a library persona NOT on the team is irrelevant."""
        on_team_consumer = _persona("ba", consumes=["scope-definition"])
        on_team_producer = _persona("po", produces=["scope-definition"])
        result = validate_contract_graph(
            [on_team_consumer, on_team_producer],
            _registry(on_team_consumer, on_team_producer),
        )
        assert result.warnings == []

    def test_orphan_warning_fires_even_when_library_has_consumer(self):
        """A library-only consumer doesn't satisfy a team-only produce —
        the warning is about the *team's* internal coherence."""
        on_team = _persona("dev", produces=["unconsumed-by-team"])
        library_only_consumer = _persona(
            "absent", consumes=["unconsumed-by-team"],
        )
        result = validate_contract_graph(
            [on_team], _registry(on_team, library_only_consumer),
        )
        warns = [m for m in result.warnings if m.code == "orphan-produces"]
        assert len(warns) == 1

    def test_handoff_packet_is_not_an_orphan(self):
        """``handoff-packet`` is universally produced — it must never
        appear in orphan-produces output even when nobody declares
        consuming it."""
        producer = _persona("dev", produces=["handoff-packet"])
        result = validate_contract_graph([producer], _registry(producer))
        assert result.warnings == []


class TestContractGraphValidatorMixedResults:
    """Combinations — ensure errors and warnings co-exist correctly."""

    def test_mixed_missing_and_orphan(self):
        dev = _persona(
            "developer",
            produces=["unused-output"],
            consumes=["missing-input"],
        )
        result = validate_contract_graph([dev], _registry(dev))
        errs = [m for m in result.errors if m.code == "missing-producer"]
        warns = [m for m in result.warnings if m.code == "orphan-produces"]
        assert len(errs) == 1
        assert len(warns) == 1
        assert not result.is_valid  # an ERROR was present

    def test_message_ordering_errors_before_warnings(self):
        """The implementation appends errors first then warnings —
        downstream UI relies on this order to render severity sections."""
        dev = _persona(
            "developer",
            produces=["orphan-1"],
            consumes=["unsatisfied-1"],
        )
        result = validate_contract_graph([dev], _registry(dev))
        # First message is the ERROR (missing producer), second is the
        # WARNING (orphan produce).
        assert result.messages[0].severity == Severity.ERROR
        assert result.messages[1].severity == Severity.WARNING
