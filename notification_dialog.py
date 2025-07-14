from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from search import *
from PyQt5.QtWidgets import (QPushButton, QLabel, QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox,
                             QAbstractItemView, QMenu, QDialog, QHBoxLayout, QScrollArea, QTreeWidget, QTreeWidgetItem,
                             QCheckBox, QGroupBox, QMessageBox, QFileDialog)

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
        title_label = QLabel("Recently Added New Content")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #2c3e50;")
        layout.addWidget(title_label)

        # Info label
        info_label = QLabel("These are new additions that were not previously in the database:")
        info_label.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-bottom: 10px;")
        layout.addWidget(info_label)

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
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_button.clicked.connect(self.clear_notifications)
        button_layout.addWidget(clear_button)

        mark_read_button = QPushButton("Mark as Read")
        mark_read_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        mark_read_button.clicked.connect(self.mark_as_read)
        button_layout.addWidget(mark_read_button)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def load_notifications(self):
        """Load and display notifications"""
        notifications = load_notifications()

        if not notifications:
            no_notifications_label = QLabel("No new additions to display.")
            no_notifications_label.setStyleSheet("color: gray; font-style: italic; padding: 20px; text-align: center;")
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
        is_new = notification.get('is_new', True)

        if is_new:
            container.setStyleSheet("""
                QWidget {
                    border: 2px solid #e74c3c;
                    border-radius: 8px;
                    margin: 5px;
                    padding: 12px;
                    background-color: #fff5f5;
                }
            """)
        else:
            container.setStyleSheet("""
                QWidget {
                    border: 1px solid #bdc3c7;
                    border-radius: 8px;
                    margin: 5px;
                    padding: 12px;
                    background-color: #f8f9fa;
                }
            """)

        layout = QVBoxLayout(container)

        # Header with field type and timestamp
        header_layout = QHBoxLayout()

        # New badge
        if is_new:
            new_badge = QLabel("NEW")
            new_badge.setStyleSheet("""
                background-color: #e74c3c;
                color: white;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            """)
            new_badge.setMaximumWidth(40)
            header_layout.addWidget(new_badge)

        field_label = QLabel(f"Field: {notification['field_type']}")
        field_label.setStyleSheet("font-weight: bold; color: #2c3e50; background: transparent; border: none;")
        header_layout.addWidget(field_label)

        header_layout.addStretch()

        timestamp_label = QLabel(notification['timestamp'])
        timestamp_label.setStyleSheet("color: #7f8c8d; font-size: 11px; background: transparent; border: none;")
        header_layout.addWidget(timestamp_label)

        layout.addLayout(header_layout)

        # Content
        content_label = QLabel(notification['content'])
        content_label.setWordWrap(True)
        content_label.setStyleSheet("""
            margin-top: 8px; 
            padding: 8px; 
            background-color: white; 
            border-radius: 4px;
            border: 1px solid #ecf0f1;
        """)
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
            no_notifications_label.setStyleSheet("color: gray; font-style: italic; padding: 20px; text-align: center;")
            self.scroll_layout.addWidget(no_notifications_label)

            # Update parent's notification count
            if hasattr(self.parent(), 'update_notification_count'):
                self.parent().update_notification_count()

    def mark_as_read(self):
        """Mark all notifications as read"""
        reply = QMessageBox.question(self, 'Mark as Read',
                                     'Mark all notifications as read?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            mark_notifications_as_read()
            # Update parent's notification count
            if hasattr(self.parent(), 'update_notification_count'):
                self.parent().update_notification_count()
            # Reload the display
            for i in reversed(range(self.scroll_layout.count())):
                self.scroll_layout.itemAt(i).widget().setParent(None)
            self.load_notifications()
