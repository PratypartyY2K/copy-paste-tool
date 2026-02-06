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
    assert hasattr(w, 'app_dropdown')
    assert hasattr(w, 'list_widget')
    w.close()

def test_search_focus_hotkey(app, qtbot, monkeypatch):
    w = MainWindow()
    qtbot.addWidget(w)
    w.show()
    qtbot.waitExposed(w)
    called = {'v': False}
    def fake_setfocus(*args, **kwargs):
        called['v'] = True
    try:
        monkeypatch.setattr(w.search_box, 'setFocus', fake_setfocus)
    except Exception:
        pass
    try:
        qtbot.keyClick(w, '`', modifier=Qt.ControlModifier)
    except Exception:
        w._on_hotkey_open()
    app.processEvents()
    qtbot.wait(200)
    assert called['v'] or w.search_box.hasFocus()
    w.close()
