import json
import os
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QDateTime, QPropertyAnimation, QEasingCurve, QUrl, QTimer
from PyQt5.QtWidgets import (QPushButton, QLabel, QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox,
                             QAbstractItemView, QMenu, QDialog, QHBoxLayout, QScrollArea, QTreeWidget, QTreeWidgetItem,
                             QCheckBox, QGroupBox, QMessageBox, QTableWidgetItem, QTableWidget, QLineEdit, QSpinBox, QAction, QFileDialog, QInputDialog)
from PyQt5 import QtCore

class MatrixDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Device-Specific Risk Matrix")
        self.setGeometry(200, 200, 900, 700)
        self.parent_window = parent
        self.current_device = None
        self.matrix_data = {}
        self.matrix_base_path = 'Risk Matrix'
        
        # Ensure directory exists
        if not os.path.exists(self.matrix_base_path):
            os.makedirs(self.matrix_base_path)
            
        self.setupUI()
        self.load_all_matrices()

    def setupUI(self):
        main_layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Device-Specific Risk Matrix Configuration")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 15px; color: #2c3e50;")
        main_layout.addWidget(title_label)

        # Device Selection
        device_group = QGroupBox("")
        device_group.setFixedSize(900, 100)  # Fixed width and height
        device_layout = QHBoxLayout(device_group)

        device_label = QLabel("Device:")
        device_layout.addWidget(device_label)

        self.device_combo = QComboBox()
        self.device_combo.addItems([
            "EzVent 101", "EzVent 201", "EzVent 202", 
            "SleepEZ", "Syringe pump", "Oxygen concentrator"
        ])
        self.device_combo.currentTextChanged.connect(self.on_device_changed)
        device_layout.addWidget(self.device_combo)

        # Add buttons for matrix operations
        copy_button = QPushButton("Copy from Another Device")
        copy_button.clicked.connect(self.copy_matrix_from_device)
        device_layout.addWidget(copy_button)

        reset_button = QPushButton("Reset to Default")
        reset_button.clicked.connect(self.reset_to_default)
        device_layout.addWidget(reset_button)

        main_layout.addWidget(device_group)

        # Matrix Table
        matrix_group = QGroupBox("")
        matrix_layout = QVBoxLayout(matrix_group)

        # Info label
        info_label = QLabel("Right-click on any cell to change its risk level. Changes are automatically saved.")
        info_label.setStyleSheet("font-size: 18px; color: #7f8c8d; margin-bottom: 8px;")
        matrix_layout.addWidget(info_label)

        self.matrix_table = QTableWidget()
        self.matrix_table.setRowCount(5)
        self.matrix_table.setColumnCount(5)
        self.matrix_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.matrix_table.customContextMenuRequested.connect(self.show_matrix_menu)

        # Set headers
        self.matrix_table.setHorizontalHeaderLabels([
            'Improbable (1)', 'Remote (2)', 'Occasional (3)', 'Probable (4)', 'Frequent (5)'
        ])
        self.matrix_table.setVerticalHeaderLabels([
            'Discomfort (1)', 'Minor (2)', 'Serious (3)', 'Critical (4)', 'Catastrophic (5)'
        ])

        # Style the table
        self.matrix_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                text-align: center;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)

        matrix_layout.addWidget(self.matrix_table)
        main_layout.addWidget(matrix_group)

        # Current Selection Info
        info_group = QGroupBox("")
        info_group.setFixedSize(900, 100)  # Fixed width and height
        info_layout = QVBoxLayout(info_group)

        self.selection_info = QLabel("Select a cell to see its current risk level")
        self.selection_info.setStyleSheet("font-size: 17px; color: #2c3e50;")
        info_layout.addWidget(self.selection_info)

        main_layout.addWidget(info_group)

        # Connect selection change
        self.matrix_table.itemSelectionChanged.connect(self.update_selection_info)

        # Buttons
        button_layout = QHBoxLayout()

        test_button = QPushButton("Test RPN Calculation")
        test_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        test_button.clicked.connect(self.test_rpn_calculation)
        button_layout.addWidget(test_button)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)

        main_layout.addLayout(button_layout)

        # Initialize with first device
        self.on_device_changed()

    def get_default_matrix(self):
        """Get the default risk matrix configuration"""
        return {
            "0,0": {"text": "Low", "color": "#2ecc71"},      # Discomfort + Improbable
            "0,1": {"text": "Low", "color": "#2ecc71"},      # Discomfort + Remote
            "0,2": {"text": "Low", "color": "#2ecc71"},      # Discomfort + Occasional
            "0,3": {"text": "Low", "color": "#2ecc71"},      # Discomfort + Probable
            "0,4": {"text": "Medium", "color": "#f1c40f"},   # Discomfort + Frequent
            
            "1,0": {"text": "Low", "color": "#2ecc71"},      # Minor + Improbable
            "1,1": {"text": "Low", "color": "#2ecc71"},      # Minor + Remote
            "1,2": {"text": "Medium", "color": "#f1c40f"},   # Minor + Occasional
            "1,3": {"text": "Medium", "color": "#f1c40f"},   # Minor + Probable
            "1,4": {"text": "Medium", "color": "#f1c40f"},   # Minor + Frequent
            
            "2,0": {"text": "Low", "color": "#2ecc71"},      # Serious + Improbable
            "2,1": {"text": "Medium", "color": "#f1c40f"},   # Serious + Remote
            "2,2": {"text": "Medium", "color": "#f1c40f"},   # Serious + Occasional
            "2,3": {"text": "High", "color": "#e74c3c"},     # Serious + Probable
            "2,4": {"text": "High", "color": "#e74c3c"},     # Serious + Frequent
            
            "3,0": {"text": "Low", "color": "#2ecc71"},      # Critical + Improbable
            "3,1": {"text": "Medium", "color": "#f1c40f"},   # Critical + Remote
            "3,2": {"text": "High", "color": "#e74c3c"},     # Critical + Occasional
            "3,3": {"text": "High", "color": "#e74c3c"},     # Critical + Probable
            "3,4": {"text": "High", "color": "#e74c3c"},     # Critical + Frequent
            
            "4,0": {"text": "Medium", "color": "#f1c40f"},   # Catastrophic + Improbable
            "4,1": {"text": "Medium", "color": "#f1c40f"},   # Catastrophic + Remote
            "4,2": {"text": "High", "color": "#e74c3c"},     # Catastrophic + Occasional
            "4,3": {"text": "High", "color": "#e74c3c"},     # Catastrophic + Probable
            "4,4": {"text": "High", "color": "#e74c3c"},     # Catastrophic + Frequent
        }

    def load_all_matrices(self):
        """Load all device matrices"""
        devices = ["EzVent 101", "EzVent 201", "EzVent 202", "SleepEZ", "Syringe pump", "Oxygen concentrator"]
        
        for device in devices:
            filename = os.path.join(self.matrix_base_path, f"{device.replace(' ', '_')}_matrix.json")
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        self.matrix_data[device] = json.load(f)
                except Exception as e:
                    print(f"Error loading matrix for {device}: {e}")
                    self.matrix_data[device] = self.get_default_matrix()
            else:
                self.matrix_data[device] = self.get_default_matrix()

    def save_matrix_for_device(self, device):
        """Save matrix for specific device"""
        filename = os.path.join(self.matrix_base_path, f"{device.replace(' ', '_')}_matrix.json")
        try:
            with open(filename, 'w') as f:
                json.dump(self.matrix_data[device], f, indent=2)
        except Exception as e:
            print(f"Error saving matrix for {device}: {e}")

    def on_device_changed(self):
        """Handle device selection change"""
        self.current_device = self.device_combo.currentText()
        if self.current_device not in self.matrix_data:
            self.matrix_data[self.current_device] = self.get_default_matrix()
        
        self.load_matrix_to_table()
        self.update_selection_info()

    def load_matrix_to_table(self):
        """Load current device matrix to table"""
        if not self.current_device:
            return
            
        matrix = self.matrix_data[self.current_device]
        
        for row in range(5):
            for col in range(5):
                key = f"{row},{col}"
                if key in matrix:
                    item = QTableWidgetItem(matrix[key]["text"])
                    item.setBackground(QColor(matrix[key]["color"]))
                    
                    # Set text color based on background
                    bg_color = QColor(matrix[key]["color"])
                    if bg_color.lightness() < 128:
                        item.setForeground(QColor("white"))
                    else:
                        item.setForeground(QColor("black"))
                        
                    self.matrix_table.setItem(row, col, item)

    def show_matrix_menu(self, position):
        """Show context menu for matrix cell"""
        menu = QMenu(self)

        high_action = QAction('High', self)
        high_action.triggered.connect(lambda: self.set_cell_value('High', '#e74c3c'))
        menu.addAction(high_action)

        medium_action = QAction('Medium', self)
        medium_action.triggered.connect(lambda: self.set_cell_value('Medium', '#f1c40f'))
        menu.addAction(medium_action)

        low_action = QAction('Low', self)
        low_action.triggered.connect(lambda: self.set_cell_value('Low', '#2ecc71'))
        menu.addAction(low_action)

        menu.exec_(self.matrix_table.viewport().mapToGlobal(position))

    def set_cell_value(self, value, color):
        """Set value and color for selected cells"""
        selected_items = self.matrix_table.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            item.setText(value)
            item.setBackground(QColor(color))
            
            # Set text color based on background
            bg_color = QColor(color)
            if bg_color.lightness() < 128:
                item.setForeground(QColor("white"))
            else:
                item.setForeground(QColor("black"))
            
            # Update matrix data
            row = item.row()
            col = item.column()
            key = f"{row},{col}"
            self.matrix_data[self.current_device][key] = {
                "text": value,
                "color": color
            }
        
        # Save changes
        self.save_matrix_for_device(self.current_device)
        self.update_selection_info()
        
        # Notify parent to update RPN calculations
        if hasattr(self.parent_window, 'on_matrix_updated'):
            self.parent_window.on_matrix_updated(self.current_device)

    def update_selection_info(self):
        """Update selection information"""
        selected_items = self.matrix_table.selectedItems()
        if selected_items:
            item = selected_items[0]
            row = item.row()
            col = item.column()
            
            severity_names = ['Discomfort (1)', 'Minor (2)', 'Serious (3)', 'Critical (4)', 'Catastrophic (5)']
            probability_names = ['Improbable (1)', 'Remote (2)', 'Occasional (3)', 'Probable (4)', 'Frequent (5)']
            
            info_text = f"Selected: {severity_names[row]} × {probability_names[col]} = {item.text()}"
            self.selection_info.setText(info_text)
        else:
            self.selection_info.setText("Select a cell to see its current risk level")

    def copy_matrix_from_device(self):
        """Copy matrix from another device"""
        devices = [d for d in self.matrix_data.keys() if d != self.current_device]
        if not devices:
            QMessageBox.information(self, "No Other Devices", "No other device matrices available to copy from.")
            return
            
        source_device, ok = QInputDialog.getItem(
            self, "Copy Matrix", "Select device to copy matrix from:", devices, 0, False
        )
        
        if ok and source_device:
            reply = QMessageBox.question(
                self, "Confirm Copy", 
                f"This will replace the current matrix for {self.current_device} with the matrix from {source_device}. Continue?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.matrix_data[self.current_device] = self.matrix_data[source_device].copy()
                self.save_matrix_for_device(self.current_device)
                self.load_matrix_to_table()
                QMessageBox.information(self, "Success", f"Matrix copied from {source_device}")

    def reset_to_default(self):
        """Reset current device matrix to default"""
        reply = QMessageBox.question(
            self, "Confirm Reset", 
            f"This will reset the matrix for {self.current_device} to default values. Continue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.matrix_data[self.current_device] = self.get_default_matrix()
            self.save_matrix_for_device(self.current_device)
            self.load_matrix_to_table()
            QMessageBox.information(self, "Success", "Matrix reset to default values")

    def test_rpn_calculation(self):
        """Test RPN calculation with current matrix"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Test RPN Calculation")
        dialog.setGeometry(300, 300, 400, 200)
        
        layout = QVBoxLayout(dialog)
        
        # Severity selection
        sev_layout = QHBoxLayout()
        sev_layout.addWidget(QLabel("Severity:"))
        sev_combo = QComboBox()
        sev_combo.addItems(["1 (Discomfort)", "2 (Minor)", "3 (Serious)", "4 (Critical)", "5 (Catastrophic)"])
        sev_layout.addWidget(sev_combo)
        layout.addLayout(sev_layout)
        
        # Probability selection
        prob_layout = QHBoxLayout()
        prob_layout.addWidget(QLabel("Probability:"))
        prob_combo = QComboBox()
        prob_combo.addItems(["1 (Improbable)", "2 (Remote)", "3 (Occasional)", "4 (Probable)", "5 (Frequent)"])
        prob_layout.addWidget(prob_combo)
        layout.addLayout(prob_layout)
        
        # Result display
        result_label = QLabel("RPN: Not calculated")
        result_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px; border: 1px solid #bdc3c7;")
        layout.addWidget(result_label)
        
        def calculate_test_rpn():
            severity = sev_combo.currentIndex() + 1
            probability = prob_combo.currentIndex() + 1
            rpn = self.get_rpn_for_device(self.current_device, severity, probability)
            result_label.setText(f"RPN: {rpn}")
            
            # Color the result
            colors = {"High": "#e74c3c", "Medium": "#f1c40f", "Low": "#2ecc71"}
            result_label.setStyleSheet(f"""
                font-size: 14px; font-weight: bold; padding: 10px; 
                border: 1px solid #bdc3c7; background-color: {colors.get(rpn, '#ecf0f1')};
                color: {'white' if rpn == 'High' else 'black'};
            """)
        
        sev_combo.currentIndexChanged.connect(calculate_test_rpn)
        prob_combo.currentIndexChanged.connect(calculate_test_rpn)
        
        # Initial calculation
        calculate_test_rpn()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()

    def get_rpn_for_device(self, device, severity, probability):
        """Get RPN value for specific device, severity, and probability"""
        if device not in self.matrix_data:
            return "Unknown"
            
        # Convert to 0-based indices
        row = severity - 1
        col = probability - 1
        
        if row < 0 or row > 4 or col < 0 or col > 4:
            return "Unknown"
            
        key = f"{row},{col}"
        matrix = self.matrix_data[device]
        
        if key in matrix:
            return matrix[key]["text"]
        else:
            return "Unknown"

    def get_all_device_matrices(self):
        """Return all device matrices for external use"""
        return self.matrix_data.copy()
