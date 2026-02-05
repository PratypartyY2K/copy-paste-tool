import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PyQt6.QtWidgets import QApplication
from clipboard_manager.watcher import ClipboardWatcher
from clipboard_manager.history import History
import time


def main():
    app = QApplication([])

    # Create watcher and history directly
    watcher = ClipboardWatcher()
    history = History()

    # connect watcher to history as the app would
    watcher.clipboard_changed.connect(lambda content, source_app, ts: history.add_item(content, source_app=source_app, timestamp=ts))

    # Default pause value (we'll just test pause behavior via watcher.pause)
    # Simulate external clipboard change
    watcher.clipboard.setText('external1')
    # Manually trigger handler since in test environment dataChanged may not fire
    watcher._on_clipboard_change()
    assert len(history.items) == 1 and history.items[0].content == 'external1', 'external change not captured'

    # Programmatic copy during pause should be ignored
    watcher.pause(200)
    watcher.clipboard.setText('external1')
    watcher._on_clipboard_change()
    assert len(history.items) == 1, 'programmatic copy was re-captured; expected ignored'

    # After resume, external change captured
    watcher.resume()
    watcher.clipboard.setText('external2')
    watcher._on_clipboard_change()
    assert len(history.items) == 2 and history.items[0].content == 'external2', 'external2 not captured'

    print('SMOKE_TEST_OK')


if __name__ == '__main__':
    main()
