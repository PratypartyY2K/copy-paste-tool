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

2. Install runtime/test dependencies (PyQt6 and pytest are required for the GUI tests):

```bash
python -m pip install -r requirements.txt
```

3. Run the app locally (with venv active):

```bash
python clipboard_manager/main.py
```

CI and coverage
----------------
This repository includes a GitHub Actions workflow at `.github/workflows/ci.yml`.
- CI runs `pytest` in a headless environment using `xvfb` so GUI tests (pytest-qt) run reliably.
- The workflow enforces a minimum coverage threshold (set to 70% by default). If coverage falls below this value the CI will fail.

Running tests locally
---------------------
Run unit and GUI tests with pytest:

```bash
pytest -q --cov=clipboard_manager --cov-report=term-missing
```

If your platform does not have a display (Linux CI or headless dev machine), run GUI tests under Xvfb:

```bash
sudo apt-get install xvfb
xvfb-run -s "-screen 0 1920x1080x24" pytest -q
```

Project layout (high level)
---------------------------
- `clipboard_manager/` - main package
  - `main.py` - entrypoint for GUI app
  - `gui.py` - Qt UI
  - `watcher.py` - clipboard watcher and pause behavior
  - `history.py` - history store, dedupe, secret-safe, pins
  - `clipboard_item.py` - data model for items
  - `boards.py` - board enum & routing heuristics (rules engine)
  - `utils.py` - small helpers (token detection, transforms, apple script)
- `tests/` - pytest-based unit and GUI tests
- `README.md` - user-facing documentation
- `DEVELOPMENT.md`, `CONTRIBUTING.md` - developer docs

Running tests in CI locally (debugging)
---------------------------------------
You can emulate CI locally by running tests under Xvfb and ensuring the same dependencies are installed:

```bash
xvfb-run -s "-screen 0 1920x1080x24" pytest -q --cov=clipboard_manager --cov-report=xml
```

If tests behave differently in CI, check `requirements.txt` and system packages (Xvfb) in the runner.

Coding style & conventions
-------------------------
- Keep code modular: `watcher` handles capture, `history` handles storage/dedupe/notifications, and `gui` handles display.
- Use stable item IDs (`ClipboardItem.id`) for any UI actions; do not rely on list indices.
- Keep long-running or blocking operations off the Qt main thread; use signals or `QTimer.singleShot(0, ...)` to schedule UI updates.
- Thread-safety: `HistoryStore` uses an RLock — hold it when mutating shared state.

Adding tests
------------
- Add pytest test files under `tests/` using `test_*.py` naming.
- GUI tests may use `pytest-qt` fixtures (e.g., `qtbot`) to manage widgets and event loops.

Last updated: 2026-02-04
