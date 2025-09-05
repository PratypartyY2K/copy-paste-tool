from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QVBoxLayout, QWidget, QComboBox, QMenu
from PyQt6.QtCore import QTimer, Qt
from history import History
from utils import get_frontmost_app

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App-Aware Clipboard Manager")
        self.setGeometry(100, 100, 600, 400)

        self.history = History()
        self.last_text = ""

        # Dropdown for recent apps
        self.app_dropdown = QComboBox()
        self.app_dropdown.currentIndexChanged.connect(self.update_list)

        # List widget for clipboard items
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.app_dropdown)
        layout.addWidget(self.list_widget)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Clipboard
        self.clipboard = QApplication.clipboard()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(500)

    def check_clipboard(self):
        text = self.clipboard.text()
        if text and text != self.last_text:
            self.last_text = text
            source_app = get_frontmost_app()
            self.history.add_item(text, source_app=source_app)
            self.update_apps_dropdown()
            self.update_list()

    def update_apps_dropdown(self):
        apps = self.history.get_apps()
        current_app = self.app_dropdown.currentText()
        self.app_dropdown.blockSignals(True)  # prevent signal triggering while updating
        self.app_dropdown.clear()
        self.app_dropdown.addItems(apps)
        # Restore previous selection if still exists
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
        menu = QMenu()
        copy_action = menu.addAction("Copy to Clipboard")
        action = menu.exec(self.list_widget.viewport().mapToGlobal(position))
        if action == copy_action:
            selected_row = self.list_widget.currentRow()
            selected_app = self.app_dropdown.currentText()
            items = self.history.get_items_by_app(selected_app)
            if selected_row != -1:
                content = items[selected_row].content
                self.clipboard.setText(content)