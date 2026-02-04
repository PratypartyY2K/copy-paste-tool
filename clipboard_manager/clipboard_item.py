from datetime import datetime
import uuid
from boards import Board

class ClipboardItem:
    def __init__(self, content, source_app="Unknown App", board: Board = None):
        self.id = uuid.uuid4().hex
        self.content = content
        self.source_app = source_app
        self.timestamp = datetime.now()
        # If board not provided default to OTHER to ensure attribute exists
        self.board = board or Board.OTHER

    def __repr__(self):
        return "<ClipboardItem id={} app={} time={} board={}>".format(self.id, self.source_app, self.timestamp, self.board)
