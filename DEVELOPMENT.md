# Development Guide

This document provides steps to set up a development environment, run the app locally, write tests, and work with CI.

Prerequisites
-------------
- Python 3.11+ recommended
- macOS (preferred) for frontmost-app attribution; many features are macOS-specific (pyobjc, osascript)
- Optional: Xvfb on Linux if you need to run GUI tests in headless CI

Setup
-----
1. Create and activate a virtualenv (recommended):

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install -r requirements.txt
    python -m pip install -r requirements-ci.txt
    ```

2. Install PyQt6 into your active venv:

    ```bash
    python -m pip install PyQt6
    ```

Running the app
----------------
- Without persistence:

    ```bash
    python -m clipboard_manager.main
    ```

- With persistence enabled (stores history to SQLite):

    ```bash
    export CLIP_PERSISTENCE_DB=./.local/persistence.db
    python -m clipboard_manager.main
    ```

Testing
-------
- Run the lightweight test scripts (smoke tests):

    ```bash
    python -m pytest -q --maxfail=1
    ```

- Or run individual scripts in `tests/` for focused checks. For GUI tests run via `pytest-qt` you may need Xvfb on CI or run on macOS directly.

Style and linting
-----------------
- Keep code readable and documented. Follow typical Python conventions (PEP8). We don't enforce linting in CI currently, but you can run `flake8` locally if preferred.

Debugging tips
--------------
- Enable runtime debug logging for clipboard attribution and history with:

    ```bash
    export CLIP_DEBUG=2
    python -m clipboard_manager.main
    ```

- To inspect the persistence DB directly use sqlite3:

    ```bash
    sqlite3 ./.local/persistence.db "SELECT id, source_app, timestamp, substr(content,1,200) FROM items ORDER BY timestamp DESC LIMIT 50;"
    ```

Schema migrations
-----------------
- The project previously stored a `board` column in the `items` table; that column has been removed in favor of a simpler history model.
- Use the provided migration helper to drop the `board` column safely (dry-run first):

```bash
PYTHONPATH=. python scripts/drop_board_column.py --db ./.local/persistence.db
# if you are satisfied with dry-run results
PYTHONPATH=. python scripts/drop_board_column.py --db ./.local/persistence.db --apply
```

Archived reference implementation
---------------------------------
The board-routing rules engine has been deprecated and archived. If you need to inspect the legacy implementation, see `archive/boards_reference.py`.

If you plan to revive board routing in the future, the recommended approach is to externalize rules as a JSON file and load them via a small rules engine (the archived file contains an example `BoardRouter` and `Board` enum you can reuse).

CI notes
--------
- The GitHub Actions workflow runs unit tests and coverage checks. See `.github/workflows/ci.yml`.
- Tests that require a display are run under Xvfb in CI; local developers can use Xvfb or run tests directly on macOS.

Contributing workflow
---------------------
- Create a branch, add tests for new behavior; run the test suite locally; open a PR.
- CI will run tests and post coverage (if enabled).

Maintenance
-----------
- Keep dependencies current in `requirements.txt` and `requirements-ci.txt`.
- Keep `codecov.yml` and `.github/workflows/ci.yml` updated when adding new test requirements.

Security
--------
- Please report any security vulnerabilities to the maintainers privately, and do not disclose them publicly until they are addressed.

Packaging and releases
----------------------

I include helper scripts and a PyInstaller spec so I can experiment locally with packaging. I am not publishing signed builds from this repository at the moment; when I decide to prepare an official signed/notarized build I will document the release steps here.

Last updated: 2026-02-07
