# General imports
import os
import sys
import json
import random
import pandas as pd
from datetime import datetime
from collections import Counter

# PyQt5 imports
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QDateTime, QPropertyAnimation, QEasingCurve, QUrl, QTimer
from PyQt5.QtWidgets import (QPushButton, QLabel, QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox,
                             QAbstractItemView, QMenu, QDialog, QHBoxLayout, QScrollArea, QTreeWidget, QTreeWidgetItem,
                             QCheckBox, QGroupBox, QMessageBox, QTableWidgetItem, QTableWidget, QLineEdit, QSpinBox, QAction, QFileDialog)

# Reporting imports
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer

# Canvas imports
import plotly.graph_objects as go
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

# Project Modular Classes
from search import *
from RiskChat import ChatDialog
from Dashboard import Dashboard
from Calendar import CalendarDialog
from filter_dialog import FilterDialog
from pdf_dialog import EnhancedPDFDialog
from DeviceSelection import DeviceSelected
from database_manager import DatabaseManager
from user_input_dialog import UserInputDialog
from sequence_widget import SequenceEventWidget
from ControlAndRequirement import AddControlClass
from risk_history_dialog import RiskHistoryDialog
from notification_dialog import NotificationDialog
from traceability_dialog import TraceabilityDialog
from Gemini_app import ChatDialog as GeminiChatDialog
from enhanced_matrix_dialog import EnhancedMatrixDialog
from component_selection_dialog import ComponentSelectionDialog


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
MainUI, _ = loadUiType('UI/mainWindowui.ui')

# Enhanced device components with categories
DEVICE_COMPONENTS = {
    "EzVent 101": {
        "Mechanical": ["Screws", "Stands", "Casing", "Valves", "Tubing", "Pressure Relief Valve"],
        "Electrical": ["Batteries", "Circuit Boards", "Sensors", "Wires", "Display Unit", "Power Supply"],
        "Software": ["Firmware", "User Interface Software", "Control Algorithms", "Safety Monitoring"],
        "Consumables": ["Filters", "Masks", "Hoses", "Breathing Circuits"],
        "Others": ["Labels", "Documentation", "Packaging", "Accessories"]
    },
    "EzVent 201": {
        "Mechanical": ["Screws", "Stands", "Casing", "Valves", "Tubing", "Flow Sensors"],
        "Electrical": ["Batteries", "Circuit Boards", "Sensors", "Wires", "Display Unit", "AC Power Cord"],
        "Software": ["Firmware", "User Interface Software", "Control Algorithms", "Data Logging"],
        "Consumables": ["Filters", "Masks", "Hoses", "Breathing Circuits"],
        "Others": ["Labels", "Documentation", "Packaging", "Calibration Tools"]
    },
    "EzVent 202": {
        "Mechanical": ["AC Power Inlet", "Check Valve", "Fittings", "Gas Manifold", "Pressure Regulators"],
        "Electrical": ["AC-DC Power Supply", "Charging controller IC", "Control Boards", "Sensors"],
        "Software": ["Advanced Control Software", "Network Interface", "Remote Monitoring"],
        "Consumables": ["Filters", "Tubing", "Connectors"],
        "Others": ["Mounting Hardware", "Service Tools", "User Manuals"]
    },
    "SleepEZ": {
        "Mechanical": ["Housing", "Motor Assembly", "Pressure Sensors", "Valves"],
        "Electrical": ["Power Supply", "Control Electronics", "Display", "Connectivity Module"],
        "Software": ["Sleep Monitoring Software", "Data Analysis", "Mobile App Interface"],
        "Consumables": ["Masks", "Tubing", "Filters", "Headgear"],
        "Others": ["Carrying Case", "SD Card", "User Guide"]
    },
    "Syringe pump": {
        "Mechanical": ["Syringe Holder", "Plunger Drive", "Motor Assembly", "Chassis"],
        "Electrical": ["Control Board", "Display", "Alarm System", "Power Supply"],
        "Software": ["Infusion Control Software", "Safety Algorithms", "User Interface"],
        "Consumables": ["Syringes", "IV Tubing", "Connectors"],
        "Others": ["Mounting Bracket", "Battery Pack", "Service Kit"]
    },
    "Oxygen concentrator": {
        "Mechanical": ["Compressor", "Molecular Sieve", "Cooling Fan", "Pressure Vessels"],
        "Electrical": ["Control Electronics", "Oxygen Sensor", "Flow Meter", "Power Supply"],
        "Software": ["Concentration Control", "Flow Management", "Alarm System"],
        "Consumables": ["Filters", "Tubing", "Cannulas"],
        "Others": ["Wheels", "Handle", "Maintenance Kit", "User Manual"]
    }
}


