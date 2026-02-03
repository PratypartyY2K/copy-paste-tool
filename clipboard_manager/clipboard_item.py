from datetime import datetime
import uuid

class ClipboardItem:
    def __init__(self, content, source_app="Unknown App"):
        self.id = uuid.uuid4().hex
        self.content = content
        self.source_app = source_app
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<ClipboardItem id={self.id} app={self.source_app} time={self.timestamp}>"
