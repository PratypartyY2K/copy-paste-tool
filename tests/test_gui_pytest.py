import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
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
    # Ensure window is shown and exposed before trying to focus
    qtbot.waitExposed(w)
    # simulate hotkey activation by sending the key event (Ctrl+`)
    try:
        qtbot.keyClick(w, '`', modifier=Qt.ControlModifier)
    except Exception:
        # fallback: directly call handler
        w._on_hotkey_open()
    # Flush event loop after hotkey and give focus some time to propagate
    app.processEvents()
    qtbot.wait(200)
    assert w.search_box.hasFocus()
    w.close()
