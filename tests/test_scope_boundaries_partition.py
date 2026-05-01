"""Tests for BEAN-275 — acceptance-criteria & ADR/dev-decision partition.

These tests lock in the Scope Boundaries subsections added to the five
core persona files (library + kit) and the bean-template subnote. They
enforce:

1. Subsection presence in library persona files.
2. Subsection presence in kit agent files.
3. AC ownership rule wording present in every subsection.
4. ADR-vs-dev-decision rule referenced by the three roles that touch it
   (Architect, Developer, Team-Lead).
5. No persona file contradicts the AC ownership rule (grep sweep).
6. Bean template carries the "Authored by" subnote under
   ``## Acceptance Criteria``.
7. Partition cleanliness — exactly one role authors ``acceptance-criteria``
   per wave config, ADRs are Architect-only, dev-decisions Developer-only.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

CORE_PERSONAS = ("ba", "architect", "developer", "tech-qa", "team-lead")

LIBRARY_PERSONA_FILES = {
    # Per ADR-014, core personas live under ``personas/core/<role>``.
    role: REPO_ROOT / "ai-team-library" / "personas" / "core" / role / "persona.md"
    for role in CORE_PERSONAS
}

KIT_AGENT_FILES = {
    role: REPO_ROOT / ".claude" / "shared" / "agents" / f"{role}.md"
    for role in CORE_PERSONAS
}

BEAN_TEMPLATE = REPO_ROOT / "ai" / "beans" / "_bean-template.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_scope_boundaries(text: str, role: str) -> str:
    """Return the Scope Boundaries subsection that names AC ownership.

    Tech-QA's library file has two ``## Scope Boundaries`` headings — the
    pre-existing CQR partition and the new AC/ADR partition. Pick the one
    whose body explicitly names BA / Team-Lead and uses the
    "Does not author" heading that BEAN-275 introduced.
    """
    pattern = re.compile(
        r"^## Scope Boundaries[^\n]*\n(.*?)(?=^## |\Z)",
        re.DOTALL | re.MULTILINE,
    )
    matches = pattern.findall(text)
    if not matches:
        return ""
    # The BEAN-275 AC/ADR partition section is identifiable by the
    # "Does not author" sub-heading (no other Scope Boundaries section
    # in the codebase uses that exact heading).
    for body in matches:
        if "### Does not author" in body:
            return body
    # Fall back to the first one if the explicit marker is missing —
    # presence tests will then fail loudly, which is the correct
    # behaviour for files that are out of policy.
    return matches[0]


# ---------------------------------------------------------------------------
# 1 + 2. Subsection presence (library + kit)
# ---------------------------------------------------------------------------


class TestScopeBoundariesPresent:
    """Every core persona file (library + kit) carries a non-empty
    Scope Boundaries subsection that addresses AC/ADR ownership."""

    @pytest.mark.parametrize("role", CORE_PERSONAS)
    def test_library_persona_has_subsection(self, role: str):
        path = LIBRARY_PERSONA_FILES[role]
        text = path.read_text(encoding="utf-8")
        body = _extract_scope_boundaries(text, role)
        assert body.strip(), f"{path} missing Scope Boundaries subsection"
        assert "acceptance" in body.lower(), (
            f"{path} Scope Boundaries does not mention acceptance criteria"
        )

    @pytest.mark.parametrize("role", CORE_PERSONAS)
    def test_kit_agent_has_subsection(self, role: str):
        path = KIT_AGENT_FILES[role]
        text = path.read_text(encoding="utf-8")
        body = _extract_scope_boundaries(text, role)
        assert body.strip(), f"{path} missing Scope Boundaries subsection"
        assert "acceptance" in body.lower(), (
            f"{path} Scope Boundaries does not mention acceptance criteria"
        )


# ---------------------------------------------------------------------------
# 3. AC ownership rule — every subsection names the AC owner correctly
# ---------------------------------------------------------------------------


class TestAcceptanceCriteriaOwnershipRule:
    """The AC ownership rule (BA-when-on-wave / Team-Lead-default;
    others verify) is consistent across every Scope Boundaries subsection."""

    @pytest.mark.parametrize(
        "role,paths",
        [
            (role, [LIBRARY_PERSONA_FILES[role], KIT_AGENT_FILES[role]])
            for role in CORE_PERSONAS
        ],
    )
    def test_subsection_names_ac_owner(self, role: str, paths: list[Path]):
        for path in paths:
            text = path.read_text(encoding="utf-8")
            body = _extract_scope_boundaries(text, role).lower()
            assert "ba" in body, f"{path} subsection does not name BA"
            assert "team-lead" in body or "team lead" in body, (
                f"{path} subsection does not name Team-Lead"
            )

    def test_ba_owns_when_activated(self):
        for path in (LIBRARY_PERSONA_FILES["ba"], KIT_AGENT_FILES["ba"]):
            body = _extract_scope_boundaries(
                path.read_text(encoding="utf-8"), "ba"
            ).lower()
            assert "owns" in body and "ba" in body
            assert "when activated" in body or "when ba is on the wave" in body, (
                f"{path} BA section must say BA owns AC when activated on the wave"
            )

    def test_team_lead_owns_by_default(self):
        for path in (
            LIBRARY_PERSONA_FILES["team-lead"],
            KIT_AGENT_FILES["team-lead"],
        ):
            body = _extract_scope_boundaries(
                path.read_text(encoding="utf-8"), "team-lead"
            ).lower()
            assert "by default" in body, (
                f"{path} Team-Lead section must say AC ownership is by default"
            )

    @pytest.mark.parametrize("role", ("architect", "developer", "tech-qa"))
    def test_non_authoring_roles_say_does_not_author(self, role: str):
        for path in (LIBRARY_PERSONA_FILES[role], KIT_AGENT_FILES[role]):
            body = _extract_scope_boundaries(
                path.read_text(encoding="utf-8"), role
            ).lower()
            # Each non-authoring role must explicitly say it does not
            # author / verifies against, never edits.
            says_not_author = "does not author" in body
            says_verify = "verif" in body and "never edit" in body
            assert says_not_author or says_verify, (
                f"{path} must say {role} does not author AC / verifies "
                f"against AC and never edits"
            )


# ---------------------------------------------------------------------------
# 4. ADR-vs-dev-decision rule — Architect, Developer, Team-Lead reference it
# ---------------------------------------------------------------------------


class TestAdrThresholdRule:
    """Architect, Developer, and Team-Lead Scope Boundaries reference the
    blast-radius rule that splits ADR from dev-decision."""

    ADR_KEYWORDS = ("adr", "dev-decision")

    @pytest.mark.parametrize("role", ("architect", "developer", "team-lead"))
    def test_subsection_references_adr_split(self, role: str):
        for path in (LIBRARY_PERSONA_FILES[role], KIT_AGENT_FILES[role]):
            body = _extract_scope_boundaries(
                path.read_text(encoding="utf-8"), role
            ).lower()
            for kw in self.ADR_KEYWORDS:
                assert kw in body, (
                    f"{path} Scope Boundaries must reference '{kw}'"
                )

    def test_architect_owns_adrs(self):
        for path in (
            LIBRARY_PERSONA_FILES["architect"],
            KIT_AGENT_FILES["architect"],
        ):
            body = _extract_scope_boundaries(
                path.read_text(encoding="utf-8"), "architect"
            ).lower()
            assert "owns" in body and "adr" in body, (
                f"{path} Architect section must claim ADR ownership"
            )

    def test_developer_owns_dev_decisions(self):
        for path in (
            LIBRARY_PERSONA_FILES["developer"],
            KIT_AGENT_FILES["developer"],
        ):
            body = _extract_scope_boundaries(
                path.read_text(encoding="utf-8"), "developer"
            ).lower()
            assert "dev-decision" in body and (
                "owns" in body or "produces" in body
            ), f"{path} Developer section must claim dev-decision ownership"

    def test_developer_pause_request_architect(self):
        """Developer Scope Boundaries must require pause-and-escalate when
        a choice crosses the ADR threshold (per Rule 2)."""
        for path in (
            LIBRARY_PERSONA_FILES["developer"],
            KIT_AGENT_FILES["developer"],
        ):
            body = _extract_scope_boundaries(
                path.read_text(encoding="utf-8"), "developer"
            ).lower()
            assert "pause" in body or "stop" in body, (
                f"{path} must instruct Developer to pause when crossing "
                f"the ADR threshold"
            )
            assert "architect" in body, (
                f"{path} must name Architect activation as the escalation"
            )


# ---------------------------------------------------------------------------
# 5. No contradictions — grep sweep for forbidden authoring claims
# ---------------------------------------------------------------------------


# Lines anywhere in the five library + kit files that would contradict
# the BEAN-275 partition. Match case-insensitively across the whole file.
FORBIDDEN_PHRASES = (
    "developer writes acceptance criteria",
    "developer authors acceptance criteria",
    "developer defines acceptance criteria",
    "tech-qa writes acceptance criteria",
    "tech-qa authors acceptance criteria",
    "tech-qa defines acceptance criteria",
    "tech qa writes acceptance criteria",
    "tech qa authors acceptance criteria",
    "tech qa defines acceptance criteria",
    "architect writes acceptance criteria",
    "architect authors acceptance criteria",
    "architect defines acceptance criteria",
)


class TestNoContradictions:
    """No persona file says a non-owner *authors* acceptance criteria."""

    def test_no_forbidden_phrase_in_any_file(self):
        all_files = list(LIBRARY_PERSONA_FILES.values()) + list(
            KIT_AGENT_FILES.values()
        )
        offenders: list[tuple[Path, str]] = []
        for path in all_files:
            text = path.read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_PHRASES:
                if phrase in text:
                    offenders.append((path, phrase))
        assert not offenders, (
            "Forbidden authoring claims found:\n"
            + "\n".join(f"  {p}: {phrase!r}" for p, phrase in offenders)
        )


# ---------------------------------------------------------------------------
# 6. Bean template subnote
# ---------------------------------------------------------------------------


class TestBeanTemplateSubnote:
    """``ai/beans/_bean-template.md`` carries the Authored-by subnote
    immediately under the ``## Acceptance Criteria`` heading."""

    def test_template_has_authored_by_blockquote(self):
        text = BEAN_TEMPLATE.read_text(encoding="utf-8")
        # The subnote is a blockquote immediately under the AC heading.
        match = re.search(
            r"^## Acceptance Criteria\s*\n\s*\n(> [^\n]+)",
            text,
            re.MULTILINE,
        )
        assert match, (
            "_bean-template.md is missing a blockquote subnote directly "
            "under the ## Acceptance Criteria heading"
        )
        subnote = match.group(1).lower()
        assert "authored by" in subnote, (
            f"AC subnote must say 'Authored by'; got: {match.group(1)!r}"
        )
        assert "ba" in subnote, "AC subnote must mention BA"
        assert "team-lead" in subnote or "team lead" in subnote, (
            "AC subnote must mention Team-Lead"
        )
        assert "default" in subnote, (
            "AC subnote must mark Team-Lead as the default author"
        )


