"""Tests for foundry_app.services.subtree_setup — git subtree setup for .claude/."""

from pathlib import Path
from unittest.mock import patch

from foundry_app.services.subtree_setup import setup_subtree


class TestSubtreeSetupErrors:
    """Test error handling in the subtree setup service."""

    def test_returns_warning_when_git_init_fails(self, tmp_path: Path):
        output = tmp_path / "project"
        output.mkdir()

        with patch(
            "foundry_app.services.subtree_setup._run_git"
        ) as mock_git:
            mock_git.return_value.returncode = 128
            mock_git.return_value.stderr = "git init failed"
            result = setup_subtree("git@example.com:test/kit.git", output)

        assert len(result.warnings) > 0
        assert "git init failed" in result.warnings[0]

    def test_returns_warning_when_subtree_add_fails(self, tmp_path: Path):
        output = tmp_path / "project"
        output.mkdir()
        # Create a .git dir so init is skipped
        (output / ".git").mkdir()

        call_count = 0

        def mock_run_git(args, cwd):
            nonlocal call_count
            call_count += 1
            from unittest.mock import MagicMock
            result = MagicMock()
            if args[0] == "rev-parse":
                result.returncode = 0
                result.stdout = "abc123"
            elif args[0] == "remote" and args[1] == "get-url":
                result.returncode = 1
                result.stderr = "No such remote"
            elif args[0] == "remote" and args[1] == "add":
                result.returncode = 0
            elif args[0] == "subtree":
                result.returncode = 1
                result.stderr = "subtree add failed: network error"
            else:
                result.returncode = 0
            return result

        with patch(
            "foundry_app.services.subtree_setup._run_git",
            side_effect=mock_run_git,
        ):
            result = setup_subtree("git@example.com:test/kit.git", output)

        assert any("subtree add failed" in w for w in result.warnings)

    def test_returns_warning_on_timeout(self, tmp_path: Path):
        import subprocess

        output = tmp_path / "project"
        output.mkdir()

        with patch(
            "foundry_app.services.subtree_setup._run_git",
            side_effect=subprocess.TimeoutExpired("git", 30),
        ):
            result = setup_subtree("git@example.com:test/kit.git", output)

        assert any("timed out" in w for w in result.warnings)


class TestSubtreeSetupSuccess:
    """Test successful subtree setup flow."""

    def test_initializes_git_when_no_repo(self, tmp_path: Path):
        output = tmp_path / "project"
        output.mkdir()
        git_calls = []

        def mock_run_git(args, cwd):
            git_calls.append(args)
            from unittest.mock import MagicMock
            result = MagicMock()
            if args[0] == "init":
                (Path(cwd) / ".git").mkdir(exist_ok=True)
                result.returncode = 0
            elif args[0] == "rev-parse":
                result.returncode = 1  # No commits yet
            elif args[0] == "add":
                result.returncode = 0
            elif args[0] == "commit":
                result.returncode = 0
            elif args[0] == "remote" and args[1] == "get-url":
                result.returncode = 1
            elif args[0] == "remote" and args[1] == "add":
                result.returncode = 0
            elif args[0] == "subtree":
                # Simulate subtree add creating files
                claude_dir = Path(cwd) / ".claude"
                claude_dir.mkdir(parents=True, exist_ok=True)
                (claude_dir / "settings.json").write_text("{}")
                result.returncode = 0
            else:
                result.returncode = 0
            return result

        with patch(
            "foundry_app.services.subtree_setup._run_git",
            side_effect=mock_run_git,
        ):
            result = setup_subtree("git@example.com:test/kit.git", output)

        assert any(args[0] == "init" for args in git_calls)
        assert len(result.warnings) == 0
        assert len(result.wrote) > 0

    def test_skips_remote_add_when_exists(self, tmp_path: Path):
        output = tmp_path / "project"
        output.mkdir()
        (output / ".git").mkdir()
        git_calls = []

        def mock_run_git(args, cwd):
            git_calls.append(args)
            from unittest.mock import MagicMock
            result = MagicMock()
            if args[0] == "rev-parse":
                result.returncode = 0
            elif args[0] == "remote" and args[1] == "get-url":
                result.returncode = 0  # Remote already exists
                result.stdout = "git@example.com:test/kit.git"
            elif args[0] == "subtree":
                claude_dir = Path(cwd) / ".claude"
                claude_dir.mkdir(parents=True, exist_ok=True)
                (claude_dir / "commands").mkdir()
                (claude_dir / "commands" / "run.md").write_text("# Run")
                result.returncode = 0
            else:
                result.returncode = 0
            return result

        with patch(
            "foundry_app.services.subtree_setup._run_git",
            side_effect=mock_run_git,
        ):
            result = setup_subtree("git@example.com:test/kit.git", output)

        # Should NOT have called remote add
        assert not any(
            args[0] == "remote" and args[1] == "add" for args in git_calls
        )
        assert len(result.warnings) == 0

    def test_wrote_contains_relative_paths(self, tmp_path: Path):
        output = tmp_path / "project"
        output.mkdir()
        (output / ".git").mkdir()

        def mock_run_git(args, cwd):
            from unittest.mock import MagicMock
            result = MagicMock()
            result.returncode = 0
            if args[0] == "remote" and args[1] == "get-url":
                result.returncode = 1
            elif args[0] == "subtree":
                claude_dir = Path(cwd) / ".claude"
                claude_dir.mkdir(parents=True, exist_ok=True)
                (claude_dir / "settings.json").write_text("{}")
                (claude_dir / "agents").mkdir()
                (claude_dir / "agents" / "dev.md").write_text("# Dev")
            return result

        with patch(
            "foundry_app.services.subtree_setup._run_git",
            side_effect=mock_run_git,
        ):
            result = setup_subtree("git@example.com:test/kit.git", output)

        for path in result.wrote:
            assert not path.startswith("/"), f"Path should be relative: {path}"
            assert path.startswith(".claude/")
