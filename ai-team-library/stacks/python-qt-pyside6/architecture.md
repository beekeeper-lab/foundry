# PySide6 Application Architecture

Patterns and structure for maintainable PySide6 desktop applications.
This guide covers Model/View, threading, dependency flow, and state management.

---

## Defaults

- **Architecture pattern:** Model/View/Controller (MVC) adapted to Qt's Model/View framework.
- **Dependency direction:** Views depend on Controllers; Controllers depend on Models and Services; Services have no Qt dependency.
- **State management:** Single-source-of-truth model objects. Views observe via signals.
- **Threading model:** Main thread owns all widgets. Workers run on `QThreadPool`.

---

## Dependency Flow

```
Views (QWidget)
  |  signals/slots
Controllers (QObject, mediators)
  |  method calls
Models (QAbstractItemModel, Pydantic)    Services (pure Python)
  |                                         |
  +----------- Data Layer -----------------+
```

**Rules:**
- Views never import Services. Controllers mediate.
- Services never import `PySide6`. They remain testable without a running `QApplication`.
- Models may be Qt Model/View models or plain Pydantic/dataclass objects depending on context.

---

## Model/View Pattern

```python
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex


class TaskTableModel(QAbstractTableModel):
    """Table model exposing a list of Task objects to any QTableView."""

    COLUMNS = ("Name", "Status", "Due Date")

    def __init__(self, tasks: list | None = None, parent=None) -> None:
        super().__init__(parent)
        self._tasks: list = tasks or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._tasks)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        task = self._tasks[index.row()]
        col = index.column()
        if col == 0:
            return task.name
        if col == 1:
            return task.status
        if col == 2:
            return task.due_date.isoformat() if task.due_date else ""
        return None

    def headerData(self, section: int, orientation, role: int = Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.COLUMNS[section]
        return None

    def replace_data(self, tasks: list) -> None:
        """Replace all data and notify views."""
        self.beginResetModel()
        self._tasks = tasks
        self.endResetModel()
```

---

## QThread Worker Pattern

```python
from PySide6.QtCore import QObject, QThread, Signal, Slot


class ExportWorker(QObject):
    """Worker that runs an export job off the main thread."""

    progress = Signal(int)          # percentage 0-100
    finished = Signal(str)          # result file path
    error = Signal(str)             # error message

    def __init__(self, source_path: str) -> None:
        super().__init__()
        self._source = source_path

    @Slot()
    def run(self) -> None:
        try:
            for i, chunk in enumerate(self._export_chunks()):
                self._write_chunk(chunk)
                self.progress.emit(int((i + 1) / self._total * 100))
            self.finished.emit(self._output_path)
        except Exception as exc:
            self.error.emit(str(exc))


# Usage in a controller or main window:
class ExportController(QObject):
    def start_export(self, path: str) -> None:
        self._thread = QThread()
        self._worker = ExportWorker(path)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._worker.progress.connect(self._on_progress)
        self._worker.error.connect(self._on_error)
        self._thread.start()
```

---

## Do / Don't

- **Do** use `moveToThread()` pattern instead of subclassing `QThread`.
- **Do** keep the service layer free of Qt imports for independent testing.
- **Do** use `QSettings` for persistent user preferences (window size, last path).
- **Do** emit `beginResetModel()` / `endResetModel()` when replacing model data.
- **Don't** store application state in widgets. Widgets are views, not data stores.
- **Don't** create god-class `MainWindow` files. Decompose into controller + view pairs.
- **Don't** use global singletons for state. Pass dependencies explicitly or use a lightweight DI container.
- **Don't** mix business logic into `QAbstractItemModel` subclasses. Delegate to services.

---

## Common Pitfalls

1. **God MainWindow.** Everything lands in `MainWindow.__init__`. Split into controller objects that own their section of the UI.
2. **Thread ownership confusion.** An object's slots run on the thread that owns it. After `moveToThread()`, the worker's slots run on the new thread, but only if connected after the move.
3. **Forgetting `beginInsertRows` / `endInsertRows`.** Mutating model data without notifying the view causes stale displays or crashes.
4. **QSettings key sprawl.** Use a constants file or enum for settings keys. Never use raw strings scattered across the codebase.
5. **Tight coupling to file dialogs.** Inject file paths or use a file-dialog service so controllers can be tested without user interaction.

---

## Checklist

- [ ] Dependency flow is one-directional: Views -> Controllers -> Models/Services
- [ ] Services layer has zero PySide6 imports
- [ ] All `QAbstractItemModel` mutations wrapped in begin/end notification calls
- [ ] Long-running tasks use worker + `moveToThread()` pattern
- [ ] Worker signals connected to main-thread slots for UI updates
- [ ] `QSettings` keys defined as constants, not scattered string literals
- [ ] No business logic in widget classes
- [ ] Application state is observable (signals emitted on change)
- [ ] Main window delegates to controller objects, not a 2000-line monolith
- [ ] Thread cleanup: `quit()` + `wait()` or `deleteLater()` chain in place
