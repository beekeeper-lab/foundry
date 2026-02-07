# Python Packaging

Guidelines for packaging Python projects including dependency management,
distribution, versioning, and build configuration with modern tooling.

---

## Defaults

| Concern              | Default Tool / Approach          |
|----------------------|----------------------------------|
| Build backend        | `hatchling`                      |
| Package manager      | `uv`                             |
| Version management   | Single source in `pyproject.toml` or `__version__` via hatch-vcs |
| Distribution format  | Wheel (sdist for libraries only) |
| Publishing           | `uv publish` or `twine`          |
| Lock file            | `uv.lock` (applications only)    |
| Python version pin   | `.python-version` file           |

### Alternatives

- **`setuptools`** -- the legacy default. Still works, but `hatchling` is
  simpler and faster for modern projects.
- **`flit`** -- minimal build backend. Lacks hatchling's plugin ecosystem.
- **`pdm`** -- PEP 582 support. Useful if you want `__pypackages__/` local
  installs; otherwise `uv` is faster.
- **`poetry`** -- popular but uses a non-standard `pyproject.toml` format for
  dependencies and a custom lock file. Avoid for new projects.

---

## pyproject.toml Reference

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-service"
version = "0.1.0"
description = "Order processing service"
readme = "README.md"
license = "MIT"
requires-python = ">=3.12"
authors = [
    { name = "Team Name", email = "team@example.com" },
]
dependencies = [
    "fastapi>=0.110",
    "structlog>=24.1",
    "pydantic>=2.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "mypy>=1.9",
    "ruff>=0.4",
    "hypothesis>=6.100",
]

[project.scripts]
my-service = "my_service.main:cli"

[tool.hatch.build.targets.wheel]
packages = ["src/my_service"]
```

**Key detail:** When your package directory name does not match the project
name in `[project]`, you must set `packages` explicitly under
`[tool.hatch.build.targets.wheel]`. This is the most common hatchling gotcha.

---

## Dependency Management with uv

```bash
# Create a new project
uv init my-project
cd my-project

# Create virtual environment
uv venv

# Install project in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Add a runtime dependency (then add it to pyproject.toml)
uv add httpx

# Lock dependencies for reproducible installs
uv lock

# Install from lock file in CI
uv sync --frozen
```

### Pinning Strategy

| Project type  | Lock file?   | Version specifiers               |
|---------------|--------------|----------------------------------|
| Application   | Yes (`uv.lock`) | `>=` with upper bound awareness |
| Library       | No           | `>=` minimum, no upper bounds    |
| CLI tool      | Yes          | `>=` with lock for reproducibility |

---

## Versioning

Use semantic versioning (`MAJOR.MINOR.PATCH`):

- **MAJOR** -- breaking API changes.
- **MINOR** -- new features, backward compatible.
- **PATCH** -- bug fixes only.

For automated versioning from git tags, use `hatch-vcs`:

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.hooks.vcs]
version-file = "src/my_service/_version.py"
```

This generates `_version.py` at build time from the latest git tag.

---

## Building and Publishing

```bash
# Build wheel and sdist
uv build

# Check the built distributions
uv run twine check dist/*

# Publish to PyPI (or private registry)
uv publish --token $PYPI_TOKEN

# Publish to a private registry
uv publish --publish-url https://private.registry/simple/ --token $TOKEN
```

For CI, build once and publish the artifact. Never rebuild between test and
publish steps.

---

## Entry Points and CLI Scripts

```toml
# Console script entry point
[project.scripts]
my-cli = "my_service.main:cli"

# Plugin entry points (for extensible apps)
[project.entry-points."my_service.plugins"]
csv-export = "my_service.plugins.csv:CsvExporter"
```

```python
# src/my_service/main.py
from __future__ import annotations

import sys

def cli() -> None:
    """Main entry point for the CLI."""
    # Argument parsing, app bootstrap, etc.
    sys.exit(run())
```

---

## Do / Don't

**Do:**
- Use `pyproject.toml` as the single source of all project metadata.
- Set `requires-python` to the minimum supported version.
- Use `uv lock` and commit `uv.lock` for applications.
- Declare all dependencies in `pyproject.toml`, never in `requirements.txt`
  as the source of truth.
- Build and test the wheel, not just the source tree.
- Use `[project.scripts]` for CLI entry points (not `setup.py` console_scripts).
- Set `packages` explicitly in hatchling when package name differs from
  project name.

**Don't:**
- Use `setup.py` or `setup.cfg` for new projects.
- Add upper bounds to library dependencies (`<2.0`). They cause needless
  resolution conflicts for downstream users.
- Commit `uv.lock` for libraries -- only applications need lock files.
- Use `pip install` directly -- always go through `uv`.
- Put dependency version pins in `requirements.txt` as the source of truth;
  `pyproject.toml` is the source, lock files are the pins.
- Forget to test the built wheel (`uv pip install dist/*.whl && pytest`).

---

## Common Pitfalls

1. **Package name vs. directory name mismatch.** If your project is named
   `my-service` but the package directory is `my_service`, hatchling cannot
   find it without `packages = ["src/my_service"]` in
   `[tool.hatch.build.targets.wheel]`.

2. **Forgetting `src/` in the packages path.** With `src/` layout, the packages
   value must include the `src/` prefix: `["src/my_service"]`, not
   `["my_service"]`.

3. **Using `pip install -e .` instead of `uv pip install -e .`.** Mixing pip
   and uv causes environment inconsistencies. Stick to one tool.

4. **No `requires-python` set.** Without it, your package installs on any
   Python version and fails at runtime with confusing syntax errors.

5. **Editing `requirements.txt` directly.** The dependency source of truth is
   `pyproject.toml`. Lock files are generated artifacts, not hand-edited files.

6. **Publishing without `twine check`.** Malformed metadata (bad README
   rendering, missing classifiers) is caught by `twine check` before you
   push a broken release to PyPI.

7. **Rebuilding between test and publish.** If you build, test, then rebuild
   before publishing, the published artifact was never tested. Build once,
   test the artifact, publish that exact artifact.

---

## Checklist

- [ ] `pyproject.toml` is the single metadata source (no `setup.py`, no `setup.cfg`)
- [ ] `build-system` specifies `hatchling` as the build backend
- [ ] `requires-python` is set to the minimum supported version
- [ ] `src/` layout with explicit `packages` in hatchling config
- [ ] Runtime dependencies in `[project.dependencies]`
- [ ] Dev dependencies in `[project.optional-dependencies] dev = [...]`
- [ ] `uv.lock` committed for applications, absent for libraries
- [ ] `.python-version` file pinning the minor version
- [ ] `[project.scripts]` defined for CLI entry points
- [ ] `twine check` runs in CI before publish
- [ ] Wheel is tested before publishing (`pip install dist/*.whl && pytest`)
- [ ] Version follows semver; automated via `hatch-vcs` if using git tags
- [ ] CI uses `uv sync --frozen` for reproducible installs
