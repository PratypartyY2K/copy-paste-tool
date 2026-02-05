DEVELOPMENT GUIDE
=================

This document helps contributors set up a local development environment, run the app and tests, and follow the project's conventions.

Prerequisites
-------------
- macOS (the repo contains AppleScript helpers for `get_frontmost_app`)
- Python 3.11 (or a compatible Python 3.x)
- git

Recommended workflow
--------------------
1. Create and activate a virtual environment from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

2. Install runtime/test dependencies (PyQt6 is required for the GUI):

```bash
python -m pip install PyQt6
```

3. Run the app locally (with venv active):

```bash
python clipboard_manager/main.py
```

Project layout (high level)
---------------------------
- `clipboard_manager/` - main package
  - `main.py` - entrypoint for GUI app
  - `gui.py` - Qt UI
  - `watcher.py` - clipboard watcher and pause behavior
  - `history.py` - history store, dedupe, secret-safe, pins
  - `clipboard_item.py` - data model for items
  - `boards.py` - board enum & routing heuristics
  - `utils.py` - small helpers (token detection, transforms, apple script)
- `tests/` - small test scripts that run without pytest
- `README.md` - user-facing documentation
- `DEVELOPMENT.md`, `CONTRIBUTING.md` - developer docs

Running tests
-------------
Several small test scripts exist to validate core behavior. They are intentionally simple so they do not require pytest.

Run them from the project root (with venv active):

```bash
python tests/test_utils.py
python tests/test_secret_safe.py
python tests/test_pins.py
python tests/smoke_pause_test.py
python tests/gui_startup.py  # non-blocking GUI startup check
```

Testing notes
-------------
- `tests/smoke_pause_test.py` validates pause behavior and watcher/history integration.
- `tests/gui_startup.py` creates `QApplication` and instantiates the main window; it runs briefly and exits.
- If tests fail with `ModuleNotFoundError: No module named 'PyQt6'`, make sure you installed PyQt6 into the same Python you're running.

Coding style & conventions
-------------------------
- Keep code modular: `watcher` handles capture, `history` handles storage/dedupe/notifications, and `gui` handles display.
- Use stable item IDs (`ClipboardItem.id`) for any UI actions; do not rely on list indices.
- Keep long-running or blocking operations off the Qt main thread; use signals or `QTimer.singleShot(0, ...)` to schedule UI updates.
- Thread-safety: `HistoryStore` uses an RLock — hold it when mutating shared state.

Adding tests
------------
- Add small unit-style scripts under `tests/` following the existing pattern (they use asserts and print a success string).
- Where possible, keep tests fast and deterministic (avoid depending on a running GUI unless explicitly testing GUI startup).

Working with the codebase
-------------------------
- Use `History.add_change_listener(cb)` to react to background updates rather than polling.
- Use `BoardRouter.assign_board_to_item(item)` to assign boards when creating items.

Debugging tips
--------------
- If the app reports `Unknown App`, the AppleScript call to `osascript` may be blocked — check system permissions and Automation settings.
- For GUI inspection, use Qt designer or print debug statements; remember to avoid printing in tight loops in the main thread.

Next tasks / TODOs (suggested)
-----------------------------
- Add persisted storage (JSON or SQLite) for history, pins and settings (I can implement this next if you confirm a storage format).
- Add more unit tests for board routing heuristics and search logic.

Last updated: 2026-02-04
