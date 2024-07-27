import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QDialog, QCalendarWidget, QTimeEdit, QWidget, QHBoxLayout


class CalendarDialog(QDialog):
    def __init__(self, parent=None):
        super(CalendarDialog, self).__init__(parent)
        self.setWindowTitle("Select Date and Time")

        # Create a calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.date_selected)

        # Create a time edit widget
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addWidget(self.time_edit)
        self.setLayout(layout)

    def date_selected(self, date):
        # Get the selected time
        time = self.time_edit.time().toString("HH:mm")
        # Emit signal with the selected date and time
        self.parent().set_date_time_label(date.toString('yyyy-MM-dd'), time)
        self.accept()

