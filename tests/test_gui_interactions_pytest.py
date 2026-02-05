from PyQt6.QtWidgets import QApplication, QMenu
from PyQt6.QtCore import QPoint
from clipboard_manager.gui import MainWindow


def test_update_list_and_actions(monkeypatch, qtbot):
    app = QApplication.instance() or QApplication([])
    w = MainWindow()
    qtbot.addWidget(w)

    # add an item to history
    it = w.history.add_item('example content http://example.com', source_app='Google Chrome')
    w.update_apps_dropdown()
    w.update_list()
    assert w.list_widget.count() >= 1

    item = w.list_widget.item(0)
    rect = w.list_widget.visualItemRect(item)
    pos = rect.center()

    called = {'set_text': False}
    def fake_set_text(text, pause_ms=None):
        called['set_text'] = True
    monkeypatch.setattr(w.watcher, 'set_text', fake_set_text)

    # monkeypatch QMenu.exec to return copy_action (first action)
    def fake_exec(self, pt):
        return self.actions()[0]
    monkeypatch.setattr(QMenu, 'exec', fake_exec)

    w.show_context_menu(pos)
    assert called['set_text'] is True

    # Now test pin action: return actions()[7] (pin)
    def fake_exec_pin(self, pt):
        return self.actions()[7]
    monkeypatch.setattr(QMenu, 'exec', fake_exec_pin)

    w.show_context_menu(pos)
    # pinned prefix should be present on update
    w.update_list()
    item_widget = w.list_widget.itemWidget(w.list_widget.item(0))
    assert item_widget is not None and '[PIN]' in item_widget.text()

    w.close()
