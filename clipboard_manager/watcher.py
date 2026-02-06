from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication
from clipboard_manager.utils import get_frontmost_app, get_top_window_owners, is_pyobjc_available
import time
from datetime import datetime
import os
from collections import deque

# Tunable helpers (env-backed)
def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)))
    except Exception:
        return default

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except Exception:
        return default

# Default tunables
DEFAULT_LOOKBACK = _env_float('CP_LOOKBACK_SECONDS', 2.5)
DEFAULT_FREQ_LOOKBACK = _env_float('CP_FREQ_LOOKBACK_SECONDS', 5.0)
OWNER_MIN_SCORE = _env_int('CP_MIN_OWNER_SCORE', 0)
OWNER_WEIGHT_BROWSER = _env_int('CP_WEIGHT_BROWSER', 50)
OWNER_WEIGHT_COMM = _env_int('CP_WEIGHT_COMM', 30)
OWNER_WEIGHT_IDE = _env_int('CP_WEIGHT_IDE', 20)
OWNER_CONTENT_BOOST = _env_int('CP_WEIGHT_CONTENT_BOOST', 25)
OWNER_CODE_BOOST = _env_int('CP_WEIGHT_CODE_BOOST', 30)

class ClipboardWatcher(QObject):
    clipboard_changed = pyqtSignal(str, str, float)

    def __init__(self, parent=None):
        super(ClipboardWatcher, self).__init__(parent)
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self._on_clipboard_change)
        self._ignore_until = 0.0

        # derive names that represent this running process to avoid self-attribution
        try:
            import sys
            self._self_names = set([os.path.basename(sys.executable).lower(), os.path.splitext(os.path.basename(sys.argv[0]))[0].lower(), 'python', 'python3', 'clipboard'])
        except Exception:
            self._self_names = set(['python', 'python3', 'clipboard'])

        # macOS clipboard attribution is timing-sensitive: by the time Qt emits dataChanged,
        # focus has often already switched (commonly to the IDE / this app), causing mis-attribution.
        # We continuously sample the frontmost app and keep a short history so we can attribute
        # the clipboard change to the most recently-active *non-self* app.
        self._app_history = deque(maxlen=80)  # (timestamp, app_name)
        self._last_sampled_app = None

        # If pyobjc is available on macOS, register for NSWorkspace activation notifications
        # for deterministic frontmost-app events. Otherwise fall back to periodic sampling.
        self._use_appkit_notifications = False
        try:
            if is_pyobjc_available():
                # Setup AppKit observer lazily (import inside try to avoid import-time failures)
                try:
                    from AppKit import NSWorkspace, NSWorkspaceDidActivateApplicationNotification
                    from Foundation import NSObject
                    import objc

                    class _AppkitObserver(NSObject):
                        def initWithWatcher_(self, watcher):
                            self = objc.super(_AppkitObserver, self).init()
                            if self is None:
                                return None
                            self._watcher = watcher
                            return self

                        def appActivated_(self, notification):
                            try:
                                info = notification.userInfo()
                                app = info.get('NSWorkspaceApplicationKey') if info else None
                                if app is not None:
                                    try:
                                        name = app.localizedName()
                                    except Exception:
                                        name = None
                                    if name:
                                        self._watcher._record_app(str(name))
                            except Exception:
                                pass

                    # register observer
                    self._appkit_observer = _AppkitObserver.alloc().initWithWatcher_(self)
                    nc = NSWorkspace.sharedWorkspace().notificationCenter()
                    nc.addObserver_selector_name_object_(self._appkit_observer, 'appActivated:', NSWorkspaceDidActivateApplicationNotification, None)
                    self._use_appkit_notifications = True
                except Exception:
                    # Import failed; fall back to timer-based sampling
                    self._use_appkit_notifications = False
        except Exception:
            self._use_appkit_notifications = False

        if not self._use_appkit_notifications:
            self._app_timer = QTimer(self)
            self._app_timer.timeout.connect(self._capture_active_app)
            self._app_timer.start(150)  # ms; low overhead, good enough for attribution

        # Seed history with current frontmost app to avoid empty-history at startup
        try:
            try:
                initial = get_frontmost_app()
            except Exception:
                initial = None
            if initial and 'python' not in initial.lower():
                norm_initial = self._normalize_app_name(initial)
                nl_init = norm_initial.lower() if norm_initial else ''
                if norm_initial and nl_init.strip() and not any(sn in nl_init for sn in self._self_names) and not any(ign in nl_init for ign in self._IGNORED_OWNERS):
                    self._app_history.append((time.time(), norm_initial))
                    self._last_sampled_app = norm_initial
        except Exception:
            pass


    def _record_app(self, app_name: str):
        """Record an app activation event from AppKit observer. Respect pause/ignore windows."""
        try:
            if not app_name:
                return
            if time.time() < self._ignore_until:
                return
            norm = self._normalize_app_name(app_name)
            nl = norm.lower() if norm else ''
            if not norm or nl.strip() == '':
                return
            # ignore self process names and noisy/system owners
            if any(sn in nl for sn in self._self_names):
                return
            if any(ign in nl for ign in self._IGNORED_OWNERS):
                return
            # Only record on change to keep history meaningful
            if norm != self._last_sampled_app:
                self._last_sampled_app = norm
                self._app_history.append((time.time(), norm))
        except Exception:
            pass


    def _capture_active_app(self):
        """Continuously sample the currently-frontmost app (best-effort) and record changes."""
        try:
            app = get_frontmost_app()
        except Exception:
            app = None
        if not app:
            return
        norm = self._normalize_app_name(app)
        nl = norm.lower() if norm else ''
        if not norm or nl.strip() == '':
            return
        if any(sn in nl for sn in self._self_names):
            return
        if any(ign in nl for ign in self._IGNORED_OWNERS):
            return
        if norm != self._last_sampled_app:
            self._last_sampled_app = norm
            self._app_history.append((time.time(), norm))

    # Normalization map (substring -> canonical name)
    _NORMALIZE_MAP = [
        ("visual studio code", "Visual Studio Code"),
        ("code -", "Visual Studio Code"),
        ("code", "Visual Studio Code"),
        ("pycharm", "PyCharm"),
        ("brave", "Brave Browser"),
        ("chrome", "Chrome"),
        ("safari", "Safari"),
        ("firefox", "Firefox"),
        ("discord", "Discord"),
        ("notion", "Notion"),
        ("outlook", "Microsoft Outlook"),
        ("whatsapp", "WhatsApp"),
        ("slack", "Slack"),
        ("teams", "Microsoft Teams"),
    ]

    # Owner blacklist (lowercase substrings to ignore or penalize heavily)
    _IGNORED_OWNERS = [
        'window server', 'grace', 'displaylink', 'display link', 'control center', 'grizzly', 'grap', 'grm', 'gr', 'dock',
        'fontd', 'kernel_task'
    ]

    def _normalize_app_name(self, name: str) -> str:
        if not name:
            return name
        n = name.strip()
        nl = n.lower()
        for k, v in self._NORMALIZE_MAP:
            if k in nl:
                return v
        return n

    def score_owner(self, owner_name: str, text_lower: str, allow_ide: bool, code_like: bool) -> int:
        """Score a top-window owner name based on heuristics and tunables."""
        if not owner_name:
            return -999
        n = owner_name.lower()
        # ignore self/terminal/python processes
        if any(k in n for k in ('clipboard', 'copy-paste-tool', 'python', 'python3', 'terminal', 'iterm')):
            return -999
        # penalize ignored owners
        if any(ign in n for ign in self._IGNORED_OWNERS):
            return -999
        score = 0
        # browsers
        if any(k in n for k in ('brave', 'chrome', 'safari', 'firefox', 'edge', 'opera')):
            score += OWNER_WEIGHT_BROWSER
        # communication apps
        if any(k in n for k in ('discord', 'slack', 'teams')):
            score += OWNER_WEIGHT_COMM
        # IDEs
        if any(k in n for k in ('pycharm', 'intellij', 'vscode', 'sublime', 'atom', 'webstorm', 'visual studio code')):
            score += OWNER_WEIGHT_IDE
        # small non-empty boost
        score += 1
        # content boosts
        if text_lower:
            if any(tok in text_lower for tok in ('http://', 'https://', 'www.')) and any(k in n for k in ('brave', 'chrome', 'safari', 'firefox', 'edge', 'opera')):
                score += OWNER_CONTENT_BOOST
            if code_like and any(k in n for k in ('pycharm', 'intellij', 'vscode', 'sublime')):
                score += OWNER_CODE_BOOST
            # slight boost if owner contains words from snippet
            try:
                for part in text_lower.split():
                    if part and part in n:
                        score += 2
            except Exception:
                pass
        return score

    def _pick_recent_source_app(self, ts: float, *, allow_ide: bool, code_like: bool = False, language_hint: str | None = None) -> str | None:
        """Pick the most likely source app from recent focus history using recency+frequency scoring.

        Returns canonicalized app name or None.
        """
        LOOKBACK = DEFAULT_LOOKBACK

        # helpers to classify names
        def is_browser_name(n: str) -> bool:
            nl = n.lower()
            return any(k in nl for k in ('brave', 'chrome', 'safari', 'firefox', 'edge', 'opera'))

        def is_comm_name(n: str) -> bool:
            nl = n.lower()
            return any(k in nl for k in ('discord', 'slack', 'teams', 'whatsapp', 'notion', 'outlook'))

        def is_ide(name: str) -> bool:
            n = name.lower()
            return any(k in n for k in ('pycharm', 'intellij', 'idea', 'webstorm', 'goland', 'clion', 'rider', 'vscode', 'visual studio code', 'sublime', 'atom'))

        def is_self(name: str) -> bool:
            n = name.lower()
            return any(k in n for k in ('clipboard', 'copy-paste-tool', 'python', 'python3', 'terminal', 'iterm'))

        if not self._app_history:
            return None

        cutoff = ts - LOOKBACK
        # 1) If code-like content, prefer an IDE that matches the detected language
        if code_like:
            # mapping from language_hint to IDE substrings to prefer
            lang_map = {
                'python': ('pycharm', 'intellij'),
                'javascript': ('vscode', 'visual studio code', 'webstorm'),
                'js': ('vscode', 'visual studio code', 'webstorm'),
            }
            preferred_ides = ()
            if language_hint and language_hint in lang_map:
                preferred_ides = lang_map[language_hint]
            # Strong rule: if language_hint given, try to find the canonical IDE name present in history and return its most recent occurrence
            if language_hint:
                canonical_map = {
                    'python': 'PyCharm',
                    'javascript': 'Visual Studio Code',
                    'js': 'Visual Studio Code',
                }
                target = canonical_map.get(language_hint)
                if target:
                    # find most recent occurrence of target in history within a wider freq lookback
                    freq_cutoff = ts - DEFAULT_FREQ_LOOKBACK
                    for t, name in reversed(self._app_history):
                        if t < freq_cutoff:
                            break
                        if not name:
                            continue
                        if is_self(name):
                            continue
                        if any(ign in name.lower() for ign in self._IGNORED_OWNERS):
                            continue
                        if target.lower() in name.lower():
                            return self._normalize_app_name(name)
            # first try to find most-recent preferred IDE
            if preferred_ides:
                for t, name in reversed(self._app_history):
                    if t < cutoff:
                        break
                    if not name:
                        continue
                    if is_self(name):
                        continue
                    if any(ign in name.lower() for ign in self._IGNORED_OWNERS):
                        continue
                    nl = name.lower()
                    if any(pid in nl for pid in preferred_ides):
                        return self._normalize_app_name(name)
            # otherwise fallback to any IDE most recent
            for t, name in reversed(self._app_history):
                if t < cutoff:
                    break
                if not name:
                    continue
                if is_self(name):
                    continue
                if any(ign in name.lower() for ign in self._IGNORED_OWNERS):
                    continue
                if is_ide(name):
                    return self._normalize_app_name(name)

        # 2) If URL-like content (caller may pass this), prefer most-recent browser
        # Note: caller currently doesn't pass url_like; we'll handle simple content heuristics here
        # but keep backward compatibility by checking code_like only.
        # collect candidates within lookback window
        freq = {}
        last_seen = {}
        for t, name in self._app_history:
            if not name:
                continue
            if t < cutoff:
                continue
            nl = name.lower()
            if is_self(name):
                continue
            if any(ign in nl for ign in self._IGNORED_OWNERS):
                continue
            key = self._normalize_app_name(name)
            freq[key] = freq.get(key, 0) + 1
            last_seen[key] = max(last_seen.get(key, 0), t)

        if not freq:
            return None

        # Strong rule: if language_hint maps to a canonical IDE and it's present in recent freq, prefer it
        if language_hint:
            canonical_map = {
                'python': 'PyCharm',
                'javascript': 'Visual Studio Code',
                'js': 'Visual Studio Code',
            }
            tgt = canonical_map.get(language_hint)
            if tgt:
                for k in freq.keys():
                    if tgt.lower() in k.lower() or k.lower() in tgt.lower():
                        return tgt

        # 3) Prefer the most recent non-IDE app (good for notes/communication)
        for t, name in reversed(self._app_history):
            if t < cutoff:
                break
            if not name:
                continue
            if is_self(name):
                continue
            if any(ign in name.lower() for ign in self._IGNORED_OWNERS):
                continue
            if not is_ide(name):
                return self._normalize_app_name(name)

        # 4) Fallback: score by recency+frequency as before
        best = None
        best_score = -1.0
        now = ts
        total = sum(freq.values())
        for name, count in freq.items():
            recency = now - last_seen.get(name, now)
            recency_score = 1.0 / (1.0 + recency)
            score = recency_score * 0.7 + (count / max(1, total)) * 0.3
            if is_ide(name) and allow_ide:
                score += 0.15 + (0.6 if code_like else 0.0)
            if score > best_score:
                best_score = score
                best = name

        return best

    def _on_clipboard_change(self):
        try:
            now = time.time()
            if now < self._ignore_until:
                return
        except RuntimeError:
            if os.environ.get('CLIP_DEBUG') == '2':
                print('[clip-debug] _on_clipboard_change called on uninitialized watcher; ignoring')
            return
        except Exception:
            return

        text = self.clipboard.text()
        if not text:
            return
        ts = now

        # Emit Unknown immediately to avoid blocking the UI. Compute refined attribution in background
        # and re-emit the result once available.
        try:
            # fast debug dump
            if os.environ.get('CLIP_DEBUG') == '2':
                print('--- clip-debug-verbose ---')
                print('timestamp:', datetime.fromtimestamp(ts).isoformat())
                # Avoid calling get_frontmost_app here; it's blocking (osascript/AppKit) and
                # can introduce delays when debug is enabled. Rely on last_sampled_app and history.
                print('frontmost_probe: <skipped in debug to avoid blocking>')
                print('last_sampled_app:', self._last_sampled_app)
                try:
                    owners_preview = get_top_window_owners(6)
                except Exception:
                    owners_preview = []
                try:
                    history_preview = list(self._app_history)[-6:]
                except Exception:
                    history_preview = []
                print('owners_preview:', owners_preview)
                print('history_preview:', history_preview)
                print('emitting placeholder: Unknown App')
                print('--- end ---')
        except Exception:
            pass

        # Choose the history entry nearest to the clipboard timestamp within window.
        # Prefer the most recent entry at or before ts (within pre_margin); otherwise
        # accept the earliest entry after ts within post_margin.
        pre_ms = int(os.environ.get('CP_PRE_MARGIN_MS', '500') or '500')
        post_ms = int(os.environ.get('CP_POST_MARGIN_MS', '50') or '50')
        pre_margin = float(pre_ms) / 1000.0
        post_margin = float(post_ms) / 1000.0
        chosen = None
        try:
            # collect candidates within [ts - pre_margin, ts + post_margin]
            candidates = []
            for t, name in self._app_history:
                try:
                    if not name or not name.strip():
                        continue
                    if t >= (ts - pre_margin) and t <= (ts + post_margin):
                        candidates.append((t, name))
                except Exception:
                    continue
            if candidates:
                # Score candidates by recency and type weight to prefer browsers/IDEs over communication apps
                def type_weight(name):
                    nl = name.lower()
                    if any(k in nl for k in ('brave', 'chrome', 'safari', 'firefox', 'edge', 'opera')):
                        return 0.6
                    if any(k in nl for k in ('pycharm', 'intellij', 'vscode', 'visual studio code', 'sublime', 'atom', 'webstorm')):
                        return 0.4
                    if any(k in nl for k in ('discord', 'slack', 'teams', 'whatsapp')):
                        return 0.1
                    return 0.2

                best_score = None
                best_candidate = None
                for (t, name) in candidates:
                    try:
                        dt = abs(t - ts)
                        recency_score = 1.0 / (1.0 + dt)
                        weight = type_weight(name)
                        score = recency_score + weight
                        if best_score is None or score > best_score:
                            best_score = score
                            best_candidate = name
                    except Exception:
                        continue
                chosen = best_candidate
        except Exception:
            pass

        # Final deterministic emit: prefer chosen history candidate, then last_sampled_app, then Unknown
        self._ignore_until = ts + 0.1  # ignore brief bursts
        final_app = None
        if chosen:
            final_app = self._normalize_app_name(chosen)
        elif self._last_sampled_app:
            final_app = self._normalize_app_name(self._last_sampled_app)
        else:
            final_app = 'Unknown App'

        if os.environ.get('CLIP_DEBUG') == '2':
            print("[clip-debug] %s final_emit app=%s" % (datetime.fromtimestamp(ts).isoformat(), final_app))

        # debug output: include short preview of text to help diagnose missing items/delays
        if os.environ.get('CLIP_DEBUG') == '2':
            try:
                preview = (text or '')[:200].replace('\n', '\\n')
            except Exception:
                preview = ''
            print("[clip-debug] emitting text_preview=\"%s\" app=%s ts=%s" % (preview, final_app, datetime.fromtimestamp(ts).isoformat()))

        try:
            self.clipboard_changed.emit(text, final_app, ts)
        except Exception:
            pass

    def pause(self, ms=None):
        if ms is None:
            return
        try:
            ms = float(ms)
        except Exception:
            return
        self._ignore_until = time.time() + (ms / 1000.0)

    def set_text(self, text: str, pause_ms: int = 300):
        """Set clipboard text programmatically and pause capture to avoid self-attribution."""
        try:
            cb = QApplication.clipboard()
            cb.setText(str(text))
        except Exception:
            pass
        try:
            # pause capture briefly
            self.pause(pause_ms)
            if os.environ.get('CLIP_DEBUG') == '2':
                print("[clip-debug] set_text called; paused for %d ms" % (pause_ms,))
        except Exception:
            pass
