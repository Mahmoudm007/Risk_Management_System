from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette
import json
from search import *
from PyQt5.QtWidgets import (QPushButton, QLabel, QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox,
                             QAbstractItemView, QMenu, QDialog, QHBoxLayout, QScrollArea, QTreeWidget, QTreeWidgetItem,
                             QCheckBox, QGroupBox, QMessageBox, QFileDialog, QLineEdit, QDialogButtonBox, QTableWidget, QTableWidgetItem, 
                             QFrame, QListWidget)

class SequenceEventWidget(QWidget):
    """Widget to manage a chain of sequential events"""

    sequence_updated = pyqtSignal(list)  # Signal emitted when sequence is updated

    def __init__(self, initial_event="", parent=None):
        super().__init__(parent)
        self.sequence_events = []
        if initial_event.strip():
            self.sequence_events.append(initial_event.strip())

        self.setupUI()
        self.update_display()

    def setupUI(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(3)

        # Scroll area for sequences
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(200)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.sequence_container = QWidget()
        self.sequence_layout = QVBoxLayout(self.sequence_container)
        self.sequence_layout.setContentsMargins(2, 2, 2, 2)
        self.sequence_layout.setSpacing(2)

        self.scroll_area.setWidget(self.sequence_container)
        self.main_layout.addWidget(self.scroll_area)

        # Add button
        self.add_button = QPushButton("+ Add Next Event")
        self.add_button.setMaximumHeight(25)
        self.add_button.clicked.connect(self.add_new_event)
        self.main_layout.addWidget(self.add_button)

    def update_display(self):
        """Update the visual display of the sequence"""
        # Clear existing widgets
        for i in reversed(range(self.sequence_layout.count())):
            child = self.sequence_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Add sequence events
        for i, event in enumerate(self.sequence_events):
            event_widget = self.create_event_widget(event, i)
            self.sequence_layout.addWidget(event_widget)

            # Add arrow between events (except for the last one)
            if i < len(self.sequence_events) - 1:
                arrow_widget = self.create_arrow_widget()
                self.sequence_layout.addWidget(arrow_widget)

        # Emit signal with updated sequence
        self.sequence_updated.emit(self.sequence_events)

    def create_event_widget(self, event_text, index):
        """Create a widget for a single event in the sequence"""
        container = QFrame()
        container.setFrameStyle(QFrame.Box)
        container.setStyleSheet("""
            QFrame {
                background-color: #e8f4f8;
                border: 1px solid #2c5aa0;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
        """)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)

        # Sequence number
        seq_label = QLabel(f"Event {index + 1}:")
        seq_label.setFont(QFont("Arial", 9, QFont.Bold))
        seq_label.setStyleSheet("color: #2c5aa0; background: transparent; border: none;")
        seq_label.setMinimumWidth(50)
        layout.addWidget(seq_label)

        # Event text
        event_label = QLabel(event_text)
        event_label.setWordWrap(True)
        event_label.setStyleSheet("background: transparent; border: none; padding: 2px;")
        layout.addWidget(event_label, 1)

        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setMaximumSize(40, 20)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_event(index))
        layout.addWidget(edit_btn)

        # Remove button (only show if more than one event)
        if len(self.sequence_events) > 1:
            remove_btn = QPushButton("×")
            remove_btn.setMaximumSize(20, 20)
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                    font-size: 20px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            remove_btn.clicked.connect(lambda: self.remove_event(index))
            layout.addWidget(remove_btn)

        return container

    def create_arrow_widget(self):
        """Create an arrow widget to show sequence flow"""
        arrow_label = QLabel("↓")
        arrow_label.setAlignment(Qt.AlignCenter)
        arrow_label.setStyleSheet("""
            color: #2c5aa0;
            font-size: 16px;
            font-weight: bold;
            background: transparent;
            margin: 2px;
        """)
        arrow_label.setMaximumHeight(20)
        return arrow_label

    def add_new_event(self):
        """Add a new event to the sequence"""
        dialog = SequenceEventDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_event = dialog.get_event_text()
            if new_event.strip():
                self.sequence_events.append(new_event.strip())
                # Add to dynamic documents if it's new
                self.check_and_add_to_documents(new_event.strip())
                self.update_display()

    def edit_event(self, index):
        """Edit an existing event"""
        if 0 <= index < len(self.sequence_events):
            dialog = SequenceEventDialog(self, self.sequence_events[index])
            if dialog.exec_() == QDialog.Accepted:
                new_event = dialog.get_event_text()
                if new_event.strip():
                    self.sequence_events[index] = new_event.strip()
                    # Add to dynamic documents if it's new
                    self.check_and_add_to_documents(new_event.strip())
                    self.update_display()

    def remove_event(self, index):
        """Remove an event from the sequence"""
        if 0 <= index < len(self.sequence_events) and len(self.sequence_events) > 1:
            reply = QMessageBox.question(self, 'Remove Event',
                                         f'Are you sure you want to remove Seq {index + 1}?',
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.sequence_events.pop(index)
                self.update_display()

    def check_and_add_to_documents(self, event_text):
        """Check if the event is new and add it to the dynamic documents"""
        global sequence_of_event_documents
        if add_new_document(sequence_of_event_documents, event_text, SEQUENCE_FILE, "Sequence of Event"):
            refresh_indices()

    def get_sequence_text(self):
        """Get the complete sequence as formatted text"""
        if not self.sequence_events:
            return ""

        formatted_sequence = []
        for i, event in enumerate(self.sequence_events):
            formatted_sequence.append(f"Seq {i + 1}: {event}")

        return " → ".join(formatted_sequence)

    def get_sequence_list(self):
        """Get the sequence as a list"""
        return self.sequence_events.copy()

    def set_sequence(self, events_list):
        """Set the sequence from a list of events"""
        if isinstance(events_list, list):
            self.sequence_events = [event.strip() for event in events_list if event.strip()]
            if not self.sequence_events:
                self.sequence_events = [""]
            self.update_display()


class SequenceEventDialog(QDialog):
    """Dialog for adding/editing sequence events with search functionality"""

    def __init__(self, parent=None, initial_text=""):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Sequence Event")
        self.setGeometry(200, 200, 600, 400)
        self.initial_text = initial_text
        self.setupUI()

        if initial_text:
            self.event_edit.setText(initial_text)

    def setupUI(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Enter Sequence Event:")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)

        # Event input
        self.event_edit = QLineEdit()
        self.event_edit.setPlaceholderText("Enter the sequence event description...")
        self.event_edit.textChanged.connect(self.update_suggestions)
        layout.addWidget(self.event_edit)

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
        search_terms = self.event_edit.text()

        if not search_terms.strip():
            self.suggestions_list.clear()
            return

        # Search in sequence documents
        results = search_documents(search_terms, sequence_of_event_inverted_index, sequence_of_event_documents)
        highlighted_results = rank_and_highlight(results, search_terms, sequence_of_event_documents, scores)

        self.suggestions_list.clear()
        if highlighted_results:
            for doc_id, content, score in highlighted_results[:10]:  # Limit to top 10 results
                # Clean up the content (remove highlighting for display)
                clean_content = content.replace(" *", " ").replace("* ", " ")
                self.suggestions_list.addItem(f"ID: {doc_id} - {clean_content}")

    def select_suggestion(self, item):
        """Select a suggestion and populate the text field"""
        text = item.text()
        # Extract the content after "ID: X - "
        if " - " in text:
            content = text.split(" - ", 1)[1]
            self.event_edit.setText(content)

    def get_event_text(self):
        """Get the entered event text"""
        return self.event_edit.text().strip()