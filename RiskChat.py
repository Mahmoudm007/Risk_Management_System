from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QLineEdit, QPushButton


class ChatDialog(QDialog):
    def __init__(self, row_id, chat_data, parent=None):
        super(ChatDialog, self).__init__(parent)
        self.setWindowTitle(f"Chat for Row {row_id}")
        self.row_id = row_id
        self.chat_data = chat_data

        # Initialize layout and widgets
        self.layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Name")
        self.layout.addWidget(self.name_edit)

        self.message_edit = QLineEdit()
        self.message_edit.setPlaceholderText("Message")
        self.layout.addWidget(self.message_edit)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button)

        # Load existing chat messages
        self.load_chat()

    def load_chat(self):
        self.list_widget.clear()
        if self.row_id in self.chat_data:
            for name, message in self.chat_data[self.row_id]:
                self.list_widget.addItem(f"{name}: {message}")

    def send_message(self):
        name = self.name_edit.text()
        message = self.message_edit.text()
        if name and message:
            if self.row_id not in self.chat_data:
                self.chat_data[self.row_id] = []
            self.chat_data[self.row_id].append((name, message))
            self.list_widget.addItem(f"{name}: {message}")
            self.message_edit.clear()
