import sys
import os
from PyQt6.QtWidgets import QApplication
from gui import MainWindow

# optional persistence: set CLIP_PERSISTENCE_DB env var to enable
DB_PATH = os.environ.get('CLIP_PERSISTENCE_DB')
if DB_PATH:
    try:
        from clipboard_manager.storage import Persistence
        persistence = Persistence(DB_PATH)
    except Exception:
        persistence = None
else:
    persistence = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # inject persisted history when available
    if persistence:
        from clipboard_manager.history import History
        history = History(persistence=persistence)
        window = MainWindow(history=history)
    else:
        window = MainWindow()
    window.show()
    sys.exit(app.exec())
