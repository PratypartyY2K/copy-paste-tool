from clipboard_item import ClipboardItem

class History:
    def __init__(self):
        self.items = []

    def add_item(self, content, source_app="Unknown App"):
        # Avoid duplicate consecutive entries
        if self.items and self.items[0].content == content:
            return self.items[0]

        item = ClipboardItem(content, source_app)
        self.items.insert(0, item)
        return item

    def get_apps(self):
        """Return unique apps in history"""
        return sorted(set(item.source_app for item in self.items))

    def get_items_by_app(self, app_name):
        return [item for item in self.items if item.source_app == app_name]
