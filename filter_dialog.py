from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Risks")
        self.setGeometry(200, 200, 400, 300)
        self.parent_window = parent
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Filter Options")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Filter Type Selection
        filter_group = QGroupBox("Select Filter Type")
        filter_layout = QVBoxLayout(filter_group)

        self.filter_type = QComboBox()
        self.filter_type.addItems(["All Risks", "Device", "Risk Level", "Approval Status", "Department"])
        self.filter_type.currentTextChanged.connect(self.update_filter_options)
        filter_layout.addWidget(self.filter_type)

        layout.addWidget(filter_group)

        # Filter Options
        options_group = QGroupBox("Select Specific Option")
        options_layout = QVBoxLayout(options_group)

        self.filter_options = QComboBox()
        options_layout.addWidget(self.filter_options)

        layout.addWidget(options_group)

        # Update initial options
        self.update_filter_options()

        # Buttons
        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply Filter")
        apply_button.clicked.connect(self.apply_filter)
        button_layout.addWidget(apply_button)

        clear_button = QPushButton("Clear Filter")
        clear_button.clicked.connect(self.clear_filter)
        button_layout.addWidget(clear_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def update_filter_options(self):
        self.filter_options.clear()
        filter_type = self.filter_type.currentText()

        if filter_type == "All Risks":
            self.filter_options.addItems(["Show All"])
        elif filter_type == "Device":
            devices = self.get_unique_devices()
            self.filter_options.addItems(devices)
        elif filter_type == "Risk Level":
            risk_levels = ["HIGH", "MEDIUM", "LOW"]
            self.filter_options.addItems(risk_levels)
        elif filter_type == "Approval Status":
            approval_statuses = ["Approved", "Rejected", "Pending"]
            self.filter_options.addItems(approval_statuses)
        elif filter_type == "Department":
            departments = ["Software Department", "Electrical Department", "Mechanical Department", 
                          "Usability Team", "Testing Team"]
            self.filter_options.addItems(departments)

    def get_unique_devices(self):
        devices = set()
        table = self.parent_window.table_widget
        for row in range(table.rowCount()):
            device_item = table.item(row, 3)  # Device Affected column
            if device_item and device_item.text().strip():
                device_list = [d.strip() for d in device_item.text().split(',')]
                devices.update(device_list)
        return sorted(list(devices))

    def apply_filter(self):
        filter_type = self.filter_type.currentText()
        filter_value = self.filter_options.currentText()
        
        if filter_type == "All Risks":
            self.parent_window.clear_table_filters()
        else:
            self.parent_window.apply_single_filter(filter_type, filter_value)
        
        self.close()

    def clear_filter(self):
        self.parent_window.clear_table_filters()
        self.close()