class RiskSystem(QMainWindow, MainUI):
    def __init__(self):
        super(RiskSystem, self).__init__()
        self.setupUi(self)
        self.setGeometry(0, 0, 1900, 950)
        self.setWindowTitle("Risk Management System")
        self.setWindowIcon(QIcon("UI/icons/ezz.png"))
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Initialize risk history storage
        self.risk_history = {}  # Store history for each row
        self.history_file = 'Database/risk_history.json'
        self.load_risk_history()
        
        # Store original table data for filtering
        self.original_table_data = []
        self.current_user_name = None  # Store current user name for the session
        
        # Flags for initial creation mode
        self.is_initial_creation = False
        self.current_session_user = None
        
        # Load counters from database
        self.sw_counter, self.elc_counter, self.mec_counter, self.us_counter, self.test_counter = self.db_manager.load_counters()
        
        self.table_widget.setFixedHeight(400)

        self.table_widget.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        
        # TODO: Fix the issues that appears in the program starting if there is a database saved, because its handled as itemChanged in the table_widget
        self.table_widget.itemChanged.connect(self.handle_item_changed) # Ask for the name multiple times if there are a data saved in the database

        self.component_btn.setEnabled(False)
        self.selected_device = None
        self.selected_components = []

        # Load chat data from database
        self.chat_data = self.db_manager.load_chat_data()
        self.chat_widgets = {}
        
        self.chat_dialog = None
        self.chat_history = ""

        self.checked_items = []

        self.first_axis = QComboBox()
        self.second_axis = QComboBox()
        self.webEngineView = QWebEngineView()

        self.seq_list_widget = QtWidgets.QListWidget()
        self.sit_list_widget = QtWidgets.QListWidget()
        self.harm_list_widget = QtWidgets.QListWidget()

        # Initialize notification system
        self.notification_counter_label = None
        self.setup_notification_counter()

        # Initialize auto-hide timers for search layouts
        self.seq_hide_timer = QTimer()
        self.seq_hide_timer.setSingleShot(True)
        self.seq_hide_timer.timeout.connect(lambda: self.hide_search_widget(self.seq_list_widget))

        self.sit_hide_timer = QTimer()
        self.sit_hide_timer.setSingleShot(True)
        self.sit_hide_timer.timeout.connect(lambda: self.hide_search_widget(self.sit_list_widget))

        self.harm_hide_timer = QTimer()
        self.harm_hide_timer.setSingleShot(True)
        self.harm_hide_timer.timeout.connect(lambda: self.hide_search_widget(self.harm_list_widget))
        

        self.init_search_lists()
        self.init_combos()
        self.buttons_signals()
        self.web_application()
        self.table_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # Initialize counters
        self.num_risks = 0
        self.num_approved_risks = 0
        self.num_unapproved_risks = 0
        self.num_rejected_risks = 0

        self.matrix_file = 'Risk Matrix/matrix_state.json'

        # Timer to update notification count periodically
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.update_notification_count)
        self.notification_timer.start(5000)

        # Auto-save timer (save every 5 minutes)
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_data)
        self.auto_save_timer.start(300000)  # 5 minutes

        # Load existing data from database
        self.load_data_from_database()

        # Initial notification count update
        self.update_notification_count()

        # Show database stats on startup
        self.show_database_stats()

    def show_database_stats(self):
        """Show database statistics on startup"""
        stats = self.db_manager.get_database_stats()
        if stats['total_risks'] > 0:
            print(f"📊 Database loaded: {stats['total_risks']} risks")
            print(f"📁 Database size: {stats['database_size']} bytes")
            if stats['last_modified']:
                print(f"🕒 Last modified: {stats['last_modified']}")

    def load_data_from_database(self):
        """Load all data from database on startup"""
        try:
            # Load risks
            if self.db_manager.load_all_risks(self.table_widget):
                self.num_risks = self.table_widget.rowCount()
                print(f"✅ Loaded {self.num_risks} risks from database")
                
                # Update counters based on loaded data
                self.update_counters_from_table()
            else:
                print("📝 No existing risks found, starting fresh")
                
        except Exception as e:
            print(f"❌ Error loading data from database: {e}")
            QMessageBox.warning(self, "Database Error", 
                              f"Error loading data from database:\n{e}\n\nStarting with empty database.")

    def update_counters_from_table(self):
        """Update risk counters based on loaded table data"""
        dept_counts = {'Software Department': 0, 'Electrical Department': 0, 
                      'Mechanical Department': 0, 'Usability Team': 0, 'Testing Team': 0}
        
        for row in range(self.table_widget.rowCount()):
            dept_item = self.table_widget.item(row, 2)
            if dept_item:
                dept = dept_item.text()
                if dept in dept_counts:
                    dept_counts[dept] += 1
        
        # Update counters to be at least as high as existing risks
        self.sw_counter = max(self.sw_counter, dept_counts['Software Department'])
        self.elc_counter = max(self.elc_counter, dept_counts['Electrical Department'])
        self.mec_counter = max(self.mec_counter, dept_counts['Mechanical Department'])
        self.us_counter = max(self.us_counter, dept_counts['Usability Team'])
        self.test_counter = max(self.test_counter, dept_counts['Testing Team'])

    def auto_save_data(self):
        """Auto-save data every 5 minutes"""
        try:
            self.save_data_to_database()
            print("💾 Auto-save completed")
        except Exception as e:
            print(f"❌ Auto-save failed: {e}")

    def save_data_to_database(self):
        """Save all current data to database"""
        try:
            # Save risks
            self.db_manager.save_all_risks(self.table_widget)
            
            # Save chat data
            self.db_manager.save_chat_data(self.chat_data)
            
            # Save counters
            self.db_manager.save_counters(
                self.sw_counter, self.elc_counter, self.mec_counter, 
                self.us_counter, self.test_counter
            )
            
            # Save risk history
            self.save_risk_history()
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving data to database: {e}")
            return False

    def closeEvent(self, event):
        """Handle application close event"""
        # Ask user if they want to save before closing
        reply = QMessageBox.question(self, 'Save Before Exit', 
                                   'Do you want to save your work before exiting?',
                                   QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                   QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:
            if self.save_data_to_database():
                QMessageBox.information(self, "Saved", "All data has been saved successfully!")
                event.accept()
            else:
                QMessageBox.critical(self, "Save Error", "Failed to save data!")
                event.ignore()
        elif reply == QMessageBox.No:
            event.accept()
        else:  # Cancel
            event.ignore()

    def load_risk_history(self):
        """Load risk history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.risk_history = json.load(f)
        except Exception as e:
            print(f"Error loading risk history: {e}")
            self.risk_history = {}

    def save_risk_history(self):
        """Save risk history to file"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w') as f:
                json.dump(self.risk_history, f, indent=2)
        except Exception as e:
            print(f"Error saving risk history: {e}")

    def get_user_name_for_edit(self):
        """Get user name for edit tracking"""
        dialog = UserInputDialog(self, "Edit Confirmation", "Please enter your name to confirm this edit:")
        if dialog.exec_() == QDialog.Accepted:
            return dialog.user_name
        return None

    def get_user_name_for_new_risk(self):
        """Get user name for new risk entry"""
        dialog = UserInputDialog(self, "New Risk Entry", "Please enter your name to confirm adding this risk:")
        if dialog.exec_() == QDialog.Accepted:
            return dialog.user_name
        return None

    def record_initial_risk_creation(self, risk_id, user_name, field_data):
        """Record all initial field values for a new risk with the same user name"""
        if risk_id not in self.risk_history:
            self.risk_history[risk_id] = []

        # Record creation entry
        creation_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user': user_name,
            'field': 'Risk Created',
            'previous_value': '',
            'new_value': 'New risk entry created'
        }
        self.risk_history[risk_id].append(creation_entry)

        # Record all initial field values with the same user name
        field_names = [
            "Date", "Risk No.", "Department", "Device Affected", "Components", "Lifecycle", 
            "Hazard Category", "Hazard Source", "Hazardous Situation", "Sequence of Events", 
            "Harm Influenced", "Harm Description", "Severity", "Probability", "RPN"
        ]

        for i, field_name in enumerate(field_names):
            if i < len(field_data) and field_data[i]:
                field_entry = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'user': user_name,
                    'field': field_name,
                    'previous_value': '',
                    'new_value': str(field_data[i])
                }
                self.risk_history[risk_id].append(field_entry)

    def record_edit_history(self, row, column, previous_value, new_value, user_name):
        """Record edit history for a cell"""
        risk_id = self.get_risk_id_for_row(row)
        if not risk_id:
            return

        if risk_id not in self.risk_history:
            self.risk_history[risk_id] = []

        # Get field name from column header
        field_name = self.table_widget.horizontalHeaderItem(column).text()

        history_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user': user_name,
            'field': field_name,
            'previous_value': previous_value,
            'new_value': new_value
        }

        self.risk_history[risk_id].append(history_entry)
        self.save_risk_history()

    def get_risk_id_for_row(self, row):
        """Get risk ID for a given row"""
        risk_no_item = self.table_widget.item(row, 1)  # Risk No. is in column 1
        if risk_no_item:
            return risk_no_item.text()
        return None

    def show_risk_history(self, row):
        """Show history dialog for a specific risk"""
        risk_id = self.get_risk_id_for_row(row)
        if not risk_id:
            QMessageBox.information(self, "No History", "No risk ID found for this row.")
            return

        history_data = self.risk_history.get(risk_id, [])
        dialog = RiskHistoryDialog(risk_id, history_data, self)
        dialog.exec_()

    def apply_single_filter(self, filter_type, filter_value):
        """Apply single filter to the table"""
        # Hide all rows first
        for row in range(self.table_widget.rowCount()):
            self.table_widget.setRowHidden(row, True)

        # Show rows that match the filter criteria
        for row in range(self.table_widget.rowCount()):
            show_row = False

            if filter_type == "Device":
                device_item = self.table_widget.item(row, 3)  # Device Affected column
                if device_item and filter_value in device_item.text():
                    show_row = True

            elif filter_type == "Risk Level":
                risk_item = self.table_widget.item(row, 14)  # RPN column
                if risk_item and risk_item.text() == filter_value:
                    show_row = True

            elif filter_type == "Approval Status":
                approval_item = self.table_widget.item(row, 16)  # Approved By column
                approval_status = "Pending"  # Default status
                if approval_item and approval_item.text().strip():
                    if "rejected" in approval_item.text().lower():
                        approval_status = "Rejected"
                    else:
                        approval_status = "Approved"
                
                if approval_status == filter_value:
                    show_row = True

            elif filter_type == "Department":
                dept_item = self.table_widget.item(row, 2)  # Department column
                if dept_item and dept_item.text() == filter_value:
                    show_row = True

            # Show/hide the row based on filter results
            self.table_widget.setRowHidden(row, not show_row)

    def clear_table_filters(self):
        """Clear all table filters and show all rows"""
        for row in range(self.table_widget.rowCount()):
            self.table_widget.setRowHidden(row, False)

    def open_filter_dialog(self):
        """Open the filter dialog"""
        dialog = FilterDialog(self)
        dialog.exec_()

    def open_traceability_dialog(self):
        """Open the traceability dialog"""
        dialog = TraceabilityDialog(self)
        dialog.exec_()

    def open_component_selection_dialog(self):
        if not self.selected_device:
            QMessageBox.warning(self, "No Device Selected", "Please select a device first.")
            return
        dialog = ComponentSelectionDialog(self.selected_device, self)
        if dialog.exec_() == QDialog.Accepted:
            self.selected_components = dialog.checked_items

    def setup_notification_counter(self):
        """Setup the notification counter badge for existing notification_btn"""
        try:
            if hasattr(self, 'notification_btn') and self.notification_btn is not None:
                # Get the parent widget of the notification button
                parent_widget = self.notification_btn.parent()

                if parent_widget:
                    # Create notification counter label
                    self.notification_counter_label = QLabel("0")
                    self.notification_counter_label.setFixedSize(20, 20)
                    self.notification_counter_label.setStyleSheet("""
                                            QLabel {
                                                background-color: #e74c3c;
                                                color: white;
                                                border-radius: 7px;
                                                font-size: 10px;
                                                font-weight: bold;
                                                text-align: center;
                                            }
                                        """)
                    self.notification_counter_label.setAlignment(QtCore.Qt.AlignCenter)
                    self.notification_counter_label.hide()

                    # Position the counter relative to the notification button
                    self.notification_counter_label.setParent(parent_widget)

                    # Position the counter above and to the right of the button
                    def position_counter():
                        if self.notification_btn and self.notification_counter_label:
                            btn_pos = self.notification_btn.pos()
                            btn_size = self.notification_btn.size()
                            counter_x = btn_pos.x() + btn_size.width() - 15
                            counter_y = btn_pos.y() - 5
                            self.notification_counter_label.move(counter_x, counter_y)

                    # Position initially and whenever the button moves
                    position_counter()
                    self.notification_btn.installEventFilter(self)

        except Exception as e:
            print(f"Error setting up notification counter: {e}")

    def eventFilter(self, obj, event):
        """Event filter to reposition notification counter when button moves"""
        if obj == self.notification_btn and hasattr(self, 'notification_counter_label'):
            if event.type() == QtCore.QEvent.Move or event.type() == QtCore.QEvent.Resize:
                if self.notification_counter_label:
                    btn_pos = self.notification_btn.pos()
                    btn_size = self.notification_btn.size()
                    counter_x = btn_pos.x() + btn_size.width() - 15
                    counter_y = btn_pos.y() - 5
                    self.notification_counter_label.move(counter_x, counter_y)
        return super().eventFilter(obj, event)

    def update_notification_count(self):
        """Update the notification counter display"""
        try:
            count = get_notification_count()
            if self.notification_counter_label:
                if count > 0:
                    self.notification_counter_label.setText(str(count))
                    self.notification_counter_label.show()
                    self.notification_counter_label.raise_()
                else:
                    self.notification_counter_label.hide()
        except Exception as e:
            print(f"Error updating notification count: {e}")

    def hide_search_widget(self, widget):
        """Hide search widget after timeout"""
        if widget.isVisible():
            widget.hide()

    def start_hide_timer(self, timer, widget):
        """Start or restart the hide timer for a search widget"""
        timer.stop()
        if widget.isVisible() and widget.count() > 0:
            timer.start(5000)

    def buttons_signals(self):
        self.open_chat_button.clicked.connect(self.open_chat)
        self.hazardous_situation_edit.textChanged.connect(self.update_sit_ver_layout)
        self.sit_list_widget.itemDoubleClicked.connect(self.add_to_hazardous_situation_edit)
        self.sit_list_widget.itemClicked.connect(lambda: self.sit_hide_timer.stop())

        self.sequence_of_event_edit.textChanged.connect(self.update_seq_ver_layout)
        self.seq_list_widget.itemDoubleClicked.connect(self.add_to_sequence_of_event_edit)
        self.seq_list_widget.itemClicked.connect(lambda: self.seq_hide_timer.stop())

        self.harm_desc_line.textChanged.connect(self.update_harm_vec_layout)
        self.harm_list_widget.itemDoubleClicked.connect(self.add_to_harm_desc_line)
        self.harm_list_widget.itemClicked.connect(lambda: self.harm_hide_timer.stop())

        self.hazard_category_combo.currentIndexChanged.connect(self.update_hazard_sources)

        self.add_button.clicked.connect(self.add_entry)
        self.add_button.clicked.connect(lambda: self.generate_risk_number(flag="add"))
        self.add_button.clicked.connect(self.set_risk_number)
        self.department_combo.currentIndexChanged.connect(self.set_risk_number)

        self.severity_spinbox.valueChanged.connect(self.update_severity_label)
        self.severity_spinbox.valueChanged.connect(self.update_rpn_value)

        self.probability_spinbox.valueChanged.connect(self.update_probability_label)
        self.probability_spinbox.valueChanged.connect(self.update_rpn_value)

        self.dectability_spin_box.valueChanged.connect(self.update_dectability_label)
        self.show_charts_button.clicked.connect(self.show_charts)
        self.pdf_gen.clicked.connect(self.open_enhanced_pdf_dialog)

        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.source_combo.currentIndexChanged.connect(self.check_standards)
        self.add_source.clicked.connect(self.add_reference)

        self.sun_charts.clicked.connect(self.open_relation_chart)
        self.show_matrix.clicked.connect(self.show_rpn_matrix)

        self.modeSideBar.toggled.connect(self.toggle_side_bar)

        self.table_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table_widget.itemDoubleClicked.connect(self.open_chat_dialog)

        self.dashboardbtn.clicked.connect(self.open_dashboard)

        self.calendar.clicked.connect(self.open_calendar_dialog)
        self.accept_meeting.clicked.connect(self.toggle_meeting_frame)

        self.add_devices_affected.clicked.connect(self.select_devices_widget)
        self.component_btn.clicked.connect(self.open_component_selection_dialog)
        self.notification_btn.clicked.connect(self.show_notifications)
        
        # Add traceability button signal
        self.trace_btn.clicked.connect(self.open_traceability_dialog)

    def open_chat(self):
        if self.chat_dialog and self.chat_dialog.isVisible():
            self.chat_dialog.raise_()
            self.chat_dialog.activateWindow()
            return

        if self.chat_history:
            choice = QMessageBox.question(self, "Continue Chat", "Continue previous conversation?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if choice == QMessageBox.No:
                self.chat_history = ""

        self.chat_dialog = GeminiChatDialog(existing_history=self.chat_history, parent=self)
        self.chat_dialog.finished.connect(self.save_chat_history)
        self.chat_dialog.show()

    def save_chat_history(self):
        if self.chat_dialog:
            self.chat_history = self.chat_dialog.get_history()
            
    def show_notifications(self):
        """Show the notifications dialog"""
        dialog = NotificationDialog(self)
        dialog.exec_()
        self.update_notification_count()

    def select_devices_widget(self):
        dialog = DeviceSelected(self)
        if dialog.exec_() == QDialog.Accepted:
            self.checked_items = dialog.checked_items
            if self.checked_items:
                self.selected_device = self.checked_items[0]
                self.component_btn.setEnabled(True)
            else:
                self.selected_device = None
                self.component_btn.setEnabled(False)

    def open_calendar_dialog(self):
        self.calendar_dialog = CalendarDialog(self)
        self.toggle_meeting_label()
        self.calendar_dialog.exec_()

    def set_date_time_label(self, date_str, time_str):
        self.date_time_label.setText(
            f"A Meeting will be held to discuss the risk analysis within : {date_str} {time_str}")

    def update_counts(self):
        self.num_unapproved_risks = abs(self.num_risks - self.num_approved_risks - self.num_rejected_risks)

    def open_dashboard(self):
        self.update_counts()
        self.dashboard = Dashboard(self.num_risks, self.num_approved_risks, self.num_unapproved_risks,
                                   self.num_rejected_risks, self)
        self.dashboard.exec_()

    def open_chat_dialog(self, item):
        row_id = item.row()
        print(f"Opening chat dialog for row: {row_id}")

        chat_dialog = ChatDialog(row_id, self.chat_data, self)
        chat_dialog.setGeometry(100, 100, 400, 300)
        chat_dialog.exec_()
        
        # Save chat data after dialog closes
        self.db_manager.save_chat_data(self.chat_data)
        print(f"Chat dialog should be visible now.")

    def add_entry(self):
        # Get user name ONCE at the very beginning for the entire risk entry
        user_name = self.get_user_name_for_new_risk()
        if not user_name:
            return  # User cancelled, don't add the entry

        # Set flag to indicate we're in initial creation mode
        self.is_initial_creation = True
        self.current_session_user = user_name

        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        # Collect all field data for history recording
        field_data = []

        current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.table_widget.setItem(row_position, 0, QTableWidgetItem(current_datetime))
        field_data.append(current_datetime)

        rsk_no = self.risk_no_line_edit.text()
        self.table_widget.setItem(row_position, 1, QTableWidgetItem(rsk_no))
        field_data.append(rsk_no)

        department = self.department_combo.currentText()
        self.table_widget.setItem(row_position, 2, QTableWidgetItem(department))
        field_data.append(department)

        devices_text = ', '.join(self.checked_items)
        self.table_widget.setItem(row_position, 3, QTableWidgetItem(devices_text))
        field_data.append(devices_text)

        components_text = ", ".join(self.selected_components)
        self.table_widget.setItem(row_position, 4, QTableWidgetItem(components_text))
        field_data.append(components_text)

        lifecycle = self.lifecycle_combo.currentText()
        self.table_widget.setItem(row_position, 5, QTableWidgetItem(lifecycle))
        field_data.append(lifecycle)

        hazard_category = self.hazard_category_combo.currentText()
        self.table_widget.setItem(row_position, 6, QTableWidgetItem(hazard_category))
        field_data.append(hazard_category)

        hazard_source = self.hazard_source_combo.currentText()
        self.table_widget.setItem(row_position, 7, QTableWidgetItem(hazard_source))
        field_data.append(hazard_source)

        hazardous_situation = self.hazardous_situation_edit.text()
        self.table_widget.setItem(row_position, 8, QTableWidgetItem(hazardous_situation))
        field_data.append(hazardous_situation)

        if hazardous_situation.strip():
            self.check_and_add_new_content(hazardous_situation, "Hazardous Situation")

        sequence_of_event = self.sequence_of_event_edit.text()

        sequence_widget = SequenceEventWidget(sequence_of_event)
        sequence_widget.sequence_updated.connect(lambda events: self.update_sequence_in_table(row_position, events))

        self.table_widget.setCellWidget(row_position, 9, sequence_widget)
        field_data.append(sequence_of_event)

        if sequence_of_event.strip():
            self.check_and_add_new_content(sequence_of_event, "Sequence of Event")

        harm_influenced = self.harm_influenced_combo.currentText()
        self.table_widget.setItem(row_position, 10, QTableWidgetItem(harm_influenced))
        field_data.append(harm_influenced)

        harm_desc = self.harm_desc_line.text()
        self.table_widget.setItem(row_position, 11, QTableWidgetItem(harm_desc))
        field_data.append(harm_desc)

        if harm_desc.strip():
            self.check_and_add_new_content(harm_desc, "Harm Description")

        severity = self.severity_spinbox.value()
        self.table_widget.setItem(row_position, 12, QTableWidgetItem(str(severity)))
        field_data.append(str(severity))

        probability = self.probability_spinbox.value()
        self.table_widget.setItem(row_position, 13, QTableWidgetItem(str(probability)))
        field_data.append(str(probability))

        RPN = self.update_rpn_value()
        self.table_widget.setItem(row_position, 14, QTableWidgetItem(RPN))
        field_data.append(RPN)

        tree_widget_cell = AddControlClass()
        self.table_widget.setCellWidget(row_position, 15, tree_widget_cell)

        self.table_widget.setRowHeight(row_position, 180)

        # Record all initial field values with the same user name (NO additional prompts)
        self.record_initial_risk_creation(rsk_no, user_name, field_data)

        self.num_risks += 1
        
        self.highlight_missing_cells(row_position)
        
        self.generate_and_set_id()
        self.update_rsk_number_combo()
        self.update_notification_count()
        
        # Save the history after adding the entry
        self.save_risk_history()

        # Auto-save to database after adding new risk
        self.save_data_to_database()

        # Clear the session flags
        self.is_initial_creation = False
        self.current_session_user = None

    def highlight_missing_cells(self, row):
        for col in range(self.table_widget.columnCount()):
            item = self.table_widget.item(row, col)
            if (item is None or not item.text().strip()) and self.table_widget.cellWidget(row, col) is None:
                if item is None:
                    item = QTableWidgetItem("")
                    self.table_widget.setItem(row, col, item)
                item.setBackground(QColor('yellow'))

    def handle_item_changed(self, item):
        row = item.row()
        column = item.column()
        
        # Get field name from column header
        field_name = self.table_widget.horizontalHeaderItem(column).text()
        
        # Special handling for "Approved By" column - don't ask for user name
        if field_name == "Approved By":
            previous_value = getattr(item, '_previous_value', '')
            new_value = item.text().strip()
            
            # Record without asking for user name
            risk_id = self.get_risk_id_for_row(row)
            if risk_id:
                history_entry = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'user': 'System',  # Use 'System' for approval changes
                    'field': field_name,
                    'previous_value': previous_value,
                    'new_value': new_value
                }
                
                if risk_id not in self.risk_history:
                    self.risk_history[risk_id] = []
                self.risk_history[risk_id].append(history_entry)
                self.save_risk_history()
            
            # Handle highlighting
            if new_value:
                item.setBackground(QColor('white'))
            else:
                item.setBackground(QColor('yellow'))
            return

        # For all other fields during editing (not initial creation)
        if not getattr(self, 'is_initial_creation', False):
            # Get user name before processing the edit

            # user_name = self.get_user_name_for_edit()
            
            #TODO: Hardcoded user name for testing purposes, until fixing the itemChanged issue in table_widget, when a database is saved
            user_name = "Eng. Mahmoud"  # For testing purposes, use a fixed name   
            if not user_name:
                # If user cancels, revert the change
                item.setText(getattr(item, '_previous_value', ''))
                return

            # Get previous value if stored
            previous_value = getattr(item, '_previous_value', '')
            new_value = item.text().strip()

            # Record the edit in history
            self.record_edit_history(row, column, previous_value, new_value, user_name)

        # Handle highlighting
        new_value = item.text().strip()
        if new_value:
            item.setBackground(QColor('white'))
        else:
            item.setBackground(QColor('yellow'))

        # Auto-save after edit
        self.save_data_to_database()

    def update_sequence_in_table(self, row, events_list):
        """Update the sequence text in the table when the sequence widget is updated"""
        if events_list:
            formatted_sequence = []
            for i, event in enumerate(events_list):
                formatted_sequence.append(f"Seq {i + 1}: {event}")
            sequence_text = " → ".join(formatted_sequence)

            item = self.table_widget.item(row, 9)
            if item:
                item.setText(sequence_text)
            else:
                self.table_widget.setItem(row, 9, QTableWidgetItem(sequence_text))

        # Auto-save after sequence update
        self.save_data_to_database()

    def check_and_add_new_content(self, content, field_type):
        """Check if content is new and add it to the appropriate dynamic list"""
        global sequence_of_event_documents, hazardous_situation_documents, harm_description_documents

        if field_type == "Sequence of Event":
            if add_new_document(sequence_of_event_documents, content, SEQUENCE_FILE, field_type):
                refresh_indices()
                print(f"Added new sequence of event: {content}")
        elif field_type == "Hazardous Situation":
            if add_new_document(hazardous_situation_documents, content, HAZARDOUS_FILE, field_type):
                refresh_indices()
                print(f"Added new hazardous situation: {content}")
        elif field_type == "Harm Description":
            if add_new_document(harm_description_documents, content, HARM_FILE, field_type):
                refresh_indices()
                print(f"Added new harm description: {content}")

    def web_application(self):
        self.webEngineView.setUrl(QUrl("file:///D:/EzzMedical/Risk_Management_System/References/ISO%2014971%20-%202019%20Document.html"))
        self.sideBarFrame.layout().addWidget(self.webEngineView)

    def toggle_side_bar(self):
        if self.modeSideBar.isChecked():
            new_width = 1000
        else:
            new_width = 0
        self.animation = QPropertyAnimation(self.sideBarFrame, b"minimumWidth")
        self.animation.setDuration(40)
        self.animation.setEndValue(new_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
        self.sideBarFrame.update()

    def toggle_meeting_label(self):
        height = 60
        self.meeting_frame.setFixedHeight(height)

    def toggle_meeting_frame(self):
        height = 0
        self.meeting_frame.setFixedHeight(height)

    def add_reference(self):
        current_id = self.rsk_no_combo.currentText()
        current_text = self.source_combo.currentText()
        if current_text == "International Standards":
            current_text = self.standards_combo.currentText()
        else:
            current_text = self.source_combo.currentText()
        self.sources.addItem(current_id + "         " + current_text)

    def init_search_lists(self):
        self.ser_ver_layout.addWidget(self.seq_list_widget)
        self.seq_list_widget.setFixedHeight(150)
        self.seq_list_widget.hide()
        self.sit_ver_layout.addWidget(self.sit_list_widget)
        self.sit_list_widget.setFixedHeight(150)
        self.sit_list_widget.hide()
        self.harm_ver_layout.addWidget(self.harm_list_widget)
        self.harm_list_widget.setFixedHeight(150)
        self.harm_list_widget.hide()

    def init_combos(self):
        self.department_combo.addItems(["  ", "Software Department", "Electrical Department", "Mechanical Department",
                                        "Usability Team", "Testing Team"])

        self.hazard_category_combo.addItems(
            ["  ", "Acoustic energy", "Electric energy", "Mechanical energy", "Potential energy", "Radiation energy",
             "Thermal energy", "Biological agents", "Chemical agents", "Immunological agents", "Data", "Delivery",
             "Diagnostic information", "Functionality", "Other"])

        self.harm_influenced_combo.addItems(["  ", "Patient", "User", "Property", "Environment"])

        self.lifecycle_combo.addItems(["   ", 'Concept', "Design", "Production", "Post-Production", "Validation",
                                       "Verification", "Storage"])

        self.source_combo.addItems(["   ", "BrainStorming", "Adverse Event Reports", "Device Characteristics",
                                    "Usability tests", "International Standards", "Clinical Investigations"
                                                                                  "Literature Review",
                                    "Clinical Equivalences", "Verification/Validation Results "
                                                             "Post-Market Surveillance"])
        self.standards_combo.addItems([
            "ISO 13485: Medical devices — Quality management systems — Requirements for regulatory purposes.",
            "ISO 14971: Medical devices — Application of risk management to medical devices.",
            "ISO 14155: Clinical investigation of medical devices for human subjects — Good clinical practice.",
            "IEC 62304: Medical device software — Software life cycle processes.",
            "ISO 12207: Systems and software engineering — Software life cycle processes.",
            "ISO/IEC 80601: Medical electrical equipment", "IEC 60601 series: Medical electrical equipment.",
            "ISO 80601-2-12: Ventilators", "ISO 80601-2-55: Respiratory gas monitors", "ISO 80601-2-70: CPAP",
            "ISO 80601-2-56: Clinical thermometers for body temperature measurements", "ISO 80601-2-13: Anaesthetic",
            "IEC 61010-1: Safety requirements for electrical equipment for measurement, control, and laboratory use — Part 1: General requirements.",
            "IEC 60601-2-12: Basic safety and essential performance of critical care ventilators",
            "IEC 60601-2-13: Basic safety and essential performance of anaesthetic",
            "IEC 62366: Medical devices — Application of usability engineering to medical devices.",
            "ISO 9241 series: Ergonomics of human-system interaction (for usability in general).",
            "ISO 17025: General requirements for the competence of testing and calibration laboratories.",
            "ISO 9001: Quality management systems — Requirements (general standard, but includes validation processes).",
            "ISO 10993 series: Biological evaluation of medical devices.",
            "ISO 15223-1: Medical devices — Symbols to be used with medical device labels, labelling, and information to be supplied — Part 1: General requirements.",

        ])
        self.standards_combo.hide()

        self.table_widget.setColumnCount(17)
        self.table_widget.setHorizontalHeaderLabels([
            "Date", "Risk No.", "Department", "Device Affected", "Components", "Lifecycle", "Hazard Category",
            "Hazard Source", "Hazardous Situation", "Sequence of Events", "Harm Influenced", "Harm Description",
            "Severity", "Probability", "RPN", "Risk Control Actions",  "Approved By"
        ])

        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.dectability_spin_box.setMinimum(1)
        self.dectability_spin_box.setMaximum(10)
        self.dectability_spin_box.setValue(1)
        self.dectaility_label.setText('Certain')

        self.severity_spinbox.setMinimum(1)
        self.severity_spinbox.setMaximum(5)
        self.severity_spinbox.setValue(1)
        self.severity_description_label.setText('Discomfort')

        self.probability_spinbox.setMinimum(1)
        self.probability_spinbox.setMaximum(5)
        self.probability_spinbox.setValue(1)
        self.probability_description_label.setText('Improbable')

        self.rpn_value_label.setStyleSheet("background-color: light gray;")
        self.table_widget.horizontalHeader().setMinimumSectionSize(350)
        self.update_rpn_value()
        self.generate_and_set_id()

    def update_hazard_sources(self):
        hazard_sources = {
            "Acoustic energy": ["infrasound", "sound pressure", "ultrasonic"],
            "Electric energy": ["Electric fields", "Leakage current", "earth leakage", "enclosure leakage",
                                "Magnetic fields", "Static discharge", "Voltage"],
            "Mechanical energy": ["falling objects", "high pressure fluid injection", "moving parts", "vibrating parts",
                                  "suspended mass", "tension", "torsion"],
            "Potential energy": ["bending", "compression", "cutting, shearing", "gravitational pull"],
            "Radiation energy": ["gamma", "x-ray"],
            "Thermal energy": ["Cryogenic effects", "Hyperthermic effects"],
            "Biological agents": ["Bacteria", "Fungi", "Parasites", "Prions", "Toxins", "Viruses"],
            "Chemical agents": ["Carcinogenic, mutagenic, reproductive", "Caustic, corrosive",
                                "Flammable, combustible, explosive", "Fumes, vapor", "Osmotic", "Pyrogenic", "Solvents",
                                "asbestos", "heavy metals", "inorganic toxicants", "organic toxicants", "silica"],
            "Immunological agents": ["Allergenic"],
            "Data": ["access", "availability", "confidentiality", "integrity"],
            "Delivery": ["quantity", "rate", "transfer"],
            "Diagnostic information": ["examination result", "image artefacts", "image orientation", "measurement"],
            "Functionality": ["alarm", "critical performance"],
            "Other": []
        }

        category = self.hazard_category_combo.currentText()
        self.hazard_source_combo.clear()
        self.hazard_source_combo.addItems(hazard_sources.get(category, []))

    def check_standards(self):
        ref = self.source_combo.currentText()
        if ref == "International Standards":
            self.standards_combo.show()
        else:
            self.standards_combo.hide()

    def set_risk_number(self):
        department = self.department_combo.currentText()
        if department == "Software Department":
            self.risk_no_line_edit.setText(f"RSK_SW_{self.sw_counter}")
        elif department == "Electrical Department":
            self.risk_no_line_edit.setText(f"RSK_ELC_{self.elc_counter}")
        elif department == "Mechanical Department":
            self.risk_no_line_edit.setText(f"RSK_MEC_{self.mec_counter}")
        elif department == "Usability Team":
            self.risk_no_line_edit.setText(f"RSK_US_{self.us_counter}")
        elif department == "Testing Team":
            self.risk_no_line_edit.setText(f"RSK_TEST_{self.test_counter}")

    def update_rsk_number_combo(self):
        department = self.department_combo.currentText()
        if department == "Software Department":
            self.rsk_no_combo.addItems([f"RSK_SW_{self.sw_counter}"])
        elif department == "Electrical Department":
            self.rsk_no_combo.addItems([f"RSK_ELC_{self.elc_counter}"])
        elif department == "Mechanical Department":
            self.rsk_no_combo.addItems([f"RSK_MEC_{self.mec_counter}"])
        elif department == "Usability Team":
            self.rsk_no_combo.addItems([f"RSK_US_{self.us_counter}"])
        elif department == "Testing Team":
            self.rsk_no_combo.addItems([f"RSK_TEST_{self.test_counter}"])

    def generate_risk_number(self, flag):
        department = self.department_combo.currentText()
        if department == "Software Department":
            if flag == "remove":
                self.sw_counter -= 1
            elif flag == "add":
                self.sw_counter += 1

        elif department == "Electrical Department":
            if flag == "remove":
                self.elc_counter -= 1
            elif flag == "add":
                self.elc_counter += 1

        elif department == "Mechanical Department":
            if flag == "remove":
                self.mec_counter -= 1
            elif flag == "add":
                self.mec_counter += 1

        elif department == "Usability Team":
            if flag == "remove":
                self.us_counter -= 1
            elif flag == "add":
                self.us_counter += 1

        elif department == "Testing Team":
            if flag == "remove":
                self.test_counter -= 1
            elif flag == "add":
                self.test_counter += 1

    def generate_and_set_id(self):
        random_id = "RISK" + str(random.randint(10000000, 99999999))
        self.ID_line.setText(random_id)
        self.ID_line.setReadOnly(True)

    def update_seq_ver_layout(self):
        self.seq_list_widget.show()
        line_edit_type = "sequence"
        self.update_layout(self.sequence_of_event_edit, self.seq_list_widget, line_edit_type)
        self.start_hide_timer(self.seq_hide_timer, self.seq_list_widget)

    def update_sit_ver_layout(self):
        self.sit_list_widget.show()
        line_edit_type = "situation"
        self.update_layout(self.hazardous_situation_edit, self.sit_list_widget, line_edit_type)
        self.start_hide_timer(self.sit_hide_timer, self.sit_list_widget)

    def update_harm_vec_layout(self):
        self.harm_list_widget.show()
        line_edit_type = "harm_desc"
        self.update_layout(self.harm_desc_line, self.harm_list_widget, line_edit_type)
        self.start_hide_timer(self.harm_hide_timer, self.harm_list_widget)

    def update_layout(self, line_edit, list_widget, line_edit_type):
        search_terms = line_edit.text()
        highlighted_results = []
        if not search_terms:
            list_widget.clear()
            list_widget.hide()
            return
        if line_edit_type == "harm_desc":
            results = search_documents(search_terms, harm_description_inverted_index, harm_description_documents)
            highlighted_results = rank_and_highlight(results, search_terms, harm_description_documents, scores)

        elif line_edit_type == "sequence":
            results = search_documents(search_terms, sequence_of_event_inverted_index, sequence_of_event_documents)
            highlighted_results = rank_and_highlight(results, search_terms, sequence_of_event_documents, scores)

        elif line_edit_type == "situation":
            results = search_documents(search_terms, hazardous_situation_inverted_index, hazardous_situation_documents)
            highlighted_results = rank_and_highlight(results, search_terms, hazardous_situation_documents, scores)

        list_widget.clear()
        if not highlighted_results:
            list_widget.addItem("No results found")
        else:
            for doc_id, content, score in highlighted_results:
                list_widget.addItem(f"ID: {doc_id} \n{content}")

    def add_to_sequence_of_event_edit(self, item):
        self.sequence_of_event_edit.setText(item.text())
        self.seq_list_widget.hide()
        self.seq_hide_timer.stop()

    def add_to_hazardous_situation_edit(self, item):
        self.hazardous_situation_edit.setText(item.text())
        self.sit_list_widget.hide()
        self.sit_hide_timer.stop()

    def add_to_harm_desc_line(self, item):
        self.harm_desc_line.setText(item.text())
        self.harm_list_widget.hide()
        self.harm_hide_timer.stop()

    def add_new_line_edit(self, layout):
        new_widget = self.create_control_action_widget()
        layout.insertWidget(layout.count() - 1, new_widget)

    def create_control_action_widget(self, text=""):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        if text:
            control_action_label = QLabel(text)
            layout.addWidget(control_action_label)
        else:
            control_action_edit = QLineEdit()
            layout.addWidget(control_action_edit)

            ok_button = QPushButton("OK")
            layout.addWidget(ok_button)
            ok_button.clicked.connect(lambda: self.set_control_action_text(control_action_edit, layout, ok_button))

        return widget

    def set_control_action_text(self, control_action_edit, layout, ok_button):
        text = control_action_edit.text()
        if text:
            control_action_label = QLabel(text)

            layout.insertWidget(0, control_action_label)

            control_action_edit.clear()
            control_action_edit.setVisible(False)
            ok_button.setVisible(False)

    def show_context_menu(self, position):
        menu = QMenu(self)
        edit_action = menu.addAction("Edit Cell")
        approved_by = menu.addAction("Approve")
        reject_by = menu.addAction("Reject")
        extract_action = menu.addAction("Extract")
        remove_action = menu.addAction("Remove")
        history_action = menu.addAction("See History")
        filter_action = menu.addAction("Filter Risks")
        save_action = menu.addAction("💾 Save to Database")
        backup_action = menu.addAction("🔄 Create Backup")

        action = menu.exec_(self.table_widget.mapToGlobal(position))
        if action == edit_action:
            index = self.table_widget.indexAt(position)
            if index.isValid():
                # Store previous value before editing
                item = self.table_widget.item(index.row(), index.column())
                if item:
                    item._previous_value = item.text()
                self.table_widget.editItem(item)
        elif action == extract_action:
            self.extract_row()
        elif action == remove_action:
            self.remove_row()
        elif action == approved_by:
            self.approved_by()
        elif action == reject_by:
            self.reject_process()
        elif action == history_action:
            index = self.table_widget.indexAt(position)
            if index.isValid():
                self.show_risk_history(index.row())
        elif action == filter_action:
            self.open_filter_dialog()
        elif action == save_action:
            if self.save_data_to_database():
                QMessageBox.information(self, "Saved", "All data has been saved to database!")
            else:
                QMessageBox.critical(self, "Save Error", "Failed to save data to database!")
        elif action == backup_action:
            if self.db_manager.backup_database():
                QMessageBox.information(self, "Backup Created", "Database backup has been created successfully!")
            else:
                QMessageBox.critical(self, "Backup Error", "Failed to create database backup!")

    def extract_row(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        row_data = [self.table_widget.item(row, col).text() if self.table_widget.item(row, col) else "" for col in
                    range(self.table_widget.columnCount())]

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)", options=options)
        if file_path:
            self.save_to_pdf(row_data, file_path)

    def save_to_pdf(self, row_data, file_path):
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        text = c.beginText(40, height - 40)
        text.setFont("Helvetica", 12)

        headers = ["Risk No.", "Department", "Device Affected", "Lifecycle", "Hazard Category", "Hazard Source",
                   "Hazardous Situation", "Sequence of event", "Harm Influenced", "Harm Description", "Severity",
                   "Probability", "RPN", "Risk Control Actions", "Type of Control", "Control Requirements", "Date"]

        for header, data in zip(headers, row_data):
            text.textLine(f"{header}: {data}")

        c.drawText(text)
        c.showPage()
        c.save()

    def remove_row(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        
        # Get risk ID before removing
        risk_id = self.get_risk_id_for_row(row)
        
        # Confirm deletion
        reply = QMessageBox.question(self, 'Remove Risk', 
                                   f'Are you sure you want to remove risk {risk_id}?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.table_widget.removeRow(row)
            self.generate_risk_number(flag="remove")
            self.set_risk_number()
            self.num_risks -= 1
            
            # Remove from risk history
            if risk_id and risk_id in self.risk_history:
                del self.risk_history[risk_id]
                self.save_risk_history()
            
            # Auto-save after removal
            self.save_data_to_database()

    def open_enhanced_pdf_dialog(self):
        """Open the enhanced PDF generation dialog"""
        dialog = EnhancedPDFDialog(self)
        dialog.exec_()

    def generate_filtered_pdf(self, filter_type, filter_value):
        """Generate PDF based on filter criteria"""
        data = []
        row_count = self.table_widget.rowCount()
        
        for row in range(row_count):
            include_row = False
            
            if filter_type == "Department":
                dept_item = self.table_widget.item(row, 2)  # Department column
                if dept_item and dept_item.text() == filter_value:
                    include_row = True
                    
            elif filter_type == "Device":
                device_item = self.table_widget.item(row, 3)  # Device Affected column
                if device_item and filter_value in device_item.text():
                    include_row = True
                    
            elif filter_type == "Risk Level":
                rpn_item = self.table_widget.item(row, 14)  # RPN column
                if rpn_item and rpn_item.text() == filter_value:
                    include_row = True
                    
            elif filter_type == "Approval Status":
                approval_item = self.table_widget.item(row, 16)  # Approved By column
                approval_status = "Pending"  # Default status
                if approval_item and approval_item.text().strip():
                    if "rejected" in approval_item.text().lower():
                        approval_status = "Rejected"
                    else:
                        approval_status = "Approved"
                
                if approval_status == filter_value:
                    include_row = True
            
            if include_row:
                row_data = []
                for column in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row, column)
                    row_data.append(item.text() if item is not None else "")
                data.append(row_data)

        if not data:
            QMessageBox.information(self, "No Data", f"No data found for {filter_type}: {filter_value}")
            return

        # Generate PDF filename
        filename = f"{filter_type}_{filter_value.replace(' ', '_')}_Risk_Report.pdf"
        
        pdf = SimpleDocTemplate(filename, pagesize=landscape(A4))
        elements = []

        def create_table_with_limited_columns(data, headers):
            tables = []
            columns_per_page = 3
            risk_no_idx = 0
            for start_col in range(1, len(headers), columns_per_page):
                end_col = start_col + columns_per_page
                sub_data = [[headers[risk_no_idx]] + headers[start_col:end_col]]
                for row in data:
                    sub_data.append([row[risk_no_idx]] + row[start_col:end_col])

                table = Table(sub_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('COLWIDTHS', (0, 0), (-1, -1), 200 / columns_per_page),
                ]))
                tables.append(table)
            return tables

        headers = [self.table_widget.horizontalHeaderItem(col).text() for col in range(self.table_widget.columnCount())]
        tables = create_table_with_limited_columns(data, headers)

        for table in tables:
            elements.append(table)
            elements.append(Spacer(1, 20))

        pdf.build(elements)
        QMessageBox.information(self, "PDF Generated", f"PDF for {filter_type}: {filter_value} has been generated as {filename}")

    def reject_process(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()

        def reject_action():
            reason = "The process rejected because : " + reason_edit.text()
            if reason:
                reason_item = QTableWidgetItem(reason)
                reason_item.setBackground(QColor('black'))
                self.table_widget.setItem(row, 16, QTableWidgetItem(reason_item))
                dialog.accept()
                # Auto-save after rejection
                self.save_data_to_database()

        dialog = QDialog(self)
        dialog.setWindowTitle("Reject the process")
        layout = QVBoxLayout(dialog)

        label = QLabel("Reason for rejection: ")
        layout.addWidget(label)

        reason_edit = QLineEdit()
        layout.addWidget(reason_edit)

        reject_btn = QPushButton("Reject")
        layout.addWidget(reject_btn)

        reject_btn.clicked.connect(reject_action)
        dialog.exec_()
        self.num_rejected_risks += 1

    def approved_by(self):
        manager_names = {
            1111: 'Eng. Ahmed El-Argawy',
            2222: 'Eng. Khaled',
            3333: 'Dr: Hamdi Abd El-fadel',
            4444: 'Eng. Aya Al-Mowafy',
            5555: 'Eng. Ahmed El-Rays'
        }

        def update_label():
            value = approved_by_line_edit.text()
            try:
                value = int(value)
                name_of_the_approval.setText(manager_names.get(value, ''))
            except ValueError:
                name_of_the_approval.setText('')
            self.name_of_the_approval = manager_names.get(value, '')

        dialog = QDialog(self)
        dialog.setWindowTitle("Approve the process")
        layout = QVBoxLayout(dialog)

        label = QLabel("ID: ")
        layout.addWidget(label)

        approved_by_line_edit = QLineEdit()
        layout.addWidget(approved_by_line_edit)

        name_of_the_approval = QLabel()
        layout.addWidget(name_of_the_approval)

        approved_by_line_edit.textChanged.connect(update_label)

        approved_btn = QPushButton("Approve")
        layout.addWidget(approved_btn)

        approved_btn.clicked.connect(lambda: self.add_approval(dialog))
        dialog.exec_()
        self.num_approved_risks += 1

    def add_approval(self, dialog):
        dialog.close()
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return
        row = selected_items[0].row()
        self.table_widget.setItem(row, 16, QTableWidgetItem(self.name_of_the_approval))
        # Auto-save after approval
        self.save_data_to_database()

    def show_charts(self):
        row_count = self.table_widget.rowCount()
        hazards = []
        rpn_values = []

        for row in range(row_count):
            hazard_source_item = self.table_widget.item(row, 7)
            rpn_item = self.table_widget.item(row, 14)

            if hazard_source_item and rpn_item:
                hazards.append(hazard_source_item.text())
                rpn_values.append(rpn_item.text().strip().upper())

        hazard_counts = Counter(hazards)
        sorted_hazard_counts = sorted(hazard_counts.items(), key=lambda x: x[1], reverse=True)
        hazard_labels, hazard_values = zip(*sorted_hazard_counts) if sorted_hazard_counts else ([], [])

        fig_hazard = Figure()
        canvas_hazard = FigureCanvas(fig_hazard)
        ax_hazard = fig_hazard.add_subplot(111)
        bars_hazard = ax_hazard.barh(hazard_labels, hazard_values)
        ax_hazard.set_xlabel('Frequency')
        ax_hazard.set_title('Most Frequent Hazard Sources')
        ax_hazard.invert_yaxis()

        for bar in bars_hazard:
            ax_hazard.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2, int(bar.get_width()), va='center')

        rpn_counts = Counter(rpn_values)
        print(f"RPN_Values Counting{rpn_values}")
        rpn_fixed_order = ['HIGH', 'MEDIUM', 'LOW']
        rpn_labels = []
        rpn_values = []
        
        for rpn in rpn_fixed_order:
            rpn_labels.append(rpn)
            rpn_values.append(rpn_counts.get(rpn, 0))

        print(f"RPN_Values after appending{rpn_values}")
        print(f"RPN Labels {rpn_labels}")
        fig_rpn = Figure()
        canvas_rpn = FigureCanvas(fig_rpn)
        ax_rpn = fig_rpn.add_subplot(111)
        bars_rpn = ax_rpn.bar(rpn_labels, rpn_values, color=['red', 'yellow', 'green', 'lightgray'])
        ax_rpn.set_xlabel('RPN Value')
        ax_rpn.set_ylabel('Number of Entries')
        ax_rpn.set_title('Number of Entries by RPN Value')

        for bar in bars_rpn:
            ax_rpn.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, int(bar.get_height()), ha='center')

        dialog = QDialog(self)
        dialog.setWindowTitle("Charts")
        layout = QVBoxLayout(dialog)
        layout.addWidget(canvas_hazard)
        layout.addWidget(canvas_rpn)
        dialog.setLayout(layout)
        dialog.resize(1300, 1000)
        dialog.exec_()

    def open_relation_chart(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Generate PDF")
        layout = QVBoxLayout(dialog)

        self.first_axis.addItems(['Department', 'Lifecycle', 'Components', 'Device affected', 'Hazard Category', 'Hazard Source',
                                  'Harm Influenced', 'RPN'])
        self.second_axis.addItems(['Department', 'Lifecycle','Components', 'Device affected', 'Hazard Category', 'Hazard Source',
                                   'Harm Influenced', 'RPN'])

        comboLayout = QHBoxLayout()
        comboLayout.addWidget(self.first_axis)
        comboLayout.addWidget(self.second_axis)

        showButton = QPushButton('Plot')
        showButton.clicked.connect(self.display_plotly_chart)

        layout.addLayout(comboLayout)
        layout.addWidget(showButton)
        layout.addWidget(self.webEngineView)
        dialog.setWindowTitle("Sunburst Chart")
        dialog.resize(1300, 1000)
        dialog.exec_()

    def display_plotly_chart(self):
        html = self.generate_plotly_chart()
        self.webEngineView.setHtml(html)

    def generate_plotly_chart(self):
        data = {
            'Department': [],
            'Lifecycle': [],
            'Components': [],
            'Device affected': [],
            'Hazard Category': [],
            'Hazard Source': [],
            'Harm Influenced': [],
            'RPN': [],
        }

        for row in range(self.table_widget.rowCount()):
            data['Department'].append(self.table_widget.item(row, 2).text())
            data['Device affected'].append(self.table_widget.item(row, 3).text())
            data['Components'].append(self.table_widget.item(row, 4).text())
            data['Lifecycle'].append(self.table_widget.item(row, 5).text())
            data['Hazard Category'].append(self.table_widget.item(row, 6).text())
            data['Hazard Source'].append(self.table_widget.item(row, 7).text())
            data['Harm Influenced'].append(self.table_widget.item(row, 10).text())
            data['RPN'].append(self.table_widget.item(row, 14).text())

        df = pd.DataFrame(data)
        key1 = self.first_axis.currentText()
        key2 = self.second_axis.currentText()

        group_counts = df.groupby([key1, key2]).size().reset_index(name='Count')

        labels = []
        parents = []
        values = []
        colors = []

        level1_totals = group_counts.groupby(key1)['Count'].sum().reset_index()
        for lvl1 in level1_totals[key1]:
            labels.append(lvl1)
            parents.append("")
            values.append(level1_totals[level1_totals[key1] == lvl1]['Count'].values[0])
            colors.append(lvl1)

        for idx, row in group_counts.iterrows():
            labels.append(row[key2])
            parents.append(row[key1])
            values.append(row['Count'])
            colors.append(row[key1])

        unique_keys1 = df[key1].unique()
        color_palette = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink', 'lightgray', 'lightcyan']
        key1_colors = {key: color_palette[i % len(color_palette)] for i, key in enumerate(unique_keys1)}

        color_list = [key1_colors[key] for key in colors]

        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues='total',
            marker=dict(colors=color_list)
        ))

        fig.update_layout(
            margin=dict(t=0, l=0, r=0, b=0),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        html = fig.to_html(include_plotlyjs='cdn')
        return html

    def sort_table_by_rpn(self):
        priorities = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "": 3}
        row_count = self.table_widget.rowCount()

        data = []
        for row in range(row_count):
            row_data = []
            for column in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, column)
                if item is None:
                    row_data.append("")
                else:
                    row_data.append(item.text())
            rpn_value = row_data[14]
            data.append((row_data, priorities[rpn_value]))

        data.sort(key=lambda x: x[1])

        self.table_widget.setRowCount(0)
        for row_data, _ in data:
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            for col, item_text in enumerate(row_data):
                self.table_widget.setItem(row_position, col, QTableWidgetItem(item_text))

    def show_rpn_matrix(self):
        """Show enhanced device-specific risk matrix dialog"""
        dialog = EnhancedMatrixDialog(self)
        dialog.exec_()


    def update_dectability_label(self):
        dectability_map = {
            1: 'Certain',
            2: 'Likely',
            3: 'Expected',
            4: 'Possible',
            5: 'Doubtful',
            6: 'Unlikely',
            7: 'Improbable',
            8: 'Rare',
            9: 'Negligible',
            10: 'Impossible'
        }
        value = self.dectability_spin_box.value()
        self.dectaility_label.setText(dectability_map.get(value, ''))

    def update_severity_label(self):
        severity_map = {
            1: 'Discomfort',
            2: 'Minor',
            3: 'Serious',
            4: 'Critical',
            5: 'Catastrophical'
        }
        value = self.severity_spinbox.value()
        self.severity_description_label.setText(severity_map.get(value, ''))

    def update_probability_label(self):
        probability_map = {
            1: 'Improbable',
            2: 'Remote',
            3: 'Occasional',
            4: 'Probable',
            5: 'Frequent'
        }
        value = self.probability_spinbox.value()
        self.probability_description_label.setText(probability_map.get(value, ''))

    def update_rpn_value(self):
        """Update RPN value based on current device matrix"""
        severity = self.severity_spinbox.value()
        probability = self.probability_spinbox.value()
        
        # Get current device from the selected devices
        current_device = None
        if self.checked_items:
            current_device = self.checked_items[0]  # Use first selected device
        
        if current_device:
            rpn = self.get_rpn_from_matrix(current_device, severity, probability)
        else:
            # Fallback to hardcoded values if no device selected
            rpn = self.get_hardcoded_rpn(severity, probability)
        
        # Set color based on RPN value
        colors = {"High": "red", "Medium": "yellow", "Low": "green"}
        color = colors.get(rpn, "lightgray")
        
        self.rpn_value_label.setText(rpn)
        self.rpn_value_label.setStyleSheet(f"background-color: {color}; color: black;")
        return rpn
    
    def get_rpn_from_matrix(self, device, severity, probability):
        """Get RPN from device-specific matrix"""
        matrix_file = os.path.join('Risk Matrix', f"{device.replace(' ', '_')}_matrix.json")
        
        try:
            if os.path.exists(matrix_file):
                with open(matrix_file, 'r') as f:
                    matrix_data = json.load(f)
                
                # Convert to 0-based indices
                row = severity - 1
                col = probability - 1
                
                if 0 <= row <= 4 and 0 <= col <= 4:
                    key = f"{row},{col}"
                    if key in matrix_data:
                        return matrix_data[key]["text"]
            
            # If file doesn't exist or key not found, return default
            return self.get_hardcoded_rpn(severity, probability)
            
        except Exception as e:
            print(f"Error reading matrix for {device}: {e}")
            return self.get_hardcoded_rpn(severity, probability)

    def get_hardcoded_rpn(self, severity, probability):
        """Fallback hardcoded RPN calculation"""
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

    def on_matrix_updated(self, device):
        """Called when matrix is updated for a device"""
        # Refresh RPN if current device matches updated device
        if self.checked_items and device in self.checked_items:
            self.update_rpn_value()
            print(f"RPN updated for device: {device}")


def main():
    app = QApplication(sys.argv)
    # app.setStyle('Fusion')  # Modern look
    window = RiskSystem()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
