import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PyQt6.QtWidgets import QApplication
from clipboard_manager.gui import MainWindow

def main():
    app = QApplication([])
    w = MainWindow()
    w.show()
    # process one event loop iteration to ensure widgets initialize
    app.processEvents()
    print('GUI_STARTUP_OK')

if __name__ == '__main__':
    main()