# ---------------------------------------------------------------------------
# 7. Partition cleanliness — single owner per artifact per wave config
# ---------------------------------------------------------------------------


# Map: artifact -> set of roles allowed to claim authorship.
# acceptance-criteria has a dual producer (BA when activated, Team-Lead
# default) per ADR-013; ADRs are Architect-only; dev-decisions Developer-only.
ALLOWED_AUTHORS = {
    "acceptance-criteria": {"ba", "team-lead"},
    "adr": {"architect"},
    "dev-decision": {"developer"},
}


def _owns_block(body: str) -> str:
    """Return just the '### Owns' block of a Scope Boundaries subsection."""
    match = re.search(
        r"^### Owns[^\n]*\n(.*?)(?=^### |\Z)",
        body,
        re.DOTALL | re.MULTILINE,
    )
    return match.group(1) if match else ""


class TestPartitionCleanliness:
    """No two roles claim authorship of the same artifact (modulo the
    BA / Team-Lead dual-producer rule for AC)."""

    def _claimed_artifacts(self, role: str, body: str) -> set[str]:
        """Return artifacts the role's '### Owns' block claims as
        first-position bullet-list authorship.

        We look only at the first words of each ``- `` bullet so that a
        narrative parenthetical reference like ``(per BEAN-273 / ADR-013)``
        in a Team-Lead AC bullet does not falsely register as an
        ADR-authorship claim.
        """
        owns = _owns_block(body)
        claims: set[str] = set()
        for line in owns.splitlines():
            stripped = line.strip()
            if not stripped.startswith("- "):
                continue
            # Take up to the first dash/em-dash separator or end of line —
            # this is the artifact phrase the role claims.
            head = re.split(r" — | -- ", stripped[2:], maxsplit=1)[0].lower()
            if "acceptance criteria" in head or "acceptance-criteria" in head:
                claims.add("acceptance-criteria")
            if re.search(r"\badrs?\b", head):
                claims.add("adr")
            if "dev-decision" in head:
                claims.add("dev-decision")
        return claims

    @pytest.mark.parametrize("role", CORE_PERSONAS)
    def test_role_only_claims_allowed_artifacts(self, role: str):
        for path in (LIBRARY_PERSONA_FILES[role], KIT_AGENT_FILES[role]):
            body = _extract_scope_boundaries(
                path.read_text(encoding="utf-8"), role
            )
            claimed = self._claimed_artifacts(role, body)
            for artifact in claimed:
                allowed = ALLOWED_AUTHORS[artifact]
                assert role in allowed, (
                    f"{path}: role '{role}' claims artifact '{artifact}' "
                    f"but only {sorted(allowed)} may claim it"
                )

    def test_acceptance_criteria_authors_are_exactly_ba_and_team_lead(self):
        authors: set[str] = set()
        for role in CORE_PERSONAS:
            for path in (LIBRARY_PERSONA_FILES[role], KIT_AGENT_FILES[role]):
                body = _extract_scope_boundaries(
                    path.read_text(encoding="utf-8"), role
                )
                if "acceptance-criteria" in self._claimed_artifacts(role, body):
                    authors.add(role)
        assert authors == {"ba", "team-lead"}, (
            f"AC authors must be exactly {{'ba', 'team-lead'}}; got {authors}"
        )

    def test_adr_author_is_exactly_architect(self):
        authors: set[str] = set()
        for role in CORE_PERSONAS:
            for path in (LIBRARY_PERSONA_FILES[role], KIT_AGENT_FILES[role]):
                body = _extract_scope_boundaries(
                    path.read_text(encoding="utf-8"), role
                )
                if "adr" in self._claimed_artifacts(role, body):
                    authors.add(role)
        assert authors == {"architect"}, (
            f"ADR author must be exactly {{'architect'}}; got {authors}"
        )

    def test_dev_decision_author_is_exactly_developer(self):
        authors: set[str] = set()
        for role in CORE_PERSONAS:
            for path in (LIBRARY_PERSONA_FILES[role], KIT_AGENT_FILES[role]):
                body = _extract_scope_boundaries(
                    path.read_text(encoding="utf-8"), role
                )
                if "dev-decision" in self._claimed_artifacts(role, body):
                    authors.add(role)
        assert authors == {"developer"}, (
            f"dev-decision author must be exactly {{'developer'}}; "
            f"got {authors}"
        )
