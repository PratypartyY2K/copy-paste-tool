from clipboard_manager.clipboard_item import ClipboardItem
from collections import OrderedDict
import hashlib
import time
from datetime import datetime
from clipboard_manager.boards import BoardRouter
import threading
import re

MAX_RECENT_HASHES = 200
APP_DEDUPE_SECONDS = 30
TEMPORARY_TOKEN_SECONDS = 30
BLOCKLIST_DEFAULTS = {
    '1password', '1password 8', 'lastpass', 'bitwarden', 'dashlane', 'keepassxc', 'keepass', 'google authenticator', 'authy', 'keychain', 'password manager'
}

_JWT_RE = re.compile(r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$")
_LONG_BASE64_RE = re.compile(r"^[A-Za-z0-9-_]{40,}$")

class HistoryStore:
    def __init__(self):
        self.items = []
        self._recent_hashes = OrderedDict()
        self._last_seen_by_app = {}
        self._items_by_id = {}
        self._lock = threading.RLock()
        self._cleanup_thread = None
        self._cleanup_event = threading.Event()

        self.secret_safe_enabled = True
        self.blocklist_apps = set(BLOCKLIST_DEFAULTS)

    def get_blocklist(self):
        """Return a sorted list copy of configured blocklist substrings."""
        with self._lock:
            return sorted(self.blocklist_apps)

    def set_blocklist(self, entries):
        """Replace blocklist with an iterable of strings."""
        with self._lock:
            self.blocklist_apps = set(e.strip().lower() for e in entries if e and e.strip())

    def set_secret_safe_enabled(self, enabled: bool):
        with self._lock:
            self.secret_safe_enabled = bool(enabled)

    def get_secret_safe_enabled(self) -> bool:
        with self._lock:
            return bool(self.secret_safe_enabled)

    def _start_cleanup_thread(self):
        if self._cleanup_thread is not None and self._cleanup_thread.is_alive():
            return
        self._cleanup_event.clear()
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def _cleanup_loop(self):
        while not self._cleanup_event.wait(timeout=2.0):
            now = time.time()
            removed = False
            with self._lock:
                new_items = []
                for it in self.items:
                    if getattr(it, 'is_temporary', False) and getattr(it, 'expire_at', None) is not None:
                        if now >= it.expire_at:
                            try:
                                del self._items_by_id[it.id]
                            except Exception:
                                pass
                            removed = True
                            continue
                    new_items.append(it)
                if removed:
                    self.items = new_items

    def stop_cleanup(self):
        self._cleanup_event.set()
        if self._cleanup_thread is not None:
            self._cleanup_thread.join(timeout=1.0)

    def _looks_like_token(self, text: str) -> bool:
        if not text:
            return False
        t = text.strip()
        if _JWT_RE.match(t):
            return True
        if _LONG_BASE64_RE.match(t):
            return True
        return False

    def _is_blocked_app(self, app_name: str) -> bool:
        if not app_name:
            return False
        if not self.secret_safe_enabled:
            return False
        n = app_name.lower()
        for bad in self.blocklist_apps:
            if bad in n:
                return True
        return False

    def add_item(self, content, source_app="Unknown App", timestamp=None):
        if not content:
            return None

        if self._is_blocked_app(source_app):
            return None

        h = hashlib.sha256(content.encode('utf-8')).hexdigest()
        now = time.time()

        with self._lock:
            if h in self._recent_hashes:
                for it in self.items:
                    if it.content == content:
                        try:
                            self._recent_hashes.move_to_end(h, last=False)
                        except Exception:
                            pass
                        return it

            last_seen = self._last_seen_by_app.get((source_app, h))
            if last_seen is not None and (now - last_seen) <= APP_DEDUPE_SECONDS:
                for it in self.items:
                    if it.content == content and it.source_app == source_app:
                        self._last_seen_by_app[(source_app, h)] = now
                        return it
                self._last_seen_by_app[(source_app, h)] = now
                return None

            is_temp = False
            expire_at = None
            if self.secret_safe_enabled and self._looks_like_token(content):
                is_temp = True
                expire_at = now + TEMPORARY_TOKEN_SECONDS

            item = ClipboardItem(content, source_app, is_temporary=is_temp, expire_at=expire_at)
            try:
                BoardRouter.assign_board_to_item(item)
            except Exception:
                pass

            if timestamp is not None:
                try:
                    item.timestamp = datetime.fromtimestamp(timestamp)
                except Exception:
                    pass

            if getattr(item, 'pinned', False):
                idx = 0
                while idx < len(self.items) and getattr(self.items[idx], 'pinned', False):
                    idx += 1
                self.items.insert(idx, item)
            else:
                idx = 0
                while idx < len(self.items) and getattr(self.items[idx], 'pinned', False):
                    idx += 1
                self.items.insert(idx, item)
            try:
                self._items_by_id[item.id] = item
            except Exception:
                pass

            try:
                if h in self._recent_hashes:
                    del self._recent_hashes[h]
                self._recent_hashes[h] = now
                while len(self._recent_hashes) > MAX_RECENT_HASHES:
                    self._recent_hashes.popitem(last=False)
            except Exception:
                pass

            self._last_seen_by_app[(source_app, h)] = now

            if is_temp:
                self._start_cleanup_thread()

            return item

    def get_item_by_id(self, item_id):
        with self._lock:
            return self._items_by_id.get(item_id)

    def get_apps(self):
        with self._lock:
            return sorted(set(item.source_app for item in self.items))

    def get_items_by_app(self, app_name):
        with self._lock:
            return [item for item in self.items if item.source_app == app_name]

    def pin_item(self, item_id):
        with self._lock:
            item = self._items_by_id.get(item_id)
            if not item:
                return False
            item.pinned = True
            try:
                self.items = [i for i in self.items if i.id != item_id]
                idx = 0
                while idx < len(self.items) and getattr(self.items[idx], 'pinned', False):
                    idx += 1
                self.items.insert(idx, item)
                return True
            except Exception:
                return False

    def unpin_item(self, item_id):
        with self._lock:
            item = self._items_by_id.get(item_id)
            if not item:
                return False
            item.pinned = False
            try:
                self.items = [i for i in self.items if i.id != item_id]
                idx = 0
                while idx < len(self.items) and getattr(self.items[idx], 'pinned', False):
                    idx += 1
                while idx < len(self.items) and self.items[idx].timestamp > item.timestamp:
                    idx += 1
                self.items.insert(idx, item)
                return True
            except Exception:
                return False

History = HistoryStore
