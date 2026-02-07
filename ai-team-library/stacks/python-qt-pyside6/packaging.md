# PySide6 Packaging

Building and distributing PySide6 desktop applications as standalone executables
across Windows, macOS, and Linux.

---

## Defaults

- **Primary tool:** PyInstaller (widest platform support, most community knowledge).
- **Project metadata:** `pyproject.toml` with `hatchling` or `setuptools` backend.
- **Icon format:** `.ico` (Windows), `.icns` (macOS), `.png` (Linux).
- **Versioning:** Single source of truth in `pyproject.toml`, read at runtime via `importlib.metadata`.

---

## PyInstaller Configuration

Use a `.spec` file committed to the repo rather than relying on CLI flags.

```python
# app.spec
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

a = Analysis(
    ["src/myapp/main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("src/myapp/resources/styles", "myapp/resources/styles"),
        ("src/myapp/resources/icons", "myapp/resources/icons"),
    ],
    hiddenimports=collect_submodules("myapp"),
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy"],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MyApp",
    debug=False,
    strip=False,
    upx=True,
    console=False,           # False for GUI apps
    icon="assets/app.ico",   # Platform-specific icon
)

coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name="MyApp")
```

---

## Runtime Resource Access

Frozen apps have a different file layout. Use this pattern to locate resources:

```python
from importlib import resources as importlib_resources
from pathlib import Path
import sys


def get_resource_path(relative_path: str) -> Path:
    """Resolve a resource path that works both in dev and frozen builds."""
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        base = Path(sys._MEIPASS)
    else:
        # Running from source
        base = Path(__file__).resolve().parent

    return base / relative_path


# Usage
stylesheet_path = get_resource_path("resources/styles/main.qss")
with open(stylesheet_path) as f:
    app.setStyleSheet(f.read())
```

---

## Do / Don't

- **Do** commit the `.spec` file to version control. It is your build recipe.
- **Do** test the frozen build on each target platform before release.
- **Do** use `--onedir` mode (the default). `--onefile` extracts to a temp dir on every launch and is slow.
- **Do** exclude unnecessary packages (`tkinter`, `matplotlib`, `test`) to shrink bundle size.
- **Do** strip unused Qt modules with `--exclude-module` (e.g., `QtWebEngine` if unused).
- **Don't** rely on `__file__` paths in frozen builds. Use the `get_resource_path` pattern above.
- **Don't** bundle development dependencies (pytest, ruff) into the release.
- **Don't** sign executables manually. Use CI-driven code signing.
- **Don't** distribute without testing the packaged binary on a clean machine.

---

## Alternatives

| Tool            | Strengths                                | Trade-offs                              |
|-----------------|------------------------------------------|-----------------------------------------|
| **PyInstaller** | Mature, cross-platform, large community  | Spec files can be tricky, AV false positives |
| **cx_Freeze**   | Good Windows support, MSI output         | Less community adoption than PyInstaller |
| **Briefcase**   | BeeWare ecosystem, native packaging      | Younger project, less battle-tested      |
| **Nuitka**      | Compiles to C, better performance        | Longer build times, complex configuration |

### Platform-Specific Distribution

| Platform | Format         | Tool                              |
|----------|----------------|-----------------------------------|
| Windows  | MSI / MSIX     | cx_Freeze MSI, WiX, or MSIX      |
| macOS    | .dmg / .app    | PyInstaller + `create-dmg`        |
| Linux    | AppImage / deb | PyInstaller + `appimagetool` or `fpm` |

---

## Common Pitfalls

1. **Missing Qt plugins.** PySide6 needs platform plugins (`platforms/`, `imageformats/`). PyInstaller usually collects them, but verify with `--debug imports` if the app crashes on launch with "Could not find the Qt platform plugin."
2. **Hidden imports.** Dynamic imports (`importlib.import_module`) are invisible to PyInstaller. Add them to `hiddenimports` in the spec.
3. **Antivirus false positives.** PyInstaller `--onefile` executables trigger Windows Defender. Prefer `--onedir` and code-sign the output.
4. **Resource path breakage.** `Path(__file__)` resolves differently in frozen builds. Always use the `sys._MEIPASS` guard pattern.
5. **Huge bundle size.** A bare PySide6 app can reach 100+ MB. Exclude unused Qt modules and use UPX compression.

---

## Checklist

- [ ] `.spec` file committed and builds reproducibly in CI
- [ ] Resources loaded via `get_resource_path()`, not hardcoded paths
- [ ] Unused Qt modules excluded to minimize bundle size
- [ ] `console=False` set for GUI applications
- [ ] Version number read from `pyproject.toml` / `importlib.metadata` at runtime
- [ ] Build tested on clean machine (no Python installed)
- [ ] Platform-specific icons provided (`.ico`, `.icns`, `.png`)
- [ ] Code signing configured in CI for Windows and macOS
- [ ] Installer/package format chosen per platform (MSI, dmg, AppImage)
- [ ] Release build excludes dev dependencies and test code
