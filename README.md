# App-Aware Clipboard Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE) [![CI](https://github.com/your-org/your-repo/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/your-repo/actions) [![codecov](https://codecov.io/gh/your-org/your-repo/branch/main/graph/badge.svg?token=)](https://codecov.io/gh/your-org/your-repo)

A lightweight, macOS-focused clipboard manager built with PyQt6. It captures text copies, attributes them to the source application, and presents an app-aware UI with advanced developer-friendly utilities.

This README covers: installation, key features (Boards, Secret-safe mode, Pins, Search, Clip Actions), usage, configuration, developer notes, and troubleshooting.

---

Table of contents
- Project overview
- Features
- Quick start (macOS)
- UI walkthrough
- Security & Privacy
- CI and testing
- Configuration and settings
- Developer notes
- Tests and validation
- Troubleshooting
- Contributing & license

---

Project overview

This tool watches the macOS clipboard and records copied text together with metadata: source application and capture timestamp. The design separates capture, storage/deduplication, and UI so functionality can be extended safely and tested.

Design goals
- Correctness: avoid re-capturing programmatic copies and attribute the frontmost application at capture time.
- Efficiency: use Qt clipboard signals (no polling) for accuracy and low CPU usage.
- Security-aware: provide a Secret-safe mode that avoids storing sensitive content from password/auth apps and token-like clipboard contents.
- Productivity features: search, pins, boards (auto-routing), and developer-friendly clip actions.


Features

- Boards (auto-routing)
  - The app automatically routes clipboard content into a few boards (Links, Code, Commands, Notes, Other) using heuristics based on the source application and content.
  - Example heuristics: browser + URL → Links; Terminal → Commands; VS Code → Code.

- Secret-safe mode (trust)
  - Blocklisted apps (password managers, authenticators, Keychain entries) are not stored when Secret-safe mode is enabled.
  - Token/JWT heuristics: if clipboard content looks like a token (JWT or long base64-like string) it will be stored only temporarily and auto-removed after a configurable timeout.
  - The Secret-safe toggle and blocklist editor are available in the UI.

- Pins
  - Pin frequently used items; pinned items stay at the top of the list for the source app.
  - Pin/Unpin is available from the context menu.

- Search
  - A search box filters the visible history for the currently selected app/board.
  - The window can be shown & search focused via a hotkey (default: Ctrl+`).

- Clip Actions (developer-friendly)
  - Right-click an item to run transformations before copying to clipboard:
    - Trim whitespace
    - Copy as one-line
    - Extract URLs
    - JSON-escape (produce a JSON quoted/escaped string)
    - Convert to camelCase / snake_case

- Stable IDs & safe context menu actions
  - The UI stores a stable `ClipboardItem.id` in each list row (UserRole) so context menu actions operate on the intended record even if the history updates while the menu is open.


Quick start (macOS)

Prerequisites
- Python 3.11 (the codebase was developed and tested with Python 3.11 on macOS; newer 3.x versions should work but use caution)
- A Python virtual environment is recommended
- PyQt6 installed in the environment

Create and activate a venv, then install PyQt6:

```bash
# from project root
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install PyQt6
```

Run the GUI app:

```bash
# from project root, with venv active
python clipboard_manager/main.py
```

If you have an existing `.venv` in the repo, run the app using its Python binary:

```bash
.venv/bin/python clipboard_manager/main.py
```


UI walkthrough

Main controls
- Pause (ms): when the app programmatically copies text back to the clipboard, the watcher pauses capture for this duration (default 500 ms) to avoid re-capturing the same content.
- App dropdown: filter history by the source application. When no app is selected, the list is empty.
- Search box: filters the visible items for the selected app/board. It searches item content and board names.
- Secret-safe mode (checkbox): enable/disable the secret-safe heuristics.
- Edit Blocklist: opens a small editor where you can add/remove app name substrings to block from capture.
- Per-app capture toggle: enable or disable capture for the currently-selected app (useful to stop capturing from a specific app without blocking it globally).
- Context menu (right-click on an item): copy, clip actions (trim, one-line, extract URLs, JSON-escape, camel/snake), Pin/Unpin.

Hotkey
- An in-app hotkey (Ctrl+`) shows the window and focuses the search box; this is NOT a system-wide/global hotkey. If you need a global hotkey, see the "Developer notes" section for implementation suggestions.


Security & Privacy

Defaults
- Secret-safe mode is ON by default.
- Persistence is OFF by default (history, pins, and settings are stored in memory only unless you enable persistence explicitly).
- Common sensitive apps are pre-populated into the blocklist (password managers, authenticators, keychain-like apps).

