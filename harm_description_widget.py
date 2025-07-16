from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from search import *

class HarmDescriptionWidget(QWidget):
    """Widget to manage multiple harm descriptions with severity/probability"""
    
    harms_updated = pyqtSignal(list)
    
    def __init__(self, initial_harm="", parent=None):
        super().__init__(parent)
        self.harms = []
        if initial_harm.strip():
            self.harms.append({
                'description': initial_harm.strip(),
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
        self.scroll_area.setMaximumHeight(250)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.harm_container = QWidget()
        self.harm_layout = QVBoxLayout(self.harm_container)
        self.harm_layout.setContentsMargins(2, 2, 2, 2)
        self.harm_layout.setSpacing(2)
        
        self.scroll_area.setWidget(self.harm_container)
        self.main_layout.addWidget(self.scroll_area)
        
        # Add button
        self.add_button = QPushButton("+ Add Harm Description")
        self.add_button.setMaximumHeight(25)
        self.add_button.clicked.connect(self.add_new_harm)
        self.main_layout.addWidget(self.add_button)
    
    def update_display(self):
        """Update the visual display of harms"""
        # Clear existing widgets
        for i in reversed(range(self.harm_layout.count())):
            child = self.harm_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add harm widgets
        for i, harm in enumerate(self.harms):
            harm_widget = self.create_harm_widget(harm, i)
            self.harm_layout.addWidget(harm_widget)
        
        # Emit signal with updated harms
        self.harms_updated.emit(self.harms)
    
    def create_harm_widget(self, harm_data, index):
        """Create a widget for a single harm description with severity/probability"""
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
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Top row: Harm description and buttons
        top_layout = QHBoxLayout()
        
        # Harm number
        harm_label = QLabel(f"Harm {index + 1}:")
        harm_label.setFont(QFont("Arial", 9, QFont.Bold))
        harm_label.setStyleSheet("color: #721c24; background: transparent; border: none;")
        harm_label.setMinimumWidth(60)
        top_layout.addWidget(harm_label)
        
        # Harm text
        harm_text_label = QLabel(harm_data['description'])
        harm_text_label.setWordWrap(True)
        harm_text_label.setStyleSheet("background: transparent; border: none; padding: 2px;")
        top_layout.addWidget(harm_text_label, 1)
        
        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setMaximumSize(40, 20)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 8px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_harm(index))
        top_layout.addWidget(edit_btn)
        
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
            top_layout.addWidget(remove_btn)
        
        main_layout.addLayout(top_layout)
        
        # Bottom row: Severity, Probability, RPN
        bottom_layout = QHBoxLayout()
        
        # Severity
        sev_label = QLabel("Severity:")
        sev_label.setStyleSheet("background: transparent; border: none; font-weight: bold;")
        bottom_layout.addWidget(sev_label)
        
        severity_spin = QSpinBox()
        severity_spin.setRange(1, 5)
        severity_spin.setValue(harm_data['severity'])
        severity_spin.valueChanged.connect(lambda v: self.update_harm_severity(index, v))
        bottom_layout.addWidget(severity_spin)
        
        # Probability
        prob_label = QLabel("Probability:")
        prob_label.setStyleSheet("background: transparent; border: none; font-weight: bold;")
        bottom_layout.addWidget(prob_label)
        
        probability_spin = QSpinBox()
        probability_spin.setRange(1, 5)
        probability_spin.setValue(harm_data['probability'])
        probability_spin.valueChanged.connect(lambda v: self.update_harm_probability(index, v))
        bottom_layout.addWidget(probability_spin)
        
        # RPN
        rpn_label = QLabel("RPN:")
        rpn_label.setStyleSheet("background: transparent; border: none; font-weight: bold;")
        bottom_layout.addWidget(rpn_label)
        
        rpn_display = QLabel(harm_data['rpn'])
        rpn_color = {"High": "red", "Medium": "yellow", "Low": "green"}.get(harm_data['rpn'], "lightgray")
        rpn_display.setStyleSheet(f"background-color: {rpn_color}; border: 1px solid black; padding: 2px; border-radius: 3px;")
        bottom_layout.addWidget(rpn_display)
        
        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)
        
        return container
    
    def update_harm_severity(self, index, severity):
        """Update severity for a harm and recalculate RPN"""
        if 0 <= index < len(self.harms):
            self.harms[index]['severity'] = severity
            self.harms[index]['rpn'] = self.calculate_rpn(severity, self.harms[index]['probability'])
            self.update_display()
    
    def update_harm_probability(self, index, probability):
        """Update probability for a harm and recalculate RPN"""
        if 0 <= index < len(self.harms):
            self.harms[index]['probability'] = probability
            self.harms[index]['rpn'] = self.calculate_rpn(self.harms[index]['severity'], probability)
            self.update_display()
    
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
    
    def add_new_harm(self):
        """Add a new harm description"""
        dialog = HarmDescriptionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_harm = dialog.get_harm_text()
            if new_harm.strip():
                harm_data = {
                    'description': new_harm.strip(),
                    'severity': 1,
                    'probability': 1,
                    'rpn': 'Low'
                }
                self.harms.append(harm_data)
                self.check_and_add_to_documents(new_harm.strip())
                self.update_display()
    
    def edit_harm(self, index):
        """Edit an existing harm"""
        if 0 <= index < len(self.harms):
            dialog = HarmDescriptionDialog(self, self.harms[index]['description'])
            if dialog.exec_() == QDialog.Accepted:
                new_harm = dialog.get_harm_text()
                if new_harm.strip():
                    self.harms[index]['description'] = new_harm.strip()
                    self.check_and_add_to_documents(new_harm.strip())
                    self.update_display()
    
    def remove_harm(self, index):
        """Remove a harm"""
        if 0 <= index < len(self.harms) and len(self.harms) > 1:
            reply = QMessageBox.question(self, 'Remove Harm',
                                       f'Are you sure you want to remove Harm {index + 1}?',
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.harms.pop(index)
                self.update_display()
    
    def check_and_add_to_documents(self, harm_text):
        """Check if the harm is new and add it to the dynamic documents"""
        global harm_description_documents
        if add_new_document(harm_description_documents, harm_text, HARM_FILE, "Harm Description"):
            refresh_indices()
    
    def get_harms_list(self):
        """Get the harms as a list"""
        return self.harms.copy()
    
    def set_harms(self, harms_list):
        """Set the harms from a list"""
        if isinstance(harms_list, list):
            self.harms = harms_list.copy()
            if not self.harms:
                self.harms = [{'description': '', 'severity': 1, 'probability': 1, 'rpn': 'Low'}]
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
        
        # Search in harm description documents
        results = search_documents(search_terms, harm_description_inverted_index, harm_description_documents)
        highlighted_results = rank_and_highlight(results, search_terms, harm_description_documents, scores)
        
        self.suggestions_list.clear()
        if highlighted_results:
            for doc_id, content, score in highlighted_results[:10]:
                clean_content = content.replace(" *", " ").replace("* ", " ")
                self.suggestions_list.addItem(f"ID: {doc_id} - {clean_content}")
    
    def select_suggestion(self, item):
        """Select a suggestion and populate the text field"""
        text = item.text()
        if " - " in text:
            content = text.split(" - ", 1)[1]
            self.harm_edit.setText(content)
    
    def get_harm_text(self):
        """Get the entered harm text"""
        return self.harm_edit.text().strip()
