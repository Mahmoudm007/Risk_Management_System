from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import (QPushButton, QLabel,QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QAbstractItemView, QMenu)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.uic import loadUiType
import os
import random
import json
from PyQt5.QtCore import QDateTime, QPropertyAnimation, QEasingCurve, QUrl
from collections import Counter
from matplotlib.figure import Figure
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
import pandas as pd
import plotly.graph_objects as go
from PyQt5.QtWebEngineWidgets import QWebEngineView

from Calendar import CalendarDialog
from ControlAndRequirement import AddControlClass
from Dashboard import Dashboard
from DeviceSelection import DeviceSelected
from RiskChat import ChatDialog
from search import *
from SortTable import SortableTableWidgetItem


URRENT_DIR = os.path.dirname(os.path.realpath(__file__))
MainUI, _ = loadUiType('mainWindowui.ui')


class RiskSystem(QMainWindow, MainUI):
    def __init__(self):
        super(RiskSystem, self).__init__()
        self.setupUi(self)
        self.setGeometry(0, 0, 1900, 950)

        self.sw_counter = 0
        self.elc_counter = 0
        self.mec_counter = 0
        self.us_counter = 0
        self.test_counter = 0

        self.chat_data = {}
        self.chat_widgets = {}

        self.checked_items = []

        self.first_axis = QComboBox()
        self.second_axis = QComboBox()
        self.webEngineView = QWebEngineView()
        
        self.seq_list_widget = QtWidgets.QListWidget()
        self.sit_list_widget = QtWidgets.QListWidget()
        self.harm_list_widget = QtWidgets.QListWidget()
        
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

        self.matrix_file = 'matrix_state.json'

    def buttons_signals(self):
        self.hazardous_situation_edit.textChanged.connect(self.update_sit_ver_layout)
        self.sit_list_widget.itemDoubleClicked.connect(self.add_to_hazardous_situation_edit)

        self.sequence_of_event_edit.textChanged.connect(self.update_seq_ver_layout)
        self.seq_list_widget.itemDoubleClicked.connect(self.add_to_sequence_of_event_edit)

        self.harm_desc_line.textChanged.connect(self.update_harm_vec_layout)
        self.harm_list_widget.itemDoubleClicked.connect(self.add_to_harm_desc_line)

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
        self.pdf_gen.clicked.connect(self.open_pdf_dialog)

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

    def select_devices_widget(self):
        dialog = DeviceSelected(self)
        if dialog.exec_() == QDialog.Accepted:
            self.checked_items = dialog.checked_items

    def open_calendar_dialog(self):
        # Create and open the calendar dialog
        self.calendar_dialog = CalendarDialog(self)
        self.toggle_meeting_label()
        self.calendar_dialog.exec_()

    def set_date_time_label(self, date_str, time_str):
        # Update the label with the selected date and time
        self.date_time_label.setText(f"A Meeting will be held to discuss the risk analysis within : {date_str} {time_str}")

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

        # Create and show the chat dialog
        chat_dialog = ChatDialog(row_id, self.chat_data, self)
        chat_dialog.setGeometry(100, 100, 400, 300)
        chat_dialog.exec_()  # Show dialog as modal window
        print(f"Chat dialog should be visible now.")

    def add_entry(self):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        rsk_no = self.risk_no_line_edit.text()
        self.table_widget.setItem(row_position, 0, QTableWidgetItem(rsk_no))

        # get data
        department = self.department_combo.currentText()
        self.table_widget.setItem(row_position, 1, QTableWidgetItem(department))

        self.table_widget.setItem(row_position, 2, QTableWidgetItem(', '.join(self.checked_items)))

        lifecycle = self.lifecycle_combo.currentText()
        self.table_widget.setItem(row_position, 3, QTableWidgetItem(lifecycle))

        hazard_category = self.hazard_category_combo.currentText()
        self.table_widget.setItem(row_position, 4, QTableWidgetItem(hazard_category))

        hazard_source = self.hazard_source_combo.currentText()
        self.table_widget.setItem(row_position, 5, QTableWidgetItem(hazard_source))

        hazardous_situation = self.hazardous_situation_edit.text()
        self.table_widget.setItem(row_position, 6, QTableWidgetItem(hazardous_situation))

        sequence_of_event = self.sequence_of_event_edit.text()
        self.table_widget.setItem(row_position, 7, QTableWidgetItem(sequence_of_event))
        sequence_widget = QWidget()
        sequence_layout = QVBoxLayout(sequence_widget)
        sequence_layout.addWidget(self.create_control_action_widget(sequence_of_event))

        add_button = QPushButton("+")
        add_button.clicked.connect(lambda: self.add_new_line_edit(sequence_layout))
        sequence_layout.addWidget(add_button)
        self.table_widget.setCellWidget(row_position, 7, sequence_widget)

        harm_influenced = self.harm_influenced_combo.currentText()
        self.table_widget.setItem(row_position, 8, QTableWidgetItem(harm_influenced))

        harm_desc = self.harm_desc_line.text()
        self.table_widget.setItem(row_position, 9, QTableWidgetItem(harm_desc))

        # Add custom widget to the fifth column
        tree_widget_cell = AddControlClass()
        self.table_widget.setCellWidget(row_position, 13, tree_widget_cell)

        severity = self.severity_spinbox.value()
        self.table_widget.setItem(row_position, 10, QTableWidgetItem(str(severity)))

        probability = self.probability_spinbox.value()
        self.table_widget.setItem(row_position, 11, QTableWidgetItem(str(probability)))

        RPN = self.update_rpn_value()
        self.table_widget.setItem(row_position, 12, QTableWidgetItem(RPN))

        # req_widget = QWidget()
        # req_layout = QVBoxLayout(req_widget)
        #
        # add_button = QPushButton("+")
        # add_button.clicked.connect(lambda: self.add_new_line_edit(req_layout))
        # req_layout.addWidget(add_button)
        # self.table_widget.setCellWidget(row_position, 15, req_widget)

        self.table_widget.setRowHeight(row_position, 300)

        current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.table_widget.setItem(row_position, 14, QTableWidgetItem(current_datetime))

        add_button.clicked.connect(self.generate_risk_number)
        add_button.clicked.connect(self.set_risk_number)

        self.num_risks += 1

        self.generate_and_set_id()
        self.update_rsk_number_combo()

    def web_application(self):
        # Set the URL to a simple web page the user can use any web page he need "e.g. ChatGPT, Gemini,..., etc"
        # https: // www.google.com
        self.webEngineView.setUrl(QUrl("file:///D:/ISO%2014971%20-%202019%20Document.html"))
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
        self.seq_list_widget.hide()
        self.sit_ver_layout.addWidget(self.sit_list_widget)
        self.sit_list_widget.hide()
        self.harm_ver_layout.addWidget(self.harm_list_widget)
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
                                    "Literature Review", "Clinical Equivalences", "Verification/Validation Results "
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
        self.table_widget.setColumnCount(16)
        self.table_widget.setHorizontalHeaderLabels([
            "Risk No.", "Department", "Device Affected", "Lifecycle", "Hazard Category", "Hazard Source",
            "Hazardous Situation", "Sequence of event", "Harm Influenced", "Harm Description", "Severity",
            "Probability", "RPN", "Risk Control Actions", "Date", "Approved By"
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

        self.rpn_value_label.setStyleSheet("background-color: lightgray;")
        self.table_widget.horizontalHeader().setMinimumSectionSize(400)
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
                self.mec_counter -=1
            elif flag == "add":
                self.mec_counter += 1

        elif department == "Usability Team":
            if flag == "remove":
                self.us_counter -=1
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

    def update_sit_ver_layout(self):
        self.sit_list_widget.show()
        line_edit_type = "situation"
        self.update_layout(self.hazardous_situation_edit, self.sit_list_widget, line_edit_type)

    def update_harm_vec_layout(self):
        self.harm_list_widget.show()
        line_edit_type = "harm_desc"
        self.update_layout(self.harm_desc_line, self.harm_list_widget, line_edit_type)

    def update_layout(self, line_edit, list_widget, line_edit_type):
        search_terms = line_edit.text()
        highlighted_results = []
        if not search_terms:
            list_widget.clear()
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

    def add_to_hazardous_situation_edit(self, item):
        self.hazardous_situation_edit.setText(item.text())
        self.sit_list_widget.hide()

    def add_to_harm_desc_line(self, item):
        self.harm_desc_line.setText(item.text())
        self.harm_list_widget.hide()

    # def add_to_risk_control_action_edit(self, item):
    #     self.risk_control_action_edit.setText(item.text())
    #     self.control_list_widget.hide()

    # def update_models_affected(self):
    #     if self.device_affected_combo.currentIndex() == 0:
    #         self.model_affected_combo.clear()
    #         self.model_affected_label.hide()
    #         self.model_affected_combo.hide()
    #     elif self.device_affected_combo.currentIndex() == 1:
    #         self.model_affected_combo.addItems(["EzVent M-101", "EzVent M-201", "EzVent M-202"])
    #         self.model_affected_label.show()
    #         self.model_affected_combo.show()

    def add_new_line_edit(self, layout):
        new_widget = self.create_control_action_widget()
        layout.insertWidget(layout.count() - 1, new_widget)

    # def add_new_control_action(self, layout, row_position):
    #     new_control_action_widget = self.create_control_action_widget()
    #     layout.insertWidget(layout.count() - 1, new_control_action_widget)
    #
    #     new_combo = QComboBox()
    #     new_combo.addItems(["  ", "Inherently safe design", "Protective measure", "Information for safety"])
    #     self.type_of_control_layout.addWidget(new_combo)
    #     self.table_widget.setCellWidget(row_position, 14, self.type_of_control_widget)

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

        approved_by = menu.addAction("Approve")
        reject_by = menu.addAction("Reject")
        extract_action = menu.addAction("Extract")
        remove_action = menu.addAction("Remove")

        action = menu.exec_(self.table_widget.mapToGlobal(position))
        if action == extract_action:
            self.extract_row()
        elif action == remove_action:
            self.remove_row()
        elif action == approved_by:
            self.approved_by()
        elif action == reject_by:
            self.reject_process()

    def extract_row(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        row_data = [self.table_widget.item(row, col).text() if self.table_widget.item(row, col) else "" for col in range(self.table_widget.columnCount())]

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
        self.table_widget.removeRow(row)
        self.generate_risk_number(flag="remove")
        self.set_risk_number()
        self.num_risks -= 1

    def open_pdf_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Generate PDF")
        layout = QVBoxLayout(dialog)

        label = QLabel("Select Department:")
        layout.addWidget(label)

        department_combo = QComboBox()
        department_combo.addItems(
            ["Software Department", "Electrical Department", "Mechanical Department", "Usability Team", "Testing Team"])
        layout.addWidget(department_combo)

        generate_button = QPushButton("Generate PDF")
        layout.addWidget(generate_button)

        generate_button.clicked.connect(lambda: self.generate_pdf(department_combo.currentText(), dialog))

        dialog.exec_()

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
                self.table_widget.setItem(row, 15, QTableWidgetItem(reason_item))  # Assuming 15th column for reason
                dialog.accept()

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
            1111: 'Eng: Ahmed El-Argawy',
            2222: 'Dr: Ayman',
            3333: 'Dr: Hamdi',
            4444: 'Eng: Aya Al-Mowafy',
            5555: 'Ahmed El-Rays'
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

        approved_btn.clicked.connect(lambda :self.add_approval(dialog))
        dialog.exec_()
        self.num_approved_risks += 1

    def add_approval(self, dialog):
        dialog.close()
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return
        row = selected_items[0].row()
        self.table_widget.setItem(row, 15, QTableWidgetItem(self.name_of_the_approval))

    # Generate a PDF for a specific department with all risks related from this department
    def generate_pdf(self, department, dialog):
        dialog.close()

        data = []
        row_count = self.table_widget.rowCount()
        for row in range(row_count):
            if self.table_widget.item(row, 1).text() == department:
                row_data = []
                for column in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row, column)
                    row_data.append(item.text() if item is not None else "")
                data.append(row_data)

        if not data:
            QMessageBox.information(self, "No Data", f"No data found for {department}")
            return

        pdf = SimpleDocTemplate(f"{department.replace(' ', '_')}_Risk_Report.pdf", pagesize=landscape(A4))
        elements = []

        # Function to create a table with at most 3 columns (excluding the "Risk No." column which is always included)
        def create_table_with_limited_columns(data, headers):
            tables = []
            columns_per_page = 3
            risk_no_idx = 0
            for start_col in range(1, len(headers), columns_per_page):  # Start from 1 to exclude "Risk No."
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
        QMessageBox.information(self, "PDF Generated", f"PDF for {department} has been generated.")

    # Show the carts of most frequent hazard source and the RPN values
    def show_charts(self):
        row_count = self.table_widget.rowCount()
        hazards = []
        rpn_values = []

        for row in range(row_count):
            hazard_source_item = self.table_widget.item(row, 5)  # Assuming hazard sources are in column 5
            rpn_item = self.table_widget.item(row, 12)  # RPN values are in column 14

            if hazard_source_item and rpn_item:
                hazards.append(hazard_source_item.text())
                rpn_values.append(rpn_item.text())

        # Plot most frequent hazard sources
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

        # Plot RPN counts with fixed order
        rpn_counts = Counter(rpn_values)
        rpn_fixed_order = ['HIGH', 'MEDIUM', 'LOW']
        rpn_labels = []
        rpn_values = []

        for rpn in rpn_fixed_order:
            rpn_labels.append(rpn)
            rpn_values.append(rpn_counts.get(rpn, 0))

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
        # Create a QWebEngineView widget

        self.first_axis.addItems(['Department', 'Lifecycle', 'Device affected', 'Hazard Category', 'Hazard Source',
                                  'Harm Influenced'])
        self.second_axis.addItems(['Department', 'Lifecycle', 'Device affected', 'Hazard Category', 'Hazard Source',
                                  'Harm Influenced'])

        # Create a horizontal layout for the combo boxes
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
        # Generate the Plotly chart as HTML
        html = self.generate_plotly_chart()
        # Load the HTML into the QWebEngineView
        self.webEngineView.setHtml(html)

    def generate_plotly_chart(self):
        # Collect data from the table widget
        data = {
            'Department': [],
            'Lifecycle': [],
            'Device affected': [],
            'Hazard Category': [],
            'Hazard Source': [],
            'Harm Influenced': []
        }

        for row in range(self.table_widget.rowCount()):
            data['Department'].append(self.table_widget.item(row, 1).text())
            data['Device affected'].append(self.table_widget.item(row, 2).text())
            data['Lifecycle'].append(self.table_widget.item(row, 3).text())
            data['Hazard Category'].append(self.table_widget.item(row, 4).text())
            data['Hazard Source'].append(self.table_widget.item(row, 5).text())
            data['Harm Influenced'].append(self.table_widget.item(row, 8).text())

        # Create a DataFrame
        df = pd.DataFrame(data)
        # Get the selected keys from the combo boxes
        key1 = self.first_axis.currentText()
        key2 = self.second_axis.currentText()

        # Grouping by the selected keys, then counting
        group_counts = df.groupby([key1, key2]).size().reset_index(name='Count')

        # Creating the sunburst chart
        labels = []
        parents = []
        values = []
        colors = []

        # Add first level keys to labels and calculate totals per first level key
        level1_totals = group_counts.groupby(key1)['Count'].sum().reset_index()
        for lvl1 in level1_totals[key1]:
            labels.append(lvl1)
            parents.append("")
            values.append(level1_totals[level1_totals[key1] == lvl1]['Count'].values[0])
            colors.append(lvl1)

        # Add second level keys under each first level key
        for idx, row in group_counts.iterrows():
            labels.append(row[key2])
            parents.append(row[key1])
            values.append(row['Count'])
            colors.append(row[key1])

        # Define colors for the first level keys
        unique_keys1 = df[key1].unique()
        color_palette = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink', 'lightgray', 'lightcyan']
        key1_colors = {key: color_palette[i % len(color_palette)] for i, key in enumerate(unique_keys1)}

        # Map colors to the corresponding first level keys
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
            paper_bgcolor='white',  # Set the background color of the entire figure
            plot_bgcolor='white'  # Set the background color of the plot area
        )
        # Generate the HTML representation of the Plotly chart
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

        # Sort data based on RPN priorities
        data.sort(key=lambda x: x[1])

        self.table_widget.setRowCount(0)
        for row_data, _ in data:
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            for col, item_text in enumerate(row_data):
                self.table_widget.setItem(row_position, col, QTableWidgetItem(item_text))

    def show_rpn_matrix(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Risk Matrix")
        layout = QVBoxLayout(dialog)

        self.matrix_table = QTableWidget()
        self.matrix_table.setRowCount(5)
        self.matrix_table.setColumnCount(5)
        self.matrix_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.matrix_table.customContextMenuRequested.connect(self.show_menu)

        # Set the table headers
        self.matrix_table.setHorizontalHeaderLabels(
            ['Improbable (1)', 'Remote (2)', 'Occasional (3)', 'Probable (4)', 'Frequent (5)'])
        self.matrix_table.setVerticalHeaderLabels(
            ['Discomfort (1)', 'Minor (2)', 'Serious (3)', 'Critical (4)', 'Catastrophic (5)'])

        # Set the cell colors and text based on the row and column specifications

        self.set_cell_properties()
        self.load_matrix_state()

        layout.addWidget(self.matrix_table)
        dialog.setLayout(layout)
        dialog.resize(785, 260)
        dialog.exec_()

    def set_cell_properties(self):
        # Row 1
        self.set_cell(0, 0, 'Low', QColor('green'))
        self.set_cell(0, 1, 'Low', QColor('green'))
        self.set_cell(0, 2, 'Low', QColor('green'))
        self.set_cell(0, 3, 'Low', QColor('green'))
        self.set_cell(0, 4, 'Medium', QColor('yellow'))

        # Row 2
        self.set_cell(1, 0, 'Low', QColor('green'))
        self.set_cell(1, 1, 'Low', QColor('green'))
        self.set_cell(1, 2, 'Medium', QColor('yellow'))
        self.set_cell(1, 3, 'Medium', QColor('yellow'))
        self.set_cell(1, 4, 'Medium', QColor('yellow'))

        # Row 3
        self.set_cell(2, 0, 'Low', QColor('green'))
        self.set_cell(2, 1, 'Medium', QColor('yellow'))
        self.set_cell(2, 2, 'Medium', QColor('yellow'))
        self.set_cell(2, 3, 'High', QColor('red'))
        self.set_cell(2, 4, 'High', QColor('red'))

        # Row 4
        self.set_cell(3, 0, 'Low', QColor('green'))
        self.set_cell(3, 1, 'Medium', QColor('yellow'))
        self.set_cell(3, 2, 'High', QColor('red'))
        self.set_cell(3, 3, 'High', QColor('red'))
        self.set_cell(3, 4, 'High', QColor('red'))

        # Row 5
        self.set_cell(4, 0, 'Medium', QColor('yellow'))
        self.set_cell(4, 1, 'Medium', QColor('yellow'))
        self.set_cell(4, 2, 'High', QColor('red'))
        self.set_cell(4, 3, 'High', QColor('red'))
        self.set_cell(4, 4, 'High', QColor('red'))

    def set_cell(self, row, col, text, color):
        item = QTableWidgetItem(text)
        item.setBackground(color)
        self.matrix_table.setItem(row, col, item)

    def show_menu(self, position):
        menu = QMenu(self)

        high_action = QAction('High', self)
        high_action.triggered.connect(lambda: self.set_cell_value('High', QColor('red')))
        menu.addAction(high_action)

        medium_action = QAction('Medium', self)
        medium_action.triggered.connect(lambda: self.set_cell_value('Medium', QColor('yellow')))
        menu.addAction(medium_action)

        low_action = QAction('Low', self)
        low_action.triggered.connect(lambda: self.set_cell_value('Low', QColor('green')))
        menu.addAction(low_action)

        menu.exec_(self.matrix_table.viewport().mapToGlobal(position))

    def set_cell_value(self, value, color):
        selected_items = self.matrix_table.selectedItems()
        for item in selected_items:
            item.setText(value)
            item.setBackground(color)
        self.save_matrix_state()  # Save changes after editing

    def save_matrix_state(self):
        matrix_state = {}

        for row in range(self.matrix_table.rowCount()):
            print(f"rows: {row}")
            for col in range(self.matrix_table.columnCount()):
                print(f"column: {col}")
                item = self.matrix_table.item(row, col)
                print(f"item: {item}")
                if item:
                    key = f"{row},{col}"
                    matrix_state[key] = {
                        'text': item.text(),
                        'color': item.background().color().name()
                    }
                    # print(f"matrix state: {matrix_state[(row, col)]}")

        with open(self.matrix_file, 'w') as file:
            json.dump(matrix_state, file)

    def load_matrix_state(self):
        if not os.path.exists(self.matrix_file):
            return

        with open(self.matrix_file, 'r') as file:
            matrix_state = json.load(file)

        for key, properties in matrix_state.items():
            row, col = map(int, key.split(','))
            color = QColor(properties['color'])
            self.set_cell(row, col, properties['text'], color)

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
            10:'Impossible'
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
        severity = self.severity_spinbox.value()
        probability = self.probability_spinbox.value()
        if (severity >= 4 and probability >= 3) or (severity == 3 and probability >= 4):
            rpn = 'HIGH'
            color = 'red'
        elif ((severity >= 4 and probability <= 3) or (severity < 3 and probability == 5)
              or (severity == 2 and probability >= 3) or (severity == 3 and probability in [2, 3])):
            rpn = 'MEDIUM'
            color = 'yellow'
        elif ((severity == 1 and probability <= 4) or (severity == 2 and probability in [1, 2]) or
              (severity == 3 and probability == 1)):
            rpn = 'LOW'
            color = 'green'
        else:
            rpn = ''
            color = 'lightgray'

        self.rpn_value_label.setText(rpn)
        self.rpn_value_label.setStyleSheet(f"background-color: {color}; color: black;")
        return rpn


def main():
    app = QApplication(sys.argv)
    window = RiskSystem()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()