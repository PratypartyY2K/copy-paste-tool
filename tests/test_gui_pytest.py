import pytest
from PyQt6.QtWidgets import QApplication
from clipboard_manager.gui import MainWindow

pytestmark = pytest.mark.gui

@pytest.fixture(scope='session')
def app():
    app = QApplication.instance() or QApplication([])
    return app

def test_mainwindow_startup(app, qtbot):
    w = MainWindow()
    qtbot.addWidget(w)
    w.show()
    assert w.windowTitle() == 'App-Aware Clipboard Manager'
    # ensure key widgets exist
    assert hasattr(w, 'app_dropdown')
    assert hasattr(w, 'list_widget')
    w.close()

def test_search_focus_hotkey(app, qtbot):
    w = MainWindow()
    qtbot.addWidget(w)
    w.show()
    # simulate hotkey activation by calling handler
    w._on_hotkey_open()
    assert w.search_box.hasFocus()
    w.close()
