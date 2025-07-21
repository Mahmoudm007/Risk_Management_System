from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette
import json
from search import *
from hazardous_situation_dialog import HazardousSituationDialog
from PyQt5.QtWidgets import (QPushButton, QLabel, QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox,
                             QAbstractItemView, QMenu, QDialog, QHBoxLayout, QScrollArea, QTreeWidget, QTreeWidgetItem,
                             QCheckBox, QGroupBox, QMessageBox, QTableWidgetItem, QTableWidget, QLineEdit, QSpinBox, QAction, QFileDialog)

class HazardousSituationCardWidget(QWidget):
    """Widget to display hazardous situations as cards in table cells"""
    situations_updated = pyqtSignal(list)

    def __init__(self, initial_situations=None, parent=None):
        super().__init__(parent)
        self.situations = initial_situations or []
        self.parent_window = parent
        self.setupUI()
        self.update_display()

    def setupUI(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(3, 3, 3, 3)
        self.main_layout.setSpacing(2)

        # Scroll area for situations
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

        self.situations_container = QWidget()
        self.situations_layout = QVBoxLayout(self.situations_container)
        self.situations_layout.setContentsMargins(2, 2, 2, 2)
        self.situations_layout.setSpacing(2)

        self.scroll_area.setWidget(self.situations_container)
        self.main_layout.addWidget(self.scroll_area)

        # Add/Edit button
        self.manage_button = QPushButton("⚙ Manage")
        self.manage_button.setMaximumHeight(22)
        self.manage_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 9px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.manage_button.clicked.connect(self.open_management_dialog)
        self.main_layout.addWidget(self.manage_button)

    def update_display(self):
        """Update the visual display of situations"""
        # Clear existing widgets
        for i in reversed(range(self.situations_layout.count())):
            child = self.situations_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Add situation cards
        for i, situation in enumerate(self.situations):
            situation_card = self.create_situation_card(situation, i)
            self.situations_layout.addWidget(situation_card)

        # Update button text
        count = len(self.situations)
        if count == 0:
            self.manage_button.setText("+ Add Situations")
        else:
            self.manage_button.setText(f"⚙ Manage ({count})")

        # Emit signal with updated situations
        self.situations_updated.emit(self.situations)

    def create_situation_card(self, situation_text, index):
        """Create a card widget for a single hazardous situation"""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 4px;
                padding: 3px;
                margin: 1px;
            }
        """)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(4, 3, 4, 3)

        # Situation number
        num_label = QLabel(f"S{index + 1}:")
        num_label.setFont(QFont("Arial", 8, QFont.Bold))
        num_label.setStyleSheet("color: #856404; background: transparent; border: none;")
        num_label.setMinimumWidth(20)
        layout.addWidget(num_label)

        # Situation text (truncated if too long)
        display_text = situation_text
        if len(display_text) > 50:
            display_text = display_text[:47] + "..."
        
        text_label = QLabel(display_text)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("""
            background: white; 
            border: none; 
            padding: 1px;
            font-size: 15px;
        """)
        text_label.setToolTip(situation_text)  # Show full text on hover
        layout.addWidget(text_label, 1)
        return card

    def open_management_dialog(self):
        """Open the management dialog for situations"""
        dialog = HazardousSituationDialog(self.parent_window, self.situations.copy())
        if dialog.exec_() == QDialog.Accepted:
            self.situations = dialog.get_situations()
            self.update_display()
            
            # Add new situations to documents
            for situation in self.situations:
                self.check_and_add_to_documents(situation)

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
            self.update_display()

    def get_situations_text(self):
        """Get all situations as formatted text"""
        if not self.situations:
            return ""
        return " | ".join([f"{i+1}. {sit}" for i, sit in enumerate(self.situations)])
