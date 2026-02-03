from clipboard_item import ClipboardItem
from collections import OrderedDict
import hashlib
import time

MAX_RECENT_HASHES = 200
APP_DEDUPE_SECONDS = 30

class History:
    def __init__(self):
        self.items = []
        self._recent_hashes = OrderedDict()
        self._last_seen_by_app = {}

    def add_item(self, content, source_app="Unknown App"):
        if not content:
            return None

        h = hashlib.sha256(content.encode('utf-8')).hexdigest()
        now = time.time()

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
                    return it
            self._last_seen_by_app[(source_app, h)] = now
            return None

        item = ClipboardItem(content, source_app)
        self.items.insert(0, item)

        try:
            if h in self._recent_hashes:
                del self._recent_hashes[h]
            self._recent_hashes[h] = now
            while len(self._recent_hashes) > MAX_RECENT_HASHES:
                self._recent_hashes.popitem(last=False)
        except Exception:
            pass

        self._last_seen_by_app[(source_app, h)] = now

        return item

    def get_apps(self):
        return sorted(set(item.source_app for item in self.items))

    def get_items_by_app(self, app_name):
        return [item for item in self.items if item.source_app == app_name]
