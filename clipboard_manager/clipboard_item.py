from datetime import datetime

class ClipboardItem:
    def __init__(self, content, source_app="Unknown App"):
        self.content = content
        self.source_app = source_app
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<ClipboardItem app={self.source_app} time={self.timestamp}>"
