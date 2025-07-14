from PyQt5.QtWidgets import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from PyQt5.QtWidgets import (QPushButton, QLabel, QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox,
                             QAbstractItemView, QMenu, QDialog, QHBoxLayout, QScrollArea, QTreeWidget, QTreeWidgetItem,
                             QCheckBox, QGroupBox, QMessageBox, QFileDialog)

class EnhancedPDFDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate PDF Report")
        self.setGeometry(200, 200, 400, 300)
        self.parent_window = parent
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("PDF Generation Options")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Filter Type Selection
        filter_group = QGroupBox("Select Filter Type")
        filter_layout = QVBoxLayout(filter_group)

        self.filter_type = QComboBox()
        self.filter_type.addItems(["Department", "Device", "Risk Level", "Approval Status"])
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

        generate_button = QPushButton("Generate PDF")
        generate_button.clicked.connect(self.generate_pdf)
        button_layout.addWidget(generate_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def update_filter_options(self):
        self.filter_options.clear()
        filter_type = self.filter_type.currentText()

        if filter_type == "Department":
            departments = ["Software Department", "Electrical Department", "Mechanical Department", 
                          "Usability Team", "Testing Team"]
            self.filter_options.addItems(departments)
        
        elif filter_type == "Device":
            devices = self.get_unique_devices()
            self.filter_options.addItems(devices)
        
        elif filter_type == "Risk Level":
            risk_levels = ["HIGH", "MEDIUM", "LOW"]
            self.filter_options.addItems(risk_levels)
        
        elif filter_type == "Approval Status":
            approval_statuses = ["Approved", "Rejected", "Pending"]
            self.filter_options.addItems(approval_statuses)

    def get_unique_devices(self):
        devices = set()
        table = self.parent_window.table_widget
        for row in range(table.rowCount()):
            device_item = table.item(row, 3)  # Device Affected column
            if device_item and device_item.text().strip():
                device_list = [d.strip() for d in device_item.text().split(',')]
                devices.update(device_list)
        return sorted(list(devices))

    def generate_pdf(self):
        filter_type = self.filter_type.currentText()
        filter_value = self.filter_options.currentText()
        
        if not filter_value:
            QMessageBox.warning(self, "No Selection", "Please select a filter option.")
            return

        self.parent_window.generate_filtered_pdf(filter_type, filter_value)
        self.close()