Per-app controls
- The UI exposes a "Per-app capture" toggle which lets you enable or disable capturing for the currently-selected app without altering the global blocklist.

Security notes
- Token/JWT heuristics attempt to detect likely secrets and keep them temporary when Secret-safe mode is enabled; heuristics are conservative and may not catch all secrets. If you need stronger guarantees, avoid enabling persistence or implement secure encrypted storage.
- If you enable persistence, consider encrypting persisted data or storing only metadata (timestamps, app names) depending on your threat model.


Configuration and developer tuning

Configuration constants in `clipboard_manager/history.py`:
- `MAX_RECENT_HASHES` — LRU size for dedupe (default 200)
- `APP_DEDUPE_SECONDS` — per-app dedupe window (default 30 seconds)
- `TEMPORARY_TOKEN_SECONDS` — how long token-like clips are kept before auto-deletion (default 30 seconds)

Secret-safe blocklist
- Edit blocklist from the UI (Edit Blocklist) or programmatically via `History.set_blocklist(...)`.

Persistence
- This version keeps history and pins in memory only. If you want persistent history/pins, I can add optional JSON or SQLite persistence and a small migration path.


Developer notes & architecture

Key modules
- `clipboard_manager/watcher.py` — `ClipboardWatcher` emits `clipboard_changed(content, source_app, timestamp)` and exposes `pause(ms)`, `resume()`, and `set_text(text, pause_ms)`.
- `clipboard_manager/history.py` — `HistoryStore` handles dedupe, blocklist, token heuristics, temporary-marking and pin management. Exported alias: `History`.
- `clipboard_manager/boards.py` — `Board` enum and a `BoardRouter` that routes clipboard content to a board using app + content heuristics.
- `clipboard_manager/gui.py` — `MainWindow` renders the UI and uses stable item IDs for list rows.
- `clipboard_manager/clipboard_item.py` — `ClipboardItem` model: id, content, source_app, timestamp, board, is_temporary, expire_at, pinned.

Testing strategy
- Unit tests cover utilities and critical behavior (dedupe, secret-safe heuristics, pin/unpin ordering).
- A smoke test exercises `ClipboardWatcher` + `History` pause behavior without requiring a visible UI (`tests/smoke_pause_test.py`).

Running tests (no pytest required)
- The repo contains small test scripts that can be executed directly. Example:

```bash
python tests/test_utils.py
python tests/test_secret_safe.py
python tests/test_pins.py
python tests/smoke_pause_test.py
python tests/gui_startup.py  # non-blocking GUI startup check
```


CI and testing

This repository includes a GitHub Actions workflow that runs the test suite and enforces a minimum coverage threshold.

- Workflow file: `.github/workflows/ci.yml`
- Coverage requirement: the CI enforces a minimum coverage (default set to 70%). The workflow runs tests in a headless environment using `xvfb` so GUI tests (pytest-qt) run reliably.

Run tests locally with coverage (recommended):

```bash
# install test deps from repo
python3 -m pip install -r requirements.txt
# run pytest with coverage
pytest --cov=clipboard_manager --cov-report=term-missing
```

If you want to run GUI tests locally in an environment without a display, use Xvfb (Linux) or run on macOS directly:

```bash
# on Linux with Xvfb
sudo apt-get install xvfb
xvfb-run -s "-screen 0 1920x1080x24" pytest -q
```

If the CI badge link in the README is incorrect, replace the `your-org/your-repo` path with the actual GitHub owner and repository name to enable the badge.


Troubleshooting

Q: `ModuleNotFoundError: No module named 'PyQt6'` when running tests or app
- Ensure PyQt6 is installed into the Python interpreter you use (activate your venv and run `python -m pip install PyQt6`).

Q: `Unknown App` is shown as the source app
- The project uses an AppleScript call (`osascript`) to ask macOS which app is frontmost. If your environment restricts automation, this may fail and fallback to `Unknown App`.

Q: Items disappear (temporary tokens)
- Token/JWT-like content is removed automatically by design when Secret-safe mode is enabled (default 30 seconds). Disable Secret-safe mode to keep all clips.


Contributing

- Create a branch, add tests for behavior changes (HistoryStore unit tests are quick), run the test scripts, and open a PR.
- Helpful areas: persist history, image/rich clipboard support, improve token heuristics, better search (fuzzy matching), keyboard shortcuts.

License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
