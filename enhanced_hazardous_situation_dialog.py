from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import json
from search import *

class EnhancedHazardousSituationDialog(QDialog):
    """Enhanced dialog for managing multiple hazardous situations with search"""
    situations_updated = pyqtSignal(list)

    def __init__(self, parent=None, existing_situations=None):
        super().__init__(parent)
        self.setWindowTitle("Hazardous Situation Manager")
        self.setGeometry(200, 200, 700, 500)
        self.situations = existing_situations or []
        self.setupUI()
        self.update_display()

    def setupUI(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Manage Hazardous Situations")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)

        # Input section
        input_group = QGroupBox("Add New Hazardous Situation")
        input_layout = QVBoxLayout(input_group)

        self.situation_edit = QLineEdit()
        self.situation_edit.setPlaceholderText("Enter hazardous situation description...")
        self.situation_edit.textChanged.connect(self.update_suggestions)
        input_layout.addWidget(self.situation_edit)

        # Search suggestions
        self.suggestions_list = QListWidget()
        self.suggestions_list.setMaximumHeight(100)
        self.suggestions_list.itemDoubleClicked.connect(self.select_suggestion)
        input_layout.addWidget(self.suggestions_list)

        # Add button
        add_btn = QPushButton("Add Situation")
        add_btn.clicked.connect(self.add_situation)
        input_layout.addWidget(add_btn)

        layout.addWidget(input_group)

        # Current situations display
        current_group = QGroupBox("Current Hazardous Situations")
        current_layout = QVBoxLayout(current_group)

        self.situations_scroll = QScrollArea()
        self.situations_scroll.setWidgetResizable(True)
        self.situations_scroll.setMaximumHeight(200)

        self.situations_container = QWidget()
        self.situations_layout = QVBoxLayout(self.situations_container)
        self.situations_scroll.setWidget(self.situations_container)

        current_layout.addWidget(self.situations_scroll)
        layout.addWidget(current_group)

        # Dialog buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

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

    def add_situation(self):
        """Add a new hazardous situation"""
        situation_text = self.situation_edit.text().strip()
        if situation_text and situation_text not in self.situations:
            self.situations.append(situation_text)
            self.check_and_add_to_documents(situation_text)
            self.situation_edit.clear()
            self.update_display()
            self.situations_updated.emit(self.situations)

    def remove_situation(self, index):
        """Remove a hazardous situation"""
        if 0 <= index < len(self.situations):
            reply = QMessageBox.question(self, 'Remove Situation',
                                       f'Remove this hazardous situation?',
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.situations.pop(index)
                self.update_display()
                self.situations_updated.emit(self.situations)

    def update_display(self):
        """Update the display of current situations"""
        # Clear existing widgets
        for i in reversed(range(self.situations_layout.count())):
            child = self.situations_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Add situation widgets
        for i, situation in enumerate(self.situations):
            situation_widget = self.create_situation_widget(situation, i)
            self.situations_layout.addWidget(situation_widget)

    def create_situation_widget(self, situation_text, index):
        """Create a widget for a single situation"""
        container = QFrame()
        container.setFrameStyle(QFrame.Box)
        container.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
        """)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)

        # Situation number
        num_label = QLabel(f"{index + 1}.")
        num_label.setFont(QFont("Arial", 9, QFont.Bold))
        num_label.setMinimumWidth(20)
        layout.addWidget(num_label)

        # Situation text
        text_label = QLabel(situation_text)
        text_label.setWordWrap(True)
        layout.addWidget(text_label, 1)

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
        remove_btn.clicked.connect(lambda: self.remove_situation(index))
        layout.addWidget(remove_btn)

        return container

    def check_and_add_to_documents(self, situation_text):
        """Check if the situation is new and add it to the dynamic documents"""
        global hazardous_situation_documents
        if add_new_document(hazardous_situation_documents, situation_text, HAZARDOUS_FILE, "Hazardous Situation"):
            refresh_indices()

    def get_situations(self):
        """Get all situations as a list"""
        return self.situations.copy()

    def get_situations_text(self):
        """Get all situations as formatted text"""
        if not self.situations:
            return ""
        return " | ".join([f"{i+1}. {sit}" for i, sit in enumerate(self.situations)])
