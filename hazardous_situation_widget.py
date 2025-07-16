from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from search import *

class HazardousSituationWidget(QWidget):
    """Widget to manage multiple hazardous situations"""
    
    situations_updated = pyqtSignal(list)
    
    def __init__(self, initial_situation="", parent=None):
        super().__init__(parent)
        self.situations = []
        if initial_situation.strip():
            self.situations.append(initial_situation.strip())
        
        self.setupUI()
        self.update_display()
    
    def setupUI(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(3)
        
        # Scroll area for situations
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(200)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.situation_container = QWidget()
        self.situation_layout = QVBoxLayout(self.situation_container)
        self.situation_layout.setContentsMargins(2, 2, 2, 2)
        self.situation_layout.setSpacing(2)
        
        self.scroll_area.setWidget(self.situation_container)
        self.main_layout.addWidget(self.scroll_area)
        
        # Add button
        self.add_button = QPushButton("+ Add Hazardous Situation")
        self.add_button.setMaximumHeight(25)
        self.add_button.clicked.connect(self.add_new_situation)
        self.main_layout.addWidget(self.add_button)
    
    def update_display(self):
        """Update the visual display of situations"""
        # Clear existing widgets
        for i in reversed(range(self.situation_layout.count())):
            child = self.situation_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add situation widgets
        for i, situation in enumerate(self.situations):
            situation_widget = self.create_situation_widget(situation, i)
            self.situation_layout.addWidget(situation_widget)
        
        # Emit signal with updated situations
        self.situations_updated.emit(self.situations)
    
    def create_situation_widget(self, situation_text, index):
        """Create a widget for a single hazardous situation"""
        container = QFrame()
        container.setFrameStyle(QFrame.Box)
        container.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Situation number
        sit_label = QLabel(f"Situation {index + 1}:")
        sit_label.setFont(QFont("Arial", 9, QFont.Bold))
        sit_label.setStyleSheet("color: #856404; background: transparent; border: none;")
        sit_label.setMinimumWidth(80)
        layout.addWidget(sit_label)
        
        # Situation text
        situation_label = QLabel(situation_text)
        situation_label.setWordWrap(True)
        situation_label.setStyleSheet("background: transparent; border: none; padding: 2px;")
        layout.addWidget(situation_label, 1)
        
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
        edit_btn.clicked.connect(lambda: self.edit_situation(index))
        layout.addWidget(edit_btn)
        
        # Remove button (only show if more than one situation)
        if len(self.situations) > 1:
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
            remove_btn.clicked.connect(lambda: self.remove_situation(index))
            layout.addWidget(remove_btn)
        
        return container
    
    def add_new_situation(self):
        """Add a new hazardous situation"""
        dialog = HazardousSituationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_situation = dialog.get_situation_text()
            if new_situation.strip():
                self.situations.append(new_situation.strip())
                self.check_and_add_to_documents(new_situation.strip())
                self.update_display()
    
    def edit_situation(self, index):
        """Edit an existing situation"""
        if 0 <= index < len(self.situations):
            dialog = HazardousSituationDialog(self, self.situations[index])
            if dialog.exec_() == QDialog.Accepted:
                new_situation = dialog.get_situation_text()
                if new_situation.strip():
                    self.situations[index] = new_situation.strip()
                    self.check_and_add_to_documents(new_situation.strip())
                    self.update_display()
    
    def remove_situation(self, index):
        """Remove a situation"""
        if 0 <= index < len(self.situations) and len(self.situations) > 1:
            reply = QMessageBox.question(self, 'Remove Situation',
                                       f'Are you sure you want to remove Situation {index + 1}?',
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.situations.pop(index)
                self.update_display()
    
    def check_and_add_to_documents(self, situation_text):
        """Check if the situation is new and add it to the dynamic documents"""
        global hazardous_situation_documents
        if add_new_document(hazardous_situation_documents, situation_text, HAZARDOUS_FILE, "Hazardous Situation"):
            refresh_indices()
    
    def get_situations_list(self):
        """Get the situations as a list"""
        return self.situations.copy()
    
    def set_situations(self, situations_list):
        """Set the situations from a list"""
        if isinstance(situations_list, list):
            self.situations = [sit.strip() for sit in situations_list if sit.strip()]
            if not self.situations:
                self.situations = [""]
            self.update_display()


class HazardousSituationDialog(QDialog):
    """Dialog for adding/editing hazardous situations with search functionality"""
    
    def __init__(self, parent=None, initial_text=""):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Hazardous Situation")
        self.setGeometry(200, 200, 600, 400)
        self.initial_text = initial_text
        self.setupUI()
        
        if initial_text:
            self.situation_edit.setText(initial_text)
    
    def setupUI(self):
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Enter Hazardous Situation:")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Situation input
        self.situation_edit = QLineEdit()
        self.situation_edit.setPlaceholderText("Enter the hazardous situation description...")
        self.situation_edit.textChanged.connect(self.update_suggestions)
        layout.addWidget(self.situation_edit)
        
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
        search_terms = self.situation_edit.text()
        
        if not search_terms.strip():
            self.suggestions_list.clear()
            return
        
        # Search in hazardous situation documents
        results = search_documents(search_terms, hazardous_situation_inverted_index, hazardous_situation_documents)
        highlighted_results = rank_and_highlight(results, search_terms, hazardous_situation_documents, scores)
        
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
            self.situation_edit.setText(content)
    
    def get_situation_text(self):
        """Get the entered situation text"""
        return self.situation_edit.text().strip()