from PyQt5.QtWidgets import *


class RiskHistoryDialog(QDialog):
    def __init__(self, risk_id, history_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Risk History - {risk_id}")
        self.setGeometry(200, 200, 800, 600)
        self.setupUI(history_data)

    def setupUI(self, history_data):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Risk Edit History")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #2c3e50;")
        layout.addWidget(title_label)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "Timestamp", "User", "Field", "Previous Value", "New Value"
        ])
        
        # Populate history
        if history_data:
            self.history_table.setRowCount(len(history_data))
            for row, entry in enumerate(history_data):
                self.history_table.setItem(row, 0, QTableWidgetItem(entry.get('timestamp', '')))
                self.history_table.setItem(row, 1, QTableWidgetItem(entry.get('user', '')))
                self.history_table.setItem(row, 2, QTableWidgetItem(entry.get('field', '')))
                self.history_table.setItem(row, 3, QTableWidgetItem(entry.get('previous_value', '')))
                self.history_table.setItem(row, 4, QTableWidgetItem(entry.get('new_value', '')))
        else:
            self.history_table.setRowCount(1)
            self.history_table.setItem(0, 0, QTableWidgetItem("No history available"))
            self.history_table.setSpan(0, 0, 1, 5)

        # Adjust column widths
        self.history_table.resizeColumnsToContents()
        layout.addWidget(self.history_table)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
