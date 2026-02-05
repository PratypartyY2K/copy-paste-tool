from PyQt6.QtWidgets import QMainWindow, QListWidget, QVBoxLayout, QWidget, QComboBox, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QSpinBox, QHBoxLayout, QCheckBox, QPushButton, QDialog, QTextEdit, QDialogButtonBox, QFormLayout, QLineEdit
from PyQt6.QtGui import QShortcut, QKeySequence
from clipboard_manager.history import History
from clipboard_manager.watcher import ClipboardWatcher
from clipboard_manager.utils import trim_whitespace, copy_one_line, extract_urls_text, json_escape, to_camel_case, to_snake_case
from PyQt6.QtCore import QTimer


class BlocklistEditor(QDialog):
    def __init__(self, parent=None, initial_blocklist=None):
        super(BlocklistEditor, self).__init__(parent)
        self.setWindowTitle('Edit Secret-safe Blocklist')
        self.setModal(True)
        layout = QVBoxLayout()
        form = QFormLayout()
        self.text = QTextEdit()
        if initial_blocklist:
            self.text.setPlainText('\n'.join(initial_blocklist))
        form.addRow('Blocklist entries (one per line):', self.text)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_entries(self):
        txt = self.text.toPlainText()
        return [line.strip() for line in txt.splitlines() if line.strip()]


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("App-Aware Clipboard Manager")
        self.setGeometry(100, 100, 600, 400)

        self.history = History()
        self._pause_ms = 500

        self._history_listener = lambda: QTimer.singleShot(0, self._on_history_changed)
        self.history.add_change_listener(self._history_listener)

        ss_layout = QHBoxLayout()
        self.secret_safe_checkbox = QCheckBox('Secret-safe mode')
        self.secret_safe_checkbox.setChecked(self.history.get_secret_safe_enabled())
        self.secret_safe_checkbox.stateChanged.connect(self._on_secret_safe_toggled)
        ss_layout.addWidget(self.secret_safe_checkbox)
        self.edit_blocklist_btn = QPushButton('Edit Blocklist')
        self.edit_blocklist_btn.clicked.connect(self._on_edit_blocklist)
        ss_layout.addWidget(self.edit_blocklist_btn)

        self.app_dropdown = QComboBox()
        self.app_dropdown.currentIndexChanged.connect(self.update_list)

        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('Search current app/board...')
        self.search_box.textChanged.connect(self.update_list)

        layout = QVBoxLayout()
        pause_layout = QHBoxLayout()
        pause_label = QLabel('Pause (ms):')
        self.pause_spin = QSpinBox()
        self.pause_spin.setRange(0, 5000)
        self.pause_spin.setSingleStep(50)
        self.pause_spin.setValue(self._pause_ms)
        self.pause_spin.valueChanged.connect(self._on_pause_spin_changed)
        pause_layout.addWidget(pause_label)
        pause_layout.addWidget(self.pause_spin)
        self.pause_status_label = QLabel('')
        self.pause_status_label.setStyleSheet('color: red; font-weight: bold;')
        self.pause_status_label.setVisible(False)
        pause_layout.addWidget(self.pause_status_label)
        layout.addLayout(pause_layout)
        layout.addLayout(ss_layout)
        layout.addWidget(self.app_dropdown)
        layout.addWidget(self.search_box)
        layout.addWidget(self.list_widget)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        shortcut = QShortcut(QKeySequence('Ctrl+`'), self)
        shortcut.activated.connect(self._on_hotkey_open)

        self.watcher = ClipboardWatcher()
        self.watcher.clipboard_changed.connect(self._on_clipboard_event)

    def _on_clipboard_event(self, content: str, source_app: str, timestamp: float):
        item = self.history.add_item(content, source_app=source_app, timestamp=timestamp)
        if item is not None:
            self.update_apps_dropdown()
            self.update_list()

    def _on_pause_spin_changed(self, value: int):
        self._pause_ms = int(value)

    def update_apps_dropdown(self):
        apps = self.history.get_apps()
        current_app = self.app_dropdown.currentText()
        self.app_dropdown.blockSignals(True)
        self.app_dropdown.clear()
        self.app_dropdown.addItems(apps)
        if current_app in apps:
            self.app_dropdown.setCurrentText(current_app)
        self.app_dropdown.blockSignals(False)

    def _on_history_changed(self):
        self.update_apps_dropdown()
        self.update_list()

    def closeEvent(self, event):
        try:
            self.history.remove_change_listener(self._history_listener)
        except Exception:
            pass
        return super(MainWindow, self).closeEvent(event)

    def update_list(self):
        self.list_widget.clear()
        selected_app = self.app_dropdown.currentText()
        if not selected_app:
            return
        filter_text = self.search_box.text().lower().strip()
        from PyQt6.QtWidgets import QListWidgetItem
        items = self.history.get_items_by_app(selected_app)
        for item in items:
            if filter_text:
                if filter_text not in item.content.lower() and filter_text not in getattr(item.board, 'value', '').lower():
                    continue
            label = "%s - [%s] %s" % (item.timestamp.strftime('%H:%M:%S'), getattr(item.board, 'value', 'other'), item.content)
            list_item = QListWidgetItem(label)
            list_item.setData(Qt.ItemDataRole.UserRole, item.id)
            if getattr(item, 'pinned', False):
                list_item.setText('[PIN] ' + list_item.text())
            self.list_widget.addItem(list_item)

    def show_context_menu(self, position):
        item = self.list_widget.itemAt(position)
        if item:
            self.list_widget.setCurrentItem(item)
        else:
            return

        menu = QMenu()
        copy_action = menu.addAction("Copy to Clipboard")
        trim_action = menu.addAction("Trim whitespace")
        oneline_action = menu.addAction("Copy as one-line")
        extract_urls_action = menu.addAction("Extract URLs")
        json_action = menu.addAction("JSON-escape")
        camel_action = menu.addAction("Convert to camelCase")
        snake_action = menu.addAction("Convert to snake_case")
        pin_action = menu.addAction("Pin item")
        unpin_action = menu.addAction("Unpin item")

        action = menu.exec(self.list_widget.viewport().mapToGlobal(position))
        if action in (copy_action, trim_action, oneline_action, extract_urls_action, json_action, camel_action, snake_action, pin_action, unpin_action):
            lw_item = self.list_widget.currentItem()
            if lw_item is None:
                return
            item_id = lw_item.data(Qt.ItemDataRole.UserRole)
            item_obj = self.history.get_item_by_id(item_id)
            if item_obj is None:
                return
            original = item_obj.content

            if action == copy_action:
                out = original
            elif action == trim_action:
                out = trim_whitespace(original)
            elif action == oneline_action:
                out = copy_one_line(original)
            elif action == extract_urls_action:
                out = extract_urls_text(original)
            elif action == json_action:
                out = json_escape(original)
            elif action == camel_action:
                out = to_camel_case(original)
            elif action == snake_action:
                out = to_snake_case(original)
            else:
                out = original

            if action == pin_action:
                self.history.pin_item(item_id)
                self.update_list()
                return
            if action == unpin_action:
                self.history.unpin_item(item_id)
                self.update_list()
                return

            self.pause_status_label.setText('Paused (%d ms)' % (self._pause_ms,))
            self.pause_status_label.setVisible(True)
            self.watcher.set_text(out, pause_ms=self._pause_ms)
            self.pause_status_label.setVisible(False)

    def _on_secret_safe_toggled(self, state: int):
        enabled = (state == Qt.CheckState.Checked)
        self.history.set_secret_safe_enabled(enabled)

    def _on_edit_blocklist(self):
        initial_blocklist = self.history.get_blocklist()
        editor = BlocklistEditor(self, initial_blocklist=initial_blocklist)
        if editor.exec() == QDialog.DialogCode.Accepted:
            entries = editor.get_entries()
            self.history.set_blocklist(entries)

    def _on_hotkey_open(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_box.setFocus()
