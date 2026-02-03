from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QVBoxLayout, QWidget, QComboBox, QMenu
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QLabel, QSpinBox, QHBoxLayout
from history import History
from utils import get_frontmost_app

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App-Aware Clipboard Manager")
        self.setGeometry(100, 100, 600, 400)

        self.history = History()
        self.last_text = ""
        self._ignore_clipboard = False
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

        # Clipboard
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.check_clipboard)

    def check_clipboard(self):
        if self._ignore_clipboard:
            return

        text = self.clipboard.text()
        if text and text != self.last_text:
            self.last_text = text
            source_app = get_frontmost_app()
            self.history.add_item(text, source_app=source_app)
            self.update_apps_dropdown()
            self.update_list()

    def _pause_clipboard_capture(self, ms=None):
        if ms is None:
            ms = self._pause_ms
        self._ignore_clipboard = True
        try:
            self.pause_status_label.setText(f'Paused ({ms} ms)')
            self.pause_status_label.setVisible(True)
        except Exception:
            pass
        QTimer.singleShot(ms, self._resume_clipboard_capture)

    def _resume_clipboard_capture(self):
        self._ignore_clipboard = False
        try:
            self.pause_status_label.setVisible(False)
            self.pause_status_label.setText('')
        except Exception:
            pass

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
        items = self.history.get_items_by_app(selected_app)
        for item in items:
            self.list_widget.addItem(f"{item.timestamp.strftime('%H:%M:%S')} - {item.content}") # item.content[:50] for putting a limit of 50 characters

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
            selected_row = self.list_widget.currentRow()
            selected_app = self.app_dropdown.currentText()
            items = self.history.get_items_by_app(selected_app)
            if selected_row != -1:
                content = items[selected_row].content
                self._pause_clipboard_capture()
                self.last_text = content
                self.clipboard.setText(content)
