"""Security tests — input bounds & error sanitization (BEAN-113)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from foundry_app.core.models import (
    ExpertiseSelection,
    HookPackSelection,
    PersonaSelection,
    ProjectIdentity,
    SecretPolicy,
)

# ---------------------------------------------------------------------------
# max_length constraints
# ---------------------------------------------------------------------------

class TestMaxLengthBounds:
    """String fields must enforce max_length constraints."""

    def test_name_rejects_over_200(self):
        with pytest.raises(ValidationError, match="String should have at most 200"):
            ProjectIdentity(name="x" * 201, slug="x")

    def test_name_accepts_200(self):
        p = ProjectIdentity(name="x" * 200, slug="x")
        assert len(p.name) == 200

    def test_slug_rejects_over_100(self):
        with pytest.raises(ValidationError):
            ProjectIdentity(name="x", slug="a" * 101)

    def test_slug_accepts_100(self):
        p = ProjectIdentity(name="x", slug="a" * 100)
        assert len(p.slug) == 100

    def test_output_root_rejects_over_500(self):
        with pytest.raises(ValidationError, match="String should have at most 500"):
            ProjectIdentity(name="x", slug="x", output_root="a" * 501)

    def test_output_folder_rejects_over_200(self):
        with pytest.raises(ValidationError, match="String should have at most 200"):
            ProjectIdentity(name="x", slug="x", output_folder="a" * 201)

    def test_persona_id_rejects_over_100(self):
        with pytest.raises(ValidationError):
            PersonaSelection(id="a" * 101)

    def test_expertise_id_rejects_over_100(self):
        with pytest.raises(ValidationError):
            ExpertiseSelection(id="a" * 101)

    def test_hook_pack_id_rejects_over_100(self):
        with pytest.raises(ValidationError):
            HookPackSelection(id="a" * 101)


# ---------------------------------------------------------------------------
# Regex pattern pre-validation
# ---------------------------------------------------------------------------

class TestSecretPatternValidation:
    """SecretPolicy.secret_patterns must pre-validate regex patterns."""

    def test_rejects_invalid_regex(self):
        with pytest.raises(ValidationError, match="not a valid regex"):
            SecretPolicy(secret_patterns=["(?i)valid", "[invalid"])

    def test_accepts_valid_patterns(self):
        sp = SecretPolicy(secret_patterns=[
            r"(?i)api[_-]?key",
            r"(?i)secret[_-]?key",
            r"(?i)password\s*=",
        ])
        assert len(sp.secret_patterns) == 3

    def test_accepts_empty_list(self):
        sp = SecretPolicy(secret_patterns=[])
        assert sp.secret_patterns == []

    def test_rejects_unclosed_group(self):
        with pytest.raises(ValidationError, match="not a valid regex"):
            SecretPolicy(secret_patterns=["(unclosed"])

    def test_rejects_bad_quantifier(self):
        with pytest.raises(ValidationError, match="not a valid regex"):
            SecretPolicy(secret_patterns=["*bad"])


# ---------------------------------------------------------------------------
# Hex color validation
# ---------------------------------------------------------------------------

class TestHexColorValidation:
    """_tint_svg must reject invalid color strings."""

    def test_rejects_non_hex(self):
        from foundry_app.ui.icons import _tint_svg

        with pytest.raises(ValueError, match="Invalid hex color"):
            _tint_svg(b'<svg stroke="#ffffff"/>', "not-a-color")

    def test_rejects_injection_attempt(self):
        from foundry_app.ui.icons import _tint_svg

        with pytest.raises(ValueError, match="Invalid hex color"):
            _tint_svg(b'<svg stroke="#ffffff"/>', '" onclick="alert(1)')

    def test_rejects_short_hex(self):
        from foundry_app.ui.icons import _tint_svg

        with pytest.raises(ValueError, match="Invalid hex color"):
            _tint_svg(b'<svg stroke="#ffffff"/>', "#fff")

    def test_accepts_valid_hex(self):
        from foundry_app.ui.icons import _tint_svg

        result = _tint_svg(b'<svg stroke="#ffffff"/>', "#c9a84c")
        assert b'stroke="#c9a84c"' in result

    def test_accepts_uppercase_hex(self):
        from foundry_app.ui.icons import _tint_svg

        result = _tint_svg(b'<svg fill="#000000"/>', "#C9A84C")
        assert b'fill="#C9A84C"' in result


# ---------------------------------------------------------------------------
# Error message sanitization
# ---------------------------------------------------------------------------

class TestErrorSanitization:
    """GenerationWorker should not leak raw exception text."""

    def test_worker_emits_generic_error(self, monkeypatch):
        from unittest.mock import MagicMock

        from foundry_app.core.models import CompositionSpec
        from foundry_app.ui.generation_worker import GenerationWorker

        spec = CompositionSpec(
            project=ProjectIdentity(name="Test", slug="test"),
        )
        worker = GenerationWorker(spec=spec, library_root="/nonexistent/path")

        # Mock the signal to capture emitted values
        mock_signal = MagicMock()
        monkeypatch.setattr(worker, "finished_err", mock_signal)

        # Mock generate_project to raise a revealing exception
        def _raise(*a, **kw):
            raise RuntimeError("secret path: /etc/passwd was accessed")

        monkeypatch.setattr(
            "foundry_app.services.generator.generate_project", _raise,
        )

        worker.run()

        mock_signal.emit.assert_called_once()
        error_msg = mock_signal.emit.call_args[0][0]
        assert "Check the log file" in error_msg
        assert "/etc/passwd" not in error_msg
