"""Human-readable labels for personas and artifact types in user-facing messages.

Centralizes the vocabulary the validator (and any other UI-surfaced message
source) uses when naming a persona or artifact in prose. The validator
imports these helpers so its `.message` strings never leak slugs like
`adr` or `team-lead` into the wizard. See BEAN-290 and the BA reference doc
at `ai/outputs/ba/BEAN-290-validator-message-phrasing.md`.
"""

from __future__ import annotations

# Short, sentence-fitting label for each artifact id. The
# ArtifactTypeInfo.description in artifact-types.yml is sentence-length;
# we use that as guidance and keep a curated short label here. Ids not
# in this map fall back to a title-cased version of the slug.
_ARTIFACT_LABELS: dict[str, str] = {
    "bean-spec": "bean specification",
    "task-spec": "task specification",
    "user-story": "user stories",
    "acceptance-criteria": "acceptance criteria",
    "scope-definition": "scope definition",
    "risk-register": "risk register",
    "adr": "Architecture Decision Records (ADRs)",
    "design-spec": "design specification",
    "dev-decision": "development-decision note",
    "code-change": "code change",
    "test-suite": "test suite",
    "traceability-matrix": "traceability matrix",
    "vdd-report": "verification report",
    "merge-summary": "merge summary",
}

# Persona ids whose natural title-casing differs from `.title()`. Most
# persona ids title-case cleanly (`developer` → `Developer`,
# `team-lead` → `Team Lead`); the exceptions live here.
_PERSONA_NAME_OVERRIDES: dict[str, str] = {
    "tech-qa": "Tech-QA",
    "ba": "BA",
    "ux-ui-designer": "UX/UI Designer",
    "devops-release": "DevOps Release",
    "platform-sre-engineer": "Platform/SRE Engineer",
}


def artifact_label(artifact_id: str) -> str:
    """Return the human-readable label for an artifact id.

    Falls back to a space-separated title-case rendering of the slug for ids
    not in the override map.
    """
    if artifact_id in _ARTIFACT_LABELS:
        return _ARTIFACT_LABELS[artifact_id]
    return artifact_id.replace("-", " ")


def persona_name(persona_id: str) -> str:
    """Return a user-facing name for a persona id.

    Strips an `extended/` prefix, applies overrides for ids that don't
    title-case cleanly (`tech-qa`, `ba`), and otherwise title-cases the
    hyphen-separated slug.
    """
    bare = persona_id.split("/", 1)[1] if persona_id.startswith("extended/") else persona_id
    if bare in _PERSONA_NAME_OVERRIDES:
        return _PERSONA_NAME_OVERRIDES[bare]
    return " ".join(part.capitalize() for part in bare.split("-"))


def join_personas(persona_ids: list[str], *, prefix: str = "the ") -> str:
    """Join a list of persona ids into a natural-language fragment.

    Each id is rendered via :func:`persona_name`, optionally prefixed with
    `"the "` so the result reads as "the Developer and the Team Lead".
    Uses Oxford-comma style for three or more items.

    Args:
        persona_ids: ordered list of persona ids.
        prefix: per-name prefix; default `"the "`. Pass `""` for no prefix.

    Returns:
        Empty string if the input is empty.
    """
    names = [f"{prefix}{persona_name(pid)}" for pid in persona_ids]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"
