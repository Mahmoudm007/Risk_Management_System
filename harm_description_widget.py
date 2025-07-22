from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import json
import os
from search import *
from harm_description_dialog import HarmDescriptionDialog
from PyQt5.QtWidgets import (QPushButton, QLabel, QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QListWidget,
                             QAbstractItemView, QMenu, QDialog, QHBoxLayout, QScrollArea, QTreeWidget, QTreeWidgetItem,
                             QCheckBox, QGroupBox, QMessageBox, QTableWidgetItem, QTableWidget, QLineEdit, QSpinBox, QAction, QFileDialog)

class HarmDescriptionCardWidget(QWidget):
    """Enhanced widget to display harm descriptions with RPN data and numbering support"""
    harms_updated = pyqtSignal(list, dict, int)  # harms list, rpn_data dict, count
    rpn_data_changed = pyqtSignal(dict)  # Signal for RPN data changes

    def __init__(self, initial_harms=None, initial_rpn_data=None, selected_device=None, 
                 parent=None, numbering_manager=None, component_name=""):
        super().__init__(parent)
        self.harms = initial_harms or []
        self.rpn_data = initial_rpn_data or {}
        self.selected_device = selected_device
        self.parent_window = parent
        self.numbering_manager = numbering_manager
        self.component_name = component_name
        self.setupUI()
        self.update_display()

    def setupUI(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(3, 3, 3, 3)
        self.main_layout.setSpacing(2)

        # Scroll area for harms
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(150)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.harms_container = QWidget()
        self.harms_layout = QVBoxLayout(self.harms_container)
        self.harms_layout.setContentsMargins(2, 2, 2, 2)
        self.harms_layout.setSpacing(2)

        self.scroll_area.setWidget(self.harms_container)
        self.main_layout.addWidget(self.scroll_area)

        # Summary bar
        self.summary_label = QLabel("No harms")
        self.summary_label.setStyleSheet("""
            background-color: #ecf0f1;
            color: #2c3e50;
            padding: 2px 4px;
            border-radius: 2px;
            font-size: 8px;
            font-weight: bold;
        """)
        self.summary_label.setMaximumHeight(16)
        self.main_layout.addWidget(self.summary_label)

        # Add/Edit button
        self.manage_button = QPushButton("⚙ Manage Harms")
        self.manage_button.setMaximumHeight(22)
        self.manage_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 9px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.manage_button.clicked.connect(self.open_management_dialog)
        self.main_layout.addWidget(self.manage_button)

    def set_component_name(self, component_name):
        """Set the component name for numbering"""
        self.component_name = component_name

    def update_display(self):
        """Update the visual display of harm descriptions"""
        # Clear existing widgets
        for i in reversed(range(self.harms_layout.count())):
            child = self.harms_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Add harm cards
        for i, harm in enumerate(self.harms):
            harm_card = self.create_harm_card(harm, i)
            self.harms_layout.addWidget(harm_card)

        # Update summary
        self.update_summary()

        # Update button text
        count = len(self.harms)
        if count == 0:
            self.manage_button.setText("+ Add Harms")
        else:
            self.manage_button.setText(f"⚙ Manage ({count})")

        # Update numbering manager if available
        if self.numbering_manager and self.component_name:
            self.numbering_manager.update_harm_description_count(self.component_name, count)

        # Emit signals
        self.harms_updated.emit(self.harms, self.rpn_data, count)
        if self.rpn_data:
            combined_rpn = self.get_combined_rpn_data()
            self.rpn_data_changed.emit(combined_rpn)

    def create_harm_card(self, harm_text, index):
        """Create a card widget for a single harm description with RPN info"""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        
        # Get RPN info for styling
        rpn_info = self.rpn_data.get(harm_text, {})
        rpn_value = rpn_info.get('rpn', 'Low')
        
        # Color based on RPN
        colors = {
            'High': '#ffebee',
            'Medium': '#fff8e1', 
            'Low': '#e8f5e8'
        }
        border_colors = {
            'High': '#f44336',
            'Medium': '#ff9800',
            'Low': '#4caf50'
        }
        
        bg_color = colors.get(rpn_value, '#f5f5f5')
        border_color = border_colors.get(rpn_value, '#bdbdbd')
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 3px;
                margin: 1px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(4, 3, 4, 3)
        layout.setSpacing(2)

        # Header with harm number and RPN
        header_layout = QHBoxLayout()
        
        num_label = QLabel(f"H{index + 1}:")
        num_label.setFont(QFont("Arial", 8, QFont.Bold))
        num_label.setStyleSheet("background: transparent; border: none;")
        header_layout.addWidget(num_label)

        header_layout.addStretch()

        if rpn_info:
            rpn_label = QLabel(rpn_value)
            rpn_label.setFont(QFont("Arial", 7, QFont.Bold))
            rpn_label.setStyleSheet(f"""
                background-color: {border_color};
                color: white;
                padding: 1px 4px;
                border-radius: 2px;
            """)
            header_layout.addWidget(rpn_label)

        layout.addLayout(header_layout)

        # Harm text (truncated if too long)
        display_text = harm_text
        if len(display_text) > 45:
            display_text = display_text[:42] + "..."
        
        text_label = QLabel(display_text)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("""
            background: transparent; 
            border: none; 
            padding: 1px;
            font-size: 9px;
        """)
        text_label.setToolTip(harm_text)  # Show full text on hover
        layout.addWidget(text_label)

        # RPN details
        if rpn_info:
            details_layout = QHBoxLayout()
            details_layout.setSpacing(4)
            
            sev_label = QLabel(f"S:{rpn_info.get('severity', 1)}")
            sev_label.setStyleSheet("font-size: 7px; color: #666; background: transparent; border: none;")
            details_layout.addWidget(sev_label)

            prob_label = QLabel(f"P:{rpn_info.get('probability', 1)}")
            prob_label.setStyleSheet("font-size: 7px; color: #666; background: transparent; border: none;")
            details_layout.addWidget(prob_label)

            details_layout.addStretch()
            layout.addLayout(details_layout)

        return card

    def update_summary(self):
        """Update the summary label"""
        if not self.harms:
            self.summary_label.setText("No harms")
            return

        rpn_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        for harm_text in self.harms:
            if harm_text in self.rpn_data:
                rpn_info = self.rpn_data[harm_text]
                rpn_counts[rpn_info['rpn']] += 1

        summary_text = f"Total: {len(self.harms)} | H:{rpn_counts['High']} M:{rpn_counts['Medium']} L:{rpn_counts['Low']}"
        
        # Color based on highest risk
        if rpn_counts['High'] > 0:
            bg_color = "#ffcdd2"
            text_color = "#c62828"
        elif rpn_counts['Medium'] > 0:
            bg_color = "#fff3e0"
            text_color = "#ef6c00"
        else:
            bg_color = "#e8f5e8"
            text_color = "#2e7d32"
            
        self.summary_label.setText(summary_text)
        self.summary_label.setStyleSheet(f"""
            background-color: {bg_color};
            color: {text_color};
            padding: 2px 4px;
            border-radius: 2px;
            font-size: 8px;
            font-weight: bold;
        """)

    def open_management_dialog(self):
        """Open the management dialog for harm descriptions"""
        dialog = HarmDescriptionDialog(
            self.parent_window, 
            self.harms.copy(), 
            self.selected_device
        )
        
        # Set existing RPN data in dialog
        dialog.rpn_data = self.rpn_data.copy()
        
        if dialog.exec_() == QDialog.Accepted:
            self.harms = dialog.get_harms()
            self.rpn_data = dialog.get_rpn_data()
            self.update_display()
            
            # Add new harms to documents
            for harm in self.harms:
                self.check_and_add_to_documents(harm)

    def check_and_add_to_documents(self, harm_text):
        """Check if the harm is new and add it to the dynamic documents"""
        global harm_description_documents
        if add_new_document(harm_description_documents, harm_text, HARM_FILE, "Harm Description"):
            refresh_indices()

    def get_harms_list(self):
        """Get the harms as a list"""
        return self.harms.copy()

    def get_rpn_data(self):
        """Get RPN data dictionary"""
        return self.rpn_data.copy()

    def set_harms_and_rpn(self, harms_list, rpn_data_dict):
        """Set the harms and RPN data"""
        if isinstance(harms_list, list):
            self.harms = [harm.strip() for harm in harms_list if harm.strip()]
        if isinstance(rpn_data_dict, dict):
            self.rpn_data = rpn_data_dict.copy()
        self.update_display()

    def get_harms_text(self):
        """Get all harms as formatted text"""
        if not self.harms:
            return ""
        return " | ".join([f"{i+1}. {harm}" for i, harm in enumerate(self.harms)])

    def get_harms_count(self):
        """Get the count of harms"""
        return len(self.harms)

    def get_combined_rpn_data(self):
        """Get combined RPN data for the main table"""
        if not self.rpn_data:
            return {'severity': 1, 'probability': 1, 'rpn': 'Low'}

        # Calculate weighted average or highest risk
        max_severity = max([data['severity'] for data in self.rpn_data.values()])
        max_probability = max([data['probability'] for data in self.rpn_data.values()])
        
        # Use the highest risk combination
        combined_rpn = self.calculate_rpn(max_severity, max_probability)
        
        return {
            'severity': max_severity,
            'probability': max_probability,
            'rpn': combined_rpn
        }

    def calculate_rpn(self, severity, probability):
        """Calculate RPN based on device-specific matrix or default logic"""
        if self.selected_device:
            return self.get_rpn_from_matrix(self.selected_device, severity, probability)
        else:
            return self.get_default_rpn(severity, probability)

    def get_rpn_from_matrix(self, device, severity, probability):
        """Get RPN from device-specific matrix"""
        matrix_file = os.path.join('Risk Matrix', f"{device.replace(' ', '_')}_matrix.json")
        
        try:
            if os.path.exists(matrix_file):
                with open(matrix_file, 'r') as f:
                    matrix_data = json.load(f)
                
                row = severity - 1
                col = probability - 1
                
                if 0 <= row <= 4 and 0 <= col <= 4:
                    key = f"{row},{col}"
                    if key in matrix_data:
                        return matrix_data[key]["text"]
            
            return self.get_default_rpn(severity, probability)
            
        except Exception as e:
            print(f"Error reading matrix for {device}: {e}")
            return self.get_default_rpn(severity, probability)

    def get_default_rpn(self, severity, probability):
        """Default RPN calculation logic"""
        if (severity >= 4 and probability >= 3) or (severity == 3 and probability >= 4):
            return 'High'
        elif ((severity >= 4 and probability <= 3) or (severity < 3 and probability == 5)
              or (severity == 2 and probability >= 3) or (severity == 3 and probability in [2, 3])):
            return 'Medium'
        elif ((severity == 1 and probability <= 4) or (severity == 2 and probability in [1, 2]) or
              (severity == 3 and probability == 1)):
            return 'Low'
        else:
            return 'Unknown'

    def set_selected_device(self, device):
        """Update the selected device for RPN calculations"""
        self.selected_device = device
        # Recalculate RPN for all harms
        for harm_text in self.harms:
            if harm_text in self.rpn_data:
                rpn_info = self.rpn_data[harm_text]
                new_rpn = self.calculate_rpn(rpn_info['severity'], rpn_info['probability'])
                self.rpn_data[harm_text]['rpn'] = new_rpn
        self.update_display()
