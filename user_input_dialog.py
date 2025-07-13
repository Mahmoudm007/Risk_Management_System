from PyQt5.QtWidgets import *


class UserInputDialog(QDialog):
    def __init__(self, parent=None, title="User Identification", message="Please enter your name:"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(300, 300, 300, 150)
        self.user_name = ""
        self.message = message
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout(self)

        label = QLabel(self.message)
        layout.addWidget(label)

        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_input)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept_input(self):
        self.user_name = self.name_edit.text().strip()
        if self.user_name:
            self.accept()
        else:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid name.")
