from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import json
import os
from search import *

class EnhancedHarmDescriptionDialog(QDialog):
    """Enhanced dialog for managing multiple harm descriptions with RPN calculation"""
    harms_updated = pyqtSignal(list, dict)  # harms list, rpn_data dict

    def __init__(self, parent=None, existing_harms=None, selected_device=None):
        super().__init__(parent)
        self.setWindowTitle("Harm Description Manager with RPN Calculation")
        self.setGeometry(200, 200, 800, 600)
        self.harms = existing_harms or []
        self.selected_device = selected_device
        self.rpn_data = {}  # Store RPN data for each harm
        self.setupUI()
        self.update_display()

    def setupUI(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Manage Harm Descriptions with RPN Calculation")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)

        # Device info
        if self.selected_device:
            device_label = QLabel(f"Selected Device: {self.selected_device}")
            device_label.setStyleSheet("color: #2c5aa0; font-weight: bold;")
            layout.addWidget(device_label)

        # Input section
        input_group = QGroupBox("Add New Harm Description")
        input_layout = QVBoxLayout(input_group)

        # Harm description input
        harm_label = QLabel("Harm Description:")
        input_layout.addWidget(harm_label)

        self.harm_edit = QLineEdit()
        self.harm_edit.setPlaceholderText("Enter harm description...")
        self.harm_edit.textChanged.connect(self.update_suggestions)
        input_layout.addWidget(self.harm_edit)

        # Search suggestions
        self.suggestions_list = QListWidget()
        self.suggestions_list.setMaximumHeight(80)
        self.suggestions_list.itemDoubleClicked.connect(self.select_suggestion)
        input_layout.addWidget(self.suggestions_list)

        # RPN calculation section
        rpn_layout = QHBoxLayout()

        # Severity
        sev_layout = QVBoxLayout()
        sev_layout.addWidget(QLabel("Severity:"))
        self.severity_combo = QComboBox()
        self.severity_combo.addItems([
            "1 - Discomfort", "2 - Minor", "3 - Serious", 
            "4 - Critical", "5 - Catastrophic"
        ])
        self.severity_combo.currentIndexChanged.connect(self.update_rpn_preview)
        sev_layout.addWidget(self.severity_combo)
        rpn_layout.addLayout(sev_layout)

        # Probability
        prob_layout = QVBoxLayout()
        prob_layout.addWidget(QLabel("Probability:"))
        self.probability_combo = QComboBox()
        self.probability_combo.addItems([
            "1 - Improbable", "2 - Remote", "3 - Occasional",
            "4 - Probable", "5 - Frequent"
        ])
        self.probability_combo.currentIndexChanged.connect(self.update_rpn_preview)
        prob_layout.addWidget(self.probability_combo)
        rpn_layout.addLayout(prob_layout)

        # RPN Preview
        rpn_preview_layout = QVBoxLayout()
        rpn_preview_layout.addWidget(QLabel("RPN:"))
        self.rpn_preview_label = QLabel("Low")
        self.rpn_preview_label.setStyleSheet("""
            background-color: #2ecc71;
            color: white;
            padding: 5px;
            border-radius: 3px;
            font-weight: bold;
            text-align: center;
        """)
        rpn_preview_layout.addWidget(self.rpn_preview_label)
        rpn_layout.addLayout(rpn_preview_layout)

        input_layout.addLayout(rpn_layout)

        # Add button
        add_btn = QPushButton("Add Harm Description")
        add_btn.clicked.connect(self.add_harm)
        input_layout.addWidget(add_btn)

        layout.addWidget(input_group)

        # Current harms display
        current_group = QGroupBox("Current Harm Descriptions")
        current_layout = QVBoxLayout(current_group)

        self.harms_scroll = QScrollArea()
        self.harms_scroll.setWidgetResizable(True)
        self.harms_scroll.setMaximumHeight(250)

        self.harms_container = QWidget()
        self.harms_layout = QVBoxLayout(self.harms_container)
        self.harms_scroll.setWidget(self.harms_container)

        current_layout.addWidget(self.harms_scroll)
        layout.addWidget(current_group)

        # Total RPN summary
        self.summary_label = QLabel("Total RPN Summary: No harms added")
        self.summary_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.summary_label.setStyleSheet("background-color: #ecf0f1; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.summary_label)

        # Dialog buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # Initial RPN update
        self.update_rpn_preview()

    def update_suggestions(self):
        """Update search suggestions based on input"""
        search_terms = self.harm_edit.text()

        if not search_terms.strip():
            self.suggestions_list.clear()
            return

        # Search in harm description documents
        results = search_documents(search_terms, harm_description_inverted_index, harm_description_documents)
        highlighted_results = rank_and_highlight(results, search_terms, harm_description_documents, scores)

        self.suggestions_list.clear()
        if highlighted_results:
            for doc_id, content, score in highlighted_results[:8]:
                clean_content = content.replace(" *", " ").replace("* ", " ")
                self.suggestions_list.addItem(f"ID: {doc_id} - {clean_content}")

    def select_suggestion(self, item):
        """Select a suggestion and populate the text field"""
        text = item.text()
        if " - " in text:
            content = text.split(" - ", 1)[1]
            self.harm_edit.setText(content)

    def update_rpn_preview(self):
        """Update the RPN preview based on current selections"""
        severity = self.severity_combo.currentIndex() + 1
        probability = self.probability_combo.currentIndex() + 1
        
        rpn = self.calculate_rpn(severity, probability)
        
        # Update preview label
        colors = {"High": "#e74c3c", "Medium": "#f1c40f", "Low": "#2ecc71"}
        color = colors.get(rpn, "#95a5a6")
        
        self.rpn_preview_label.setText(rpn)
        self.rpn_preview_label.setStyleSheet(f"""
            background-color: {color};
            color: {'white' if rpn == 'High' else 'black'};
            padding: 5px;
            border-radius: 3px;
            font-weight: bold;
            text-align: center;
        """)

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

    def add_harm(self):
        """Add a new harm description with RPN data"""
        harm_text = self.harm_edit.text().strip()
        if harm_text and harm_text not in self.harms:
            severity = self.severity_combo.currentIndex() + 1
            probability = self.probability_combo.currentIndex() + 1
            rpn = self.calculate_rpn(severity, probability)
            
            self.harms.append(harm_text)
            self.rpn_data[harm_text] = {
                'severity': severity,
                'probability': probability,
                'rpn': rpn
            }
            
            self.check_and_add_to_documents(harm_text)
            self.harm_edit.clear()
            self.update_display()
            self.update_summary()
            self.harms_updated.emit(self.harms, self.rpn_data)

    def remove_harm(self, index):
        """Remove a harm description"""
        if 0 <= index < len(self.harms):
            reply = QMessageBox.question(self, 'Remove Harm',
                                       f'Remove this harm description?',
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            if reply == QMessageBox.Yes:
                harm_text = self.harms.pop(index)
                if harm_text in self.rpn_data:
                    del self.rpn_data[harm_text]
                self.update_display()
                self.update_summary()
                self.harms_updated.emit(self.harms, self.rpn_data)

    def update_display(self):
        """Update the display of current harms"""
        # Clear existing widgets
        for i in reversed(range(self.harms_layout.count())):
            child = self.harms_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Add harm widgets
        for i, harm in enumerate(self.harms):
            harm_widget = self.create_harm_widget(harm, i)
            self.harms_layout.addWidget(harm_widget)

    def create_harm_widget(self, harm_text, index):
        """Create a widget for a single harm with RPN info"""
        container = QFrame()
        container.setFrameStyle(QFrame.Box)
        container.setStyleSheet("""
            QFrame {
                background-color: #ffeaa7;
                border: 1px solid #fdcb6e;
                border-radius: 5px;
                padding: 8px;
                margin: 2px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header with harm number and remove button
        header_layout = QHBoxLayout()
        
        num_label = QLabel(f"Harm {index + 1}:")
        num_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(num_label)

        header_layout.addStretch()

        # Remove button
        remove_btn = QPushButton("×")
        remove_btn.setMaximumSize(20, 20)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_harm(index))
        header_layout.addWidget(remove_btn)

        layout.addLayout(header_layout)

        # Harm text
        text_label = QLabel(harm_text)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("font-size: 11px; margin-bottom: 5px;")
        layout.addWidget(text_label)

        # RPN info
        if harm_text in self.rpn_data:
            rpn_info = self.rpn_data[harm_text]
            rpn_layout = QHBoxLayout()
            
            sev_label = QLabel(f"Severity: {rpn_info['severity']}")
            sev_label.setStyleSheet("font-size: 9px; color: #2c3e50;")
            rpn_layout.addWidget(sev_label)

            prob_label = QLabel(f"Probability: {rpn_info['probability']}")
            prob_label.setStyleSheet("font-size: 9px; color: #2c3e50;")
            rpn_layout.addWidget(prob_label)

            rpn_label = QLabel(f"RPN: {rpn_info['rpn']}")
            rpn_label.setStyleSheet("font-size: 9px; font-weight: bold; color: #2c3e50;")
            rpn_layout.addWidget(rpn_label)

            layout.addLayout(rpn_layout)

        return container

    def update_summary(self):
        """Update the RPN summary"""
        if not self.harms:
            self.summary_label.setText("Total RPN Summary: No harms added")
            return

        rpn_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        total_severity = 0
        total_probability = 0

        for harm_text in self.harms:
            if harm_text in self.rpn_data:
                rpn_info = self.rpn_data[harm_text]
                rpn_counts[rpn_info['rpn']] += 1
                total_severity += rpn_info['severity']
                total_probability += rpn_info['probability']

        avg_severity = total_severity / len(self.harms) if self.harms else 0
        avg_probability = total_probability / len(self.harms) if self.harms else 0

        summary_text = f"Total Harms: {len(self.harms)} | High: {rpn_counts['High']} | Medium: {rpn_counts['Medium']} | Low: {rpn_counts['Low']} | Avg Severity: {avg_severity:.1f} | Avg Probability: {avg_probability:.1f}"
        self.summary_label.setText(summary_text)

    def check_and_add_to_documents(self, harm_text):
        """Check if the harm is new and add it to the dynamic documents"""
        global harm_description_documents
        if add_new_document(harm_description_documents, harm_text, HARM_FILE, "Harm Description"):
            refresh_indices()

    def get_harms(self):
        """Get all harms as a list"""
        return self.harms.copy()

    def get_rpn_data(self):
        """Get RPN data dictionary"""
        return self.rpn_data.copy()

    def get_harms_text(self):
        """Get all harms as formatted text"""
        if not self.harms:
            return ""
        return " | ".join([f"{i+1}. {harm}" for i, harm in enumerate(self.harms)])

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
