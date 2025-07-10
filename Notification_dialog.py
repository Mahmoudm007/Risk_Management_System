from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import (QPushButton, QLabel, QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QAbstractItemView, QMenu, QDialog, QHBoxLayout, QTextEdit, QScrollArea)


class NotificationDialog(QDialog):
    """Dialog to display notifications of newly added sentences"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Additions Notifications")
        self.setGeometry(200, 200, 800, 600)
        self.setupUI()
        self.load_notifications()

    def setupUI(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Recently Added Sentences")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Scroll area for notifications
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Buttons
        button_layout = QHBoxLayout()

        clear_button = QPushButton("Clear All Notifications")
        clear_button.clicked.connect(self.clear_notifications)
        button_layout.addWidget(clear_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def load_notifications(self):
        """Load and display notifications"""
        notifications = load_notifications()

        if not notifications:
            no_notifications_label = QLabel("No new additions to display.")
            no_notifications_label.setStyleSheet("color: gray; font-style: italic; padding: 20px;")
            self.scroll_layout.addWidget(no_notifications_label)
            return

        # Sort notifications by timestamp (newest first)
        notifications.sort(key=lambda x: x['timestamp'], reverse=True)

        for notification in notifications:
            self.add_notification_widget(notification)

    def add_notification_widget(self, notification):
        """Add a single notification widget"""
        # Create container widget
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                margin: 5px;
                padding: 10px;
                background-color: #f9f9f9;
            }
        """)

        layout = QVBoxLayout(container)

        # Header with field type and timestamp
        header_layout = QHBoxLayout()

        field_label = QLabel(f"Field: {notification['field_type']}")
        field_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(field_label)

        header_layout.addStretch()

        timestamp_label = QLabel(notification['timestamp'])
        timestamp_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        header_layout.addWidget(timestamp_label)

        layout.addLayout(header_layout)

        # Content
        content_label = QLabel(notification['content'])
        content_label.setWordWrap(True)
        content_label.setStyleSheet("margin-top: 5px; padding: 5px; background-color: white; border-radius: 3px;")
        layout.addWidget(content_label)

        self.scroll_layout.addWidget(container)

    def clear_notifications(self):
        """Clear all notifications"""
        reply = QMessageBox.question(self, 'Clear Notifications',
                                     'Are you sure you want to clear all notifications?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            clear_notifications()
            # Clear the display
            for i in reversed(range(self.scroll_layout.count())):
                self.scroll_layout.itemAt(i).widget().setParent(None)

            # Show empty message
            no_notifications_label = QLabel("No new additions to display.")
            no_notifications_label.setStyleSheet("color: gray; font-style: italic; padding: 20px;")
            self.scroll_layout.addWidget(no_notifications_label)

