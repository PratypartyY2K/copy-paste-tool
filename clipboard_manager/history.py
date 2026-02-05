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
# Default temporary storage seconds for token-like clipboard captures
TEMPORARY_TOKEN_SECONDS = 30
# Apps to block entirely from being stored (password managers, authenticators, keychain UIs)
BLOCKLIST_APPS = {
    '1password', '1password 8', 'lastpass', 'bitwarden', 'dashlane', 'keepassxc', 'keepass', 'google authenticator', 'authy', 'keychain', 'password manager'
}

# Simple token/JWT heuristics
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

    def _start_cleanup_thread(self):
        if self._cleanup_thread is not None and self._cleanup_thread.is_alive():
            return
        self._cleanup_event.clear()
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def _cleanup_loop(self):
        # Run until the event is set
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
        # tokens often have lots of punctuation-free long sequences
        return False

    def _is_blocked_app(self, app_name: str) -> bool:
        if not app_name:
            return False
        n = app_name.lower()
        for bad in BLOCKLIST_APPS:
            if bad in n:
                return True
        return False

    def add_item(self, content, source_app="Unknown App", timestamp=None):
        if not content:
            return None

        # Blocklist apps entirely
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

            # Create item and assign board using BoardRouter
            is_temp = False
            expire_at = None
            if self._looks_like_token(content):
                # Token-like content -> mark temporary
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

            # Insert at front
            self.items.insert(0, item)
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

            # Start cleanup thread if needed
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

History = HistoryStore
