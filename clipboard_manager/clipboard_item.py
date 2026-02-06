from datetime import datetime
import uuid

class ClipboardItem:
    def __init__(self, content, source_app="Unknown App", board=None, is_temporary: bool = False, expire_at: float = None, pinned: bool = False):
        self.id = uuid.uuid4().hex
        self.content = content
        self.source_app = source_app
        self.timestamp = datetime.now()
        # board is optional; None means boarding is disabled
        self.board = board if board is not None else None
        self.is_temporary = is_temporary
        self.expire_at = expire_at
        self.pinned = pinned

    def __repr__(self):
        return "<ClipboardItem id={} app={} time={} board={} temporary={} pinned={}>".format(self.id, self.source_app, self.timestamp, self.board, self.is_temporary, self.pinned)
