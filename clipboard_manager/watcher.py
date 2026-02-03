from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication
from utils import get_frontmost_app
import time

class ClipboardWatcher(QObject):
    clipboard_changed = pyqtSignal(str, str, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self._on_clipboard_change)
        self._ignore = False

    def _on_clipboard_change(self):
        if self._ignore:
            return
        text = self.clipboard.text()
        if not text:
            return
        ts = time.time()
        source_app = get_frontmost_app()
        self.clipboard_changed.emit(text, source_app, ts)

    def pause(self, ms=None):
        if ms is None:
            return
        self._ignore = True
        QTimer.singleShot(ms, self.resume)

    def resume(self):
        self._ignore = False

    def set_text(self, text, pause_ms=None):
        if pause_ms is not None:
            self.pause(pause_ms)
        self.clipboard.setText(text)
