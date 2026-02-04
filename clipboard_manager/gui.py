from PyQt6.QtWidgets import QMainWindow, QListWidget, QVBoxLayout, QWidget, QComboBox, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QSpinBox, QHBoxLayout
from history import History
from watcher import ClipboardWatcher

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("App-Aware Clipboard Manager")
        self.setGeometry(100, 100, 600, 400)

        self.history = History()
        self._pause_ms = 500

        # Dropdown for recent apps
        self.app_dropdown = QComboBox()
        self.app_dropdown.currentIndexChanged.connect(self.update_list)

        # List widget for clipboard items
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)

        # Layout
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
        layout.addWidget(self.app_dropdown)
        layout.addWidget(self.list_widget)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Watcher: signal-based clipboard event emitter
        self.watcher = ClipboardWatcher()
        self.watcher.clipboard_changed.connect(self._on_clipboard_event)

    def _on_clipboard_event(self, content: str, source_app: str, timestamp: float):
        # Delegate to history store and update UI
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

    def update_list(self):
        self.list_widget.clear()
        selected_app = self.app_dropdown.currentText()
        if not selected_app:
            return
        from PyQt6.QtWidgets import QListWidgetItem
        items = self.history.get_items_by_app(selected_app)
        for item in items:
            label = "%s - [%s] %s" % (item.timestamp.strftime('%H:%M:%S'), getattr(item.board, 'value', 'other'), item.content)
            list_item = QListWidgetItem(label)
            list_item.setData(Qt.ItemDataRole.UserRole, item.id)
            self.list_widget.addItem(list_item)

    def show_context_menu(self, position):
        item = self.list_widget.itemAt(position)
        if item:
            self.list_widget.setCurrentItem(item)
        else:
            return

        menu = QMenu()
        copy_action = menu.addAction("Copy to Clipboard")
        action = menu.exec(self.list_widget.viewport().mapToGlobal(position))
        if action == copy_action:
            lw_item = self.list_widget.currentItem()
            if lw_item is None:
                return
            item_id = lw_item.data(Qt.ItemDataRole.UserRole)
            item_obj = self.history.get_item_by_id(item_id)
            if item_obj is None:
                return
            content = item_obj.content
            self.pause_status_label.setText('Paused (%d ms)' % (self._pause_ms,))
            self.pause_status_label.setVisible(True)
            self.watcher.set_text(content, pause_ms=self._pause_ms)
            self.pause_status_label.setVisible(False)
