from clipboard_manager.history import HistoryStore


def test_normalize_python_app():
    h = HistoryStore()
    item = h.add_item('sample', source_app='Python 3.11')
    assert item is not None
    assert item.source_app == 'Python 3.11'


def test_add_and_get_item_by_app():
    h = HistoryStore()
    h.add_item('a', source_app='Terminal')
    h.add_item('b', source_app='Terminal')
    items = h.get_items_by_app('Terminal')
    assert len(items) >= 2
