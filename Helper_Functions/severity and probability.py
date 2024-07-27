from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QWidget, QScrollArea
)
from PyQt5.QtCore import Qt, QEvent

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Searchable List Example")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.sequence_of_event_edit = QLineEdit()
        self.sequence_of_event_edit.setPlaceholderText("Type to search...")
        self.sequence_of_event_edit.textChanged.connect(self.update_search_results)
        self.sequence_of_event_edit.installEventFilter(self)
        layout.addWidget(self.sequence_of_event_edit)

        self.search_results = QListWidget()
        self.search_results.setHidden(True)
        layout.addWidget(self.search_results)

        # Example data
        self.data = ["Event 1", "Event 2", "Event 3", "Another Event", "More Events"]

        # Add all data to the search results initially
        for item in self.data:
            self.search_results.addItem(QListWidgetItem(item))

    def eventFilter(self, obj, event):
        if obj is self.sequence_of_event_edit and event.type() == QEvent.FocusOut:
            self.search_results.setHidden(True)
        return super().eventFilter(obj, event)

    def update_search_results(self, text):
        self.search_results.clear()

        if text:
            filtered_data = [item for item in self.data if text.lower() in item.lower()]
            if filtered_data:
                self.search_results.setHidden(False)
                for item in filtered_data:
                    self.search_results.addItem(QListWidgetItem(item))
            else:
                self.search_results.setHidden(True)
        else:
            self.search_results.setHidden(True)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
