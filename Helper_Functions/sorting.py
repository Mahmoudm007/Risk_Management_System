import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, \
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog
from PyQt5.QtCore import QDateTime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import Counter

class HazardManager(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setGeometry(100, 100, 700, 500)

    def initUI(self):
        # Layouts
        main_layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        # Name input
        self.name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        form_layout.addWidget(self.name_label)
        form_layout.addWidget(self.name_edit)

        # Hazard input
        self.hazard_label = QLabel("Hazard:")
        self.hazard_edit = QLineEdit()
        form_layout.addWidget(self.hazard_label)
        form_layout.addWidget(self.hazard_edit)

        # Priority selection
        self.priority_label = QLabel("Priority:")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["High", "Medium", "Low"])
        form_layout.addWidget(self.priority_label)
        form_layout.addWidget(self.priority_combo)

        # Add button
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_entry)
        button_layout.addWidget(self.add_button)

        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Hazard", "Priority", "Date"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Add layouts to main layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table_widget)

        # Button to display charts
        self.show_charts_button = QPushButton("Show Charts")
        self.show_charts_button.clicked.connect(self.show_charts)
        main_layout.addWidget(self.show_charts_button)

        self.setLayout(main_layout)
        self.setWindowTitle('Hazard Manager')
        self.show()

    def add_entry(self):
        # Get current date and time
        current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

        # Get inputs
        name = self.name_edit.text()
        hazard = self.hazard_edit.text()
        priority = self.priority_combo.currentText()

        # Add data to the table
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        self.table_widget.setItem(row_position, 0, QTableWidgetItem(name))
        self.table_widget.setItem(row_position, 1, QTableWidgetItem(hazard))
        self.table_widget.setItem(row_position, 2, QTableWidgetItem(priority))
        self.table_widget.setItem(row_position, 3, QTableWidgetItem(current_datetime))

        # Sort the table by priority
        self.sort_table()

    def sort_table(self):
        priorities = {"High": 0, "Medium": 1, "Low": 2}
        row_count = self.table_widget.rowCount()

        data = []
        for row in range(row_count):
            name = self.table_widget.item(row, 0).text()
            hazard = self.table_widget.item(row, 1).text()
            priority = self.table_widget.item(row, 2).text()
            date = self.table_widget.item(row, 3).text()
            data.append((name, hazard, priority, date))

        data.sort(key=lambda x: priorities[x[2]])

        self.table_widget.setRowCount(0)
        for row_data in data:
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            for col, item in enumerate(row_data):
                self.table_widget.setItem(row_position, col, QTableWidgetItem(item))

    def show_charts(self):
        row_count = self.table_widget.rowCount()
        hazards = []
        priorities = []

        for row in range(row_count):
            hazards.append(self.table_widget.item(row, 1).text())
            priorities.append(self.table_widget.item(row, 2).text())

        # Plot most frequent hazards
        hazard_counts = Counter(hazards)
        sorted_hazard_counts = sorted(hazard_counts.items(), key=lambda x: x[1], reverse=True)
        hazard_labels, hazard_values = zip(*sorted_hazard_counts)

        # Create hazard figure
        fig_hazard = Figure()
        canvas_hazard = FigureCanvas(fig_hazard)
        ax_hazard = fig_hazard.add_subplot(111)
        bars = ax_hazard.barh(hazard_labels, hazard_values)
        ax_hazard.set_xlabel('Frequency')
        ax_hazard.set_title('Most Frequent Hazards')
        ax_hazard.invert_yaxis()  # Most frequent on top

        # Annotate bars with counts
        for bar in bars:
            ax_hazard.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2, int(bar.get_width()), va='center')

        # Plot priority counts
        priority_counts = Counter(priorities)
        priority_labels, priority_values = zip(*priority_counts.items())

        # Create priority figure
        fig_priority = Figure()
        canvas_priority = FigureCanvas(fig_priority)
        ax_priority = fig_priority.add_subplot(111)
        bars_priority = ax_priority.bar(priority_labels, priority_values, color=['red', 'orange', 'green'])
        ax_priority.set_xlabel('Priority')
        ax_priority.set_ylabel('Number of Requests')
        ax_priority.set_title('Number of Requests by Priority')

        # Annotate bars with counts
        for bar in bars_priority:
            ax_priority.text(bar.get_x() + bar.get_width() / 2 - 0.1, bar.get_height() + 0.1, int(bar.get_height()), ha='center')

        # Display charts in a new dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Charts")
        layout = QVBoxLayout(dialog)
        layout.addWidget(canvas_hazard)
        layout.addWidget(canvas_priority)
        dialog.setLayout(layout)
        dialog.resize(1300, 1000)
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = HazardManager()
    sys.exit(app.exec_())
