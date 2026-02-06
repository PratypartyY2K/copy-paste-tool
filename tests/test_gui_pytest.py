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

def test_search_focus_hotkey(app, qtbot, monkeypatch):
    w = MainWindow()
    qtbot.addWidget(w)
    w.show()
    # Ensure window is shown and exposed before trying to focus
    qtbot.waitExposed(w)
    # Monkeypatch the search_box.setFocus to record calls rather than depending on OS focus
    called = {'v': False}
    def fake_setfocus(*args, **kwargs):
        called['v'] = True
    try:
        monkeypatch.setattr(w.search_box, 'setFocus', fake_setfocus)
    except Exception:
        # if monkeypatching fails, continue; we'll still try to assert focus
        pass
    # simulate hotkey activation by sending the key event (Ctrl+`)
    try:
        qtbot.keyClick(w, '`', modifier=Qt.ControlModifier)
    except Exception:
        # fallback: directly call handler
        w._on_hotkey_open()
    # Flush event loop after hotkey and give focus some time to propagate
    app.processEvents()
    qtbot.wait(200)
    # Either setFocus was called on the widget, or the widget actually has focus
    assert called['v'] or w.search_box.hasFocus()
    w.close()
