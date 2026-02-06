import sys
import os
import pathlib
project_root = pathlib.Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from clipboard_manager.gui import MainWindow

NO_GUI = os.environ.get('CLIP_NO_GUI') == '1' or '--no-gui' in sys.argv

DB_PATH = os.environ.get('CLIP_PERSISTENCE_DB')
if DB_PATH:
    try:
        from clipboard_manager.storage import Persistence
        persistence = Persistence(DB_PATH)
    except Exception:
        persistence = None
else:
    persistence = None

if __name__ == '__main__':
    if NO_GUI:
        print('NO_GUI')
        sys.exit(0)
    app = QApplication(sys.argv)
    if persistence:
        from clipboard_manager.history import History
        history = History(persistence=persistence)
        window = MainWindow(history=history)
    else:
        window = MainWindow()
    window.show()
    rc = app.exec()
    try:
        if persistence:
            persistence.close()
    except Exception:
        pass
    sys.exit(rc)
