from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QScrollArea, QSpinBox, QWidget, QMessageBox, QDialog, QListWidget, QLineEdit
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette
import json
from search import *

class HarmDescriptionWidget(QWidget):
    """Widget to manage multiple harm descriptions with severity/probability for each"""

    harms_updated = pyqtSignal(list)  # Signal emitted when harms are updated

    def __init__(self, initial_harm="", parent=None):
        super().__init__(parent)
        self.harms = []
        if initial_harm.strip():
            self.harms.append({
                'text': initial_harm.strip(),
                'severity': 1,
                'probability': 1,
                'rpn': 'Low'
            })

        self.setupUI()
        self.update_display()

    def setupUI(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(3)

        # Scroll area for harms
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(300)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.harms_container = QWidget()
        self.harms_layout = QVBoxLayout(self.harms_container)
        self.harms_layout.setContentsMargins(2, 2, 2, 2)
        self.harms_layout.setSpacing(2)

        self.scroll_area.setWidget(self.harms_container)
        self.main_layout.addWidget(self.scroll_area)

        # Add button
        self.add_button = QPushButton("+ Add Harm Description")
        self.add_button.setMaximumHeight(25)
        self.add_button.clicked.connect(self.add_new_harm)
        self.main_layout.addWidget(self.add_button)

    def update_display(self):
        """Update the visual display of the harms"""
        try:
            # Clear existing widgets
            for i in reversed(range(self.harms_layout.count())):
                child = self.harms_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)

            # Add harm widgets
            for i, harm in enumerate(self.harms):
                harm_widget = self.create_harm_widget(harm, i)
                self.harms_layout.addWidget(harm_widget)

            # Emit signal with updated harms
            self.harms_updated.emit(self.harms)
        except Exception as e:
            print(f"Error updating harm display: {e}")

    def create_harm_widget(self, harm_data, index):
        """Create a widget for a single harm description"""
        container = QFrame()
        container.setFrameStyle(QFrame.Box)
        container.setStyleSheet("""
            QFrame {
                background-color: #f8d7da;
                border: 1px solid #dc3545;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header with harm number and controls
        header_layout = QHBoxLayout()
        
        # Harm number and ID
        harm_label = QLabel(f"Harm {index + 1} (ID: {index + 1}):")
        harm_label.setFont(QFont("Arial", 9, QFont.Bold))
        harm_label.setStyleSheet("color: #721c24; background: transparent; border: none;")
        header_layout.addWidget(harm_label)

        header_layout.addStretch()

        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setMaximumSize(40, 20)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 8px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_harm(index))
        header_layout.addWidget(edit_btn)

        # Remove button (only show if more than one harm)
        if len(self.harms) > 1:
            remove_btn = QPushButton("×")
            remove_btn.setMaximumSize(20, 20)
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            remove_btn.clicked.connect(lambda: self.remove_harm(index))
            header_layout.addWidget(remove_btn)

        layout.addLayout(header_layout)

        # Harm text
        harm_text = harm_data.get('text', '') if isinstance(harm_data, dict) else str(harm_data)
        harm_text_label = QLabel(harm_text)
        harm_text_label.setWordWrap(True)
        harm_text_label.setStyleSheet("background: transparent; border: none; padding: 2px; font-size: 10px;")
        layout.addWidget(harm_text_label)

        # Severity and Probability controls (only for dict format)
        if isinstance(harm_data, dict):
            controls_layout = QHBoxLayout()
            
            # Severity
            sev_label = QLabel("Severity:")
            sev_label.setStyleSheet("font-size: 9px; font-weight: bold;")
            controls_layout.addWidget(sev_label)
            
            sev_spinbox = QSpinBox()
            sev_spinbox.setRange(1, 5)
            sev_spinbox.setValue(harm_data.get('severity', 1))
            sev_spinbox.setMaximumWidth(50)
            sev_spinbox.valueChanged.connect(lambda val: self.update_harm_severity(index, val))
            controls_layout.addWidget(sev_spinbox)

            # Probability
            prob_label = QLabel("Probability:")
            prob_label.setStyleSheet("font-size: 9px; font-weight: bold;")
            controls_layout.addWidget(prob_label)
            
            prob_spinbox = QSpinBox()
            prob_spinbox.setRange(1, 5)
            prob_spinbox.setValue(harm_data.get('probability', 1))
            prob_spinbox.setMaximumWidth(50)
            prob_spinbox.valueChanged.connect(lambda val: self.update_harm_probability(index, val))
            controls_layout.addWidget(prob_spinbox)

            # RPN display
            rpn_value = harm_data.get('rpn', 'Low')
            rpn_label = QLabel(f"RPN: {rpn_value}")
            rpn_label.setStyleSheet(f"""
                font-size: 9px; font-weight: bold; padding: 2px 5px;
                background-color: {self.get_rpn_color(rpn_value)};
                border-radius: 3px;
            """)
            controls_layout.addWidget(rpn_label)

            controls_layout.addStretch()
            layout.addLayout(controls_layout)

        return container

    def get_rpn_color(self, rpn):
        """Get color for RPN display"""
        colors = {"High": "#dc3545", "Medium": "#ffc107", "Low": "#28a745"}
        return colors.get(rpn, "#6c757d")

    def add_new_harm(self):
        """Add a new harm description"""
        dialog = HarmDescriptionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_harm = dialog.get_harm_text()
            if new_harm.strip():
                harm_data = {
                    'text': new_harm.strip(),
                    'severity': 1,
                    'probability': 1,
                    'rpn': 'Low'
                }
                self.harms.append(harm_data)
                # Add to dynamic documents if it's new
                self.check_and_add_to_documents(new_harm.strip())
                self.update_display()

    def edit_harm(self, index):
        """Edit an existing harm"""
        if 0 <= index < len(self.harms):
            current_text = self.harms[index].get('text', '') if isinstance(self.harms[index], dict) else str(self.harms[index])
            dialog = HarmDescriptionDialog(self, current_text)
            if dialog.exec_() == QDialog.Accepted:
                new_harm = dialog.get_harm_text()
                if new_harm.strip():
                    if isinstance(self.harms[index], dict):
                        self.harms[index]['text'] = new_harm.strip()
                    else:
                        # Convert old format to new format
                        self.harms[index] = {
                            'text': new_harm.strip(),
                            'severity': 1,
                            'probability': 1,
                            'rpn': 'Low'
                        }
                    # Add to dynamic documents if it's new
                    self.check_and_add_to_documents(new_harm.strip())
                    self.update_display()

    def remove_harm(self, index):
        """Remove a harm from the list"""
        if 0 <= index < len(self.harms) and len(self.harms) > 1:
            reply = QMessageBox.question(self, 'Remove Harm',
                                         f'Are you sure you want to remove Harm {index + 1}?',
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.harms.pop(index)
                self.update_display()

    def update_harm_severity(self, index, severity):
        """Update severity for a specific harm"""
        try:
            if 0 <= index < len(self.harms):
                if isinstance(self.harms[index], dict):
                    self.harms[index]['severity'] = severity
                    self.harms[index]['rpn'] = self.calculate_rpn(severity, self.harms[index].get('probability', 1))
                    self.update_display()
        except Exception as e:
            print(f"Error updating harm severity: {e}")

    def update_harm_probability(self, index, probability):
        """Update probability for a specific harm"""
        try:
            if 0 <= index < len(self.harms):
                if isinstance(self.harms[index], dict):
                    self.harms[index]['probability'] = probability
                    self.harms[index]['rpn'] = self.calculate_rpn(self.harms[index].get('severity', 1), probability)
                    self.update_display()
        except Exception as e:
            print(f"Error updating harm probability: {e}")

    def calculate_rpn(self, severity, probability):
        """Calculate RPN based on severity and probability"""
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

    def check_and_add_to_documents(self, harm_text):
        """Check if the harm is new and add it to the dynamic documents"""
        try:
            global harm_description_documents
            if add_new_document(harm_description_documents, harm_text, HARM_FILE, "Harm Description"):
                refresh_indices()
        except:
            pass  # Ignore if search system not available

    def get_harms_data(self):
        """Get the harms data (with severity/probability info)"""
        return self.harms.copy()

    def set_harms_data(self, harms_data):
        """Set the harms from data"""
        if isinstance(harms_data, list):
            self.harms = []
            for harm in harms_data:
                if isinstance(harm, dict):
                    self.harms.append(harm)
                else:
                    # Convert old string format to new dict format
                    self.harms.append({
                        'text': str(harm).strip(),
                        'severity': 1,
                        'probability': 1,
                        'rpn': 'Low'
                    })
            if not self.harms:
                self.harms = [{
                    'text': "",
                    'severity': 1,
                    'probability': 1,
                    'rpn': 'Low'
                }]
            self.update_display()

    def get_harms_list(self):
        """Get the harms as a simple list of strings (for backward compatibility)"""
        result = []
        for harm in self.harms:
            if isinstance(harm, dict):
                result.append(harm.get('text', ''))
            else:
                result.append(str(harm))
        return result

    def set_harms_list(self, harms_list):
        """Set the harms from a simple list of strings (for backward compatibility)"""
        if isinstance(harms_list, list):
            self.harms = []
            for harm_text in harms_list:
                if harm_text.strip():
                    self.harms.append({
                        'text': harm_text.strip(),
                        'severity': 1,
                        'probability': 1,
                        'rpn': 'Low'
                    })
            if not self.harms:
                self.harms = [{
                    'text': "",
                    'severity': 1,
                    'probability': 1,
                    'rpn': 'Low'
                }]
            self.update_display()


class HarmDescriptionDialog(QDialog):
    """Dialog for adding/editing harm descriptions with search functionality"""

    def __init__(self, parent=None, initial_text=""):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Harm Description")
        self.setGeometry(200, 200, 600, 400)
        self.initial_text = initial_text
        self.setupUI()

        if initial_text:
            self.harm_edit.setText(initial_text)

    def setupUI(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Enter Harm Description:")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)

        # Harm input
        self.harm_edit = QLineEdit()
        self.harm_edit.setPlaceholderText("Enter the harm description...")
        self.harm_edit.textChanged.connect(self.update_suggestions)
        layout.addWidget(self.harm_edit)

        # Search suggestions
        suggestions_label = QLabel("Suggestions:")
        suggestions_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(suggestions_label)

        self.suggestions_list = QListWidget()
        self.suggestions_list.setMaximumHeight(150)
        self.suggestions_list.itemDoubleClicked.connect(self.select_suggestion)
        layout.addWidget(self.suggestions_list)

        # Buttons
        button_layout = QHBoxLayout()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def update_suggestions(self):
        """Update search suggestions based on input"""
        search_terms = self.harm_edit.text()

        if not search_terms.strip():
            self.suggestions_list.clear()
            return

        try:
            # Search in harm description documents
            results = search_documents(search_terms, harm_description_inverted_index, harm_description_documents)
            highlighted_results = rank_and_highlight(results, search_terms, harm_description_documents, scores)

            self.suggestions_list.clear()
            if highlighted_results:
                for doc_id, content, score in highlighted_results[:10]:  # Limit to top 10 results
                    # Clean up the content (remove highlighting for display)
                    clean_content = content.replace(" *", " ").replace("* ", " ")
                    self.suggestions_list.addItem(f"ID: {doc_id} - {clean_content}")
        except:
            pass  # Ignore if search system not available

    def select_suggestion(self, item):
        """Select a suggestion and populate the text field"""
        text = item.text()
        # Extract the content after "ID: X - "
        if " - " in text:
            content = text.split(" - ", 1)[1]
            self.harm_edit.setText(content)

    def get_harm_text(self):
        """Get the entered harm text"""
        return self.harm_edit.text().strip()
