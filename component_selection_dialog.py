from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QPushButton, QLabel, QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox,
                             QAbstractItemView, QMenu, QDialog, QHBoxLayout, QScrollArea, QTreeWidget, QTreeWidgetItem,
                             QCheckBox, QGroupBox, QMessageBox, QFileDialog, QLineEdit, QDialogButtonBox)

# Enhanced device components with categories
DEVICE_COMPONENTS = {
    "EzVent 101": {
        "Mechanical": ["Screws", "Stands", "Casing", "Valves", "Tubing", "Pressure Relief Valve"],
        "Electrical": ["Batteries", "Circuit Boards", "Sensors", "Wires", "Display Unit", "Power Supply"],
        "Software": ["Firmware", "User Interface Software", "Control Algorithms", "Safety Monitoring"],
        "Consumables": ["Filters", "Masks", "Hoses", "Breathing Circuits"],
        "Others": ["Labels", "Documentation", "Packaging", "Accessories"]
    },
    "EzVent 201": {
        "Mechanical": ["Screws", "Stands", "Casing", "Valves", "Tubing", "Flow Sensors"],
        "Electrical": ["Batteries", "Circuit Boards", "Sensors", "Wires", "Display Unit", "AC Power Cord"],
        "Software": ["Firmware", "User Interface Software", "Control Algorithms", "Data Logging"],
        "Consumables": ["Filters", "Masks", "Hoses", "Breathing Circuits"],
        "Others": ["Labels", "Documentation", "Packaging", "Calibration Tools"]
    },
    "EzVent 202": {
        "Mechanical": ["AC Power Inlet", "Check Valve", "Fittings", "Gas Manifold", "Pressure Regulators"],
        "Electrical": ["AC-DC Power Supply", "Charging controller IC", "Control Boards", "Sensors"],
        "Software": ["Advanced Control Software", "Network Interface", "Remote Monitoring"],
        "Consumables": ["Filters", "Tubing", "Connectors"],
        "Others": ["Mounting Hardware", "Service Tools", "User Manuals"]
    },
    "SleepEZ": {
        "Mechanical": ["Housing", "Motor Assembly", "Pressure Sensors", "Valves"],
        "Electrical": ["Power Supply", "Control Electronics", "Display", "Connectivity Module"],
        "Software": ["Sleep Monitoring Software", "Data Analysis", "Mobile App Interface"],
        "Consumables": ["Masks", "Tubing", "Filters", "Headgear"],
        "Others": ["Carrying Case", "SD Card", "User Guide"]
    },
    "Syringe pump": {
        "Mechanical": ["Syringe Holder", "Plunger Drive", "Motor Assembly", "Chassis"],
        "Electrical": ["Control Board", "Display", "Alarm System", "Power Supply"],
        "Software": ["Infusion Control Software", "Safety Algorithms", "User Interface"],
        "Consumables": ["Syringes", "IV Tubing", "Connectors"],
        "Others": ["Mounting Bracket", "Battery Pack", "Service Kit"]
    },
    "Oxygen concentrator": {
        "Mechanical": ["Compressor", "Molecular Sieve", "Cooling Fan", "Pressure Vessels"],
        "Electrical": ["Control Electronics", "Oxygen Sensor", "Flow Meter", "Power Supply"],
        "Software": ["Concentration Control", "Flow Management", "Alarm System"],
        "Consumables": ["Filters", "Tubing", "Cannulas"],
        "Others": ["Wheels", "Handle", "Maintenance Kit", "User Manual"]
    }
}


class ComponentSelectionDialog(QDialog):
    def __init__(self, selected_device, parent=None):
        super().__init__(parent)
        self.selected_device = selected_device
        self.setWindowTitle(f'Select Components for {self.selected_device}')
        self.setGeometry(100, 100, 600, 500)

        self.layout = QVBoxLayout(self)

        info_label = QLabel(f"Please select components for the device: <b>{self.selected_device}</b>")
        info_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.layout.addWidget(info_label)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(['Components'])
        self.populate_tree()
        self.tree.itemChanged.connect(self.update_save_button_state)

        self.layout.addWidget(self.tree)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.save_button = self.button_box.button(QDialogButtonBox.Save)
        self.save_button.setEnabled(False)
        self.button_box.accepted.connect(self.add_checked_items)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.checked_items = []

    def populate_tree(self):
        components_data = DEVICE_COMPONENTS.get(self.selected_device, {
            'General Components': ['Power Supply', 'Main Board', 'User Interface', 'Enclosure'],
            'Specific Components': [f'Component A for {self.selected_device}', f'Component B for {self.selected_device}']
        })

        for category, items in components_data.items():
            category_item = QTreeWidgetItem(self.tree, [category])
            category_item.setCheckState(0, 0)
            for item_name in items:
                component_item = QTreeWidgetItem(category_item, [item_name])
                component_item.setCheckState(0, 0)

    def update_save_button_state(self, item):
        has_checked_items = False
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            if self._check_any_child_checked(root.child(i)):
                has_checked_items = True
                break
        self.save_button.setEnabled(has_checked_items)

    def _check_any_child_checked(self, item):
        if item.checkState(0) == 2:
            return True
        for i in range(item.childCount()):
            if self._check_any_child_checked(item.child(i)):
                return True
        return False

    def add_checked_items(self):
        self.checked_items = self.get_checked_items(self.tree.invisibleRootItem())
        self.accept()

    def get_checked_items(self, item):
        checked_items = []
        if item.checkState(0) == 2:
            if item.childCount() == 0 or item.parent() is None:
                checked_items.append(item.text(0))

        for i in range(item.childCount()):
            checked_items.extend(self.get_checked_items(item.child(i)))

        return checked_items
