from datetime import datetime
import uuid
from boards import Board

class ClipboardItem:
    def __init__(self, content, source_app="Unknown App", board: Board = None, is_temporary: bool = False, expire_at: float = None, pinned: bool = False):
        self.id = uuid.uuid4().hex
        self.content = content
        self.source_app = source_app
        self.timestamp = datetime.now()
        self.board = board or Board.OTHER
        self.is_temporary = is_temporary
        self.expire_at = expire_at
        self.pinned = pinned

    def __repr__(self):
        return "<ClipboardItem id={} app={} time={} board={} temporary={} pinned={}>".format(self.id, self.source_app, self.timestamp, self.board, self.is_temporary, self.pinned)
