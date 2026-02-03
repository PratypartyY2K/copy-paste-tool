# App-Aware Clipboard Manager

A small, macOS-focused clipboard manager built with PyQt6 that tracks multiple copied items across applications and presents an app-filtered clipboard history. The project separates the capture pipeline (clipboard watcher), storage/dedupe logic (history store), and the UI so features can be extended without coupling concerns.

---

Table of contents
- Project overview
- Quick start
- Architecture and key modules
- Features and behavior
- Configuration and UI controls
- Development and testing
- Troubleshooting & FAQ
- Contributing
- License

---

Project overview

This tool watches the macOS clipboard and records copied text along with which application it came from and a timestamp. The UI lists clipboard entries and lets you filter by source application and copy items back to the system clipboard.

The design goals are:
- Correctness: avoid re-capturing programmatic copies and avoid attribution races.
- Efficiency: use Qt clipboard signals (no polling) whenever possible.
- Extensibility: keep capture, storage (dedupe), and UI separated so each can be extended independently.

Quick start (macOS)

Prerequisites
- Python 3.11 (project tested with Python 3.11 on macOS)
- A working Python virtual environment is strongly recommended
- PyQt6 installed in the environment

Recommended quick commands

Create/activate a virtual environment and install UI dependency:

```bash
# from project root
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install PyQt6
```

Run the GUI (from project root):

```bash
# Use the environment Python to run the app entrypoint
.venv/bin/python clipboard_manager/main.py
```

If you already have a `.venv` in the project (created previously), use that Python binary directly, for example:

```bash
/Users/you/path/to/copy-paste-tool/.venv/bin/python clipboard_manager/main.py
```

Architecture and key modules

The code is intentionally split into three responsibilities:

1. Clipboard watcher (capture pipeline)
   - File: `clipboard_manager/watcher.py`
   - Class: `ClipboardWatcher` (a Qt `QObject`) that emits a `clipboard_changed` signal with `(content, source_app, timestamp)` when clipboard data changes.
   - Provides `pause(ms)` / `resume()` and `set_text(text, pause_ms)` helpers so the UI or other controllers can programmatically write the clipboard without re-capturing their own writes.
   - Uses `QApplication.clipboard().dataChanged` for efficient signal-based detection.

2. History store (storage & dedupe)
   - File: `clipboard_manager/history.py` (class `HistoryStore`, exported as `History` for convenience)
   - Handles dedupe with a combined approach:
     - A small global LRU of recent content hashes (default 200) to prevent repeated inserts of the same text even if other clips occur in between.
     - A per-app recent-time window (default 30 seconds) to avoid recording identical content from the same app repeatedly in a short period.
   - Accepts a `timestamp` when adding items so the watcher can provide accurate capture times.
   - Exposes `add_item(content, source_app, timestamp=None)`, `get_apps()`, `get_items_by_app(app_name)`, and `get_item_by_id(item_id)`.

3. UI (presentation)
   - File: `clipboard_manager/gui.py`
   - Class: `MainWindow` (PyQt6 QMainWindow) renders the history and app dropdown, subscribes to `ClipboardWatcher.clipboard_changed`, and delegates storage to `History`.
   - Each list row stores the stable `ClipboardItem.id` in Qt `UserRole` so UI actions refer to items by ID (not by index) which prevents mismatches if the history updates while a context menu is open.
   - Provides a small control `Pause (ms)` to configure how long the watcher ignores clipboard changes after programmatic writes.

Additional files
- `clipboard_manager/clipboard_item.py` — `ClipboardItem` data model (has stable `id`, `content`, `source_app`, `timestamp`).
- `clipboard_manager/main.py` — application entrypoint that creates the QApplication and `MainWindow`.
- `tests/smoke_pause_test.py` — a lightweight smoke test that exercises `ClipboardWatcher` + `History` behavior (no GUI interaction required).
- `requirements.txt` — a long pinned list used for other development work; the app itself needs PyQt6 at minimum.

Features and behavior

- Signal-based clipboard capture (no 500ms polling). This reduces CPU usage and improves accuracy when attributing the frontmost app at capture time.
- Programmatic copy protection: when the app copies an item back to the clipboard, it briefly pauses capture so the app does not re-record its own copy operation.
- Configurable pause: the UI exposes a `Pause (ms)` spinbox (default 500 ms). You can tune this to match your environment.
- Robust dedupe: avoids duplicate history entries using both an LRU cache of recent content hashes and per-app time-window dedupe.
- Stable IDs: list rows store stable item IDs (not indexes), preventing UI race conditions when acting on a row after history updates.

Configuration and UI controls

From the main window:
- Pause (ms): default 500 ms. When you copy an item from the UI back to the system clipboard, the watcher will ignore clipboard changes for this duration.

Dedupe tuning (developer-level)
- `MAX_RECENT_HASHES` (in `clipboard_manager/history.py`) — maximum recent distinct content hashes to remember (default 200).
- `APP_DEDUPE_SECONDS` — per-app time window to avoid re-capturing identical content (default 30 seconds).

Development and testing

Run the smoke test (recommended after code changes):

```bash
.venv/bin/python tests/smoke_pause_test.py
```

Notes on running tests
- The smoke test constructs `ClipboardWatcher` and `History` directly and simulates clipboard changes; it does not require the GUI to be visible.
- For more complex integration tests that exercise the GUI, you'll need a display (or a headless X server) and tests that can interact with Qt event loop.

Troubleshooting & FAQ

Q: The app doesn't show items when I copy from another app.
- Make sure the app has permissions needed to interact with the clipboard and run AppleScript if your environment restricts automation.
- Confirm PyQt6 is installed in the Python interpreter you're using to run the app.

Q: The source app name looks wrong or is reported as `Unknown App`.
- The project uses an AppleScript snippet (via `osascript`) to ask macOS for the frontmost application. In some restricted environments or sandboxed contexts that may fail — the watcher falls back to `Unknown App` in that case.

Q: I see duplicates still — how do I tune dedupe?
- Increase `MAX_RECENT_HASHES` in `clipboard_manager/history.py` to remember more distinct recent content.
- Increase `APP_DEDUPE_SECONDS` to widen the per-app duplicate window.
- Optionally normalize content before adding (e.g., strip whitespace, casefold) if you want similar values to dedupe.

Contributing

Contributions are welcome. A suggested workflow:
1. Create a branch for your feature/fix.
2. Add tests for your changes (unit tests for `HistoryStore` are easy and fast).
3. Open a pull request and describe the change and rationale.

One small set of areas that will be helpful:
- Persisting history between runs (JSON, sqlite, or similar).
- Image and rich-text clipboard support.
- Search and pinning features in the UI.

License

This repository doesn't include a formal license file by default. Add a `LICENSE` file (for example MIT) if you intend to permit reuse.

---

If you'd like, I can also:
- Add a short `DEVELOPMENT.md` with step-by-step dev tasks and how to run the app in a debugger.
- Add unit tests for `HistoryStore` that explicitly cover LRU trimming and per-app dedupe windows.
- Add persisted history storage (JSON/SQLite) with a small migration strategy.


Last updated: 2026-02-03
