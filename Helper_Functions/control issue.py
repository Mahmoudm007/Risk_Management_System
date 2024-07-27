import sys

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, \
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt5.QtCore import QDateTime
from PyQt5.QtGui import QFont

class HazardManager(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setGeometry(10, 50, 1900, 950)
        self.apply_stylesheet()
    def initUI(self):
        # Layouts
        main_layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        form_left_layout = QVBoxLayout()
        form_right_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Hazard category combo box
        self.hazard_category_label = QLabel("Hazard Category:")
        self.hazard_category_combo = QComboBox()
        self.hazard_category_combo.addItems([
            "Acoustic energy", "Electric energy", "Mechanical energy", "Potential energy",
            "Radiation energy", "Thermal energy", "Biological agents", "Chemical agents",
            "Immunological agents", "Data", "Delivery", "Diagnostic information",
            "Functionality", "Other"
        ])
        self.hazard_category_combo.currentIndexChanged.connect(self.update_hazard_sources)
        form_left_layout.addWidget(self.hazard_category_label)
        form_left_layout.addWidget(self.hazard_category_combo)

        # Hazard source combo box
        self.hazard_source_label = QLabel("Hazard Source:")
        self.hazard_source_combo = QComboBox()
        form_left_layout.addWidget(self.hazard_source_label)
        form_left_layout.addWidget(self.hazard_source_combo)

        # Hazardous situation input
        self.hazardous_situation_label = QLabel("Hazardous Situation:")
        self.hazardous_situation_edit = QLineEdit()
        form_right_layout.addWidget(self.hazardous_situation_label)
        form_right_layout.addWidget(self.hazardous_situation_edit)

        # Harm influenced combo box
        self.harm_influenced_label = QLabel("Harm Influenced:")
        self.harm_influenced_combo = QComboBox()
        self.harm_influenced_combo.addItems(["Patient", "User", "Property", "Environment"])
        form_right_layout.addWidget(self.harm_influenced_label)
        form_right_layout.addWidget(self.harm_influenced_combo)

        # Risk control action input
        self.risk_control_action_label = QLabel("Risk Control Action:")
        self.risk_control_action_edit = QLineEdit()
        self.control_type_combo = QComboBox()
        self.control_type_combo.addItems(["  ", "Inherently safe design", "Protective measure", "Information for safety"])

        risk_control_layout = QHBoxLayout()
        risk_control_layout.addWidget(self.risk_control_action_edit)
        risk_control_layout.addWidget(self.control_type_combo)

        form_right_layout.addWidget(self.risk_control_action_label)
        form_right_layout.addLayout(risk_control_layout)

        form_layout.addLayout(form_left_layout)
        form_layout.addLayout(form_right_layout)

        # Add button
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_entry)
        button_layout.addWidget(self.add_button)

        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels([
            "Hazard Category", "Hazard Source", "Hazardous Situation", "Harm Influenced",
            "Risk Control Actions", "Type of Control", "Date"
        ])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make table uneditable

        # Add layouts to main layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table_widget)

        self.setLayout(main_layout)
        self.setWindowTitle('Hazard Manager')
        self.show()

        # Initial update of hazard sources
        self.update_hazard_sources()
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

    def add_entry(self):
        # Get current date and time
        current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

        # Get inputs
        hazard_category = self.hazard_category_combo.currentText()
        hazard_source = self.hazard_source_combo.currentText()
        hazardous_situation = self.hazardous_situation_edit.text()
        harm_influenced = self.harm_influenced_combo.currentText()
        risk_control_action = self.risk_control_action_edit.text()
        control_type = self.control_type_combo.currentText()

        # Add data to the table
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        self.table_widget.setItem(row_position, 0, QTableWidgetItem(hazard_category))
        self.table_widget.setItem(row_position, 1, QTableWidgetItem(hazard_source))
        self.table_widget.setItem(row_position, 2, QTableWidgetItem(hazardous_situation))
        self.table_widget.setItem(row_position, 3, QTableWidgetItem(harm_influenced))

        # Create a widget to hold the initial risk control action and the add button
        control_action_widget = QWidget()
        control_action_layout = QVBoxLayout(control_action_widget)

        # Add initial control action
        control_action_layout.addWidget(self.create_control_action_widget(risk_control_action))

        # Add button to add new control actions
        add_button = QPushButton("+")
        add_button.clicked.connect(lambda: self.add_new_control_action(control_action_layout, row_position))
        control_action_layout.addWidget(add_button)

        self.table_widget.setCellWidget(row_position, 4, control_action_widget)

        # Create a widget to hold the type of control combo box
        self.type_of_control_widget = QWidget()
        self.type_of_control_layout = QVBoxLayout(self.type_of_control_widget)


        # Add type of control combo box
        type_of_control_combo = QComboBox()
        type_of_control_combo.addItems(["  ", "Inherently safe design", "Protective measure", "Information for safety"])
        # add_button.clicked.connect(lambda: self.add_new_control_action(self.type_of_control_layout, row_position))


        type_of_control_combo.setCurrentText(control_type)
        self.type_of_control_layout.addWidget(type_of_control_combo)
        self.table_widget.setCellWidget(row_position, 5, self.type_of_control_widget)

        self.table_widget.setItem(row_position, 6, QTableWidgetItem(current_datetime))
        self.table_widget.setRowHeight(row_position, 200)
    def create_control_action_widget(self, text=""):
        control_action_widget = QWidget()
        layout = QHBoxLayout(control_action_widget)
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


        return control_action_widget

    def set_control_action_text(self, control_action_edit, layout, ok_button):
        text = control_action_edit.text()
        if text:
            # Create QLabel with the entered text
            control_action_label = QLabel(text)

            # Insert QLabel above the line edit
            layout.insertWidget(0, control_action_label)

            # Clear the text in the line edit
            control_action_edit.clear()
            control_action_edit.setVisible(False)  # Initially hide the line edit
            ok_button.setVisible(False)  # Initially hide the OK button

    def add_new_control_action(self, layout, row_position):
        # Add new control action line edit and OK button to the layout
        new_control_action_widget = self.create_control_action_widget()
        layout.insertWidget(layout.count() - 1, new_control_action_widget)  # Insert before the "+" button

        # Add a new combo box to the "Type of Control" column
        # type_of_control_combo = self.table_widget.cellWidget(row_position, 5)
        new_combo = QComboBox()
        new_combo.addItems(["  ", "Inherently safe design", "Protective measure", "Information for safety"])
        self.type_of_control_layout.addWidget(new_combo)
        self.table_widget.setCellWidget(row_position, 5, self.type_of_control_widget)

    def apply_stylesheet(self):
        stylesheet = """
        QToolTip
        {
             border: 1px solid black;
             background-color: #ffa02f;
             padding: 1px;
             border-radius: 3px;
             opacity: 100;
        }
        
        QWidget
        {
            color: #b1b1b1;
            background-color: #323232;
        }
        
        QTreeView, QListView
        {
            background-color: silver;
            margin-left: 5px;
        }
        
        QWidget:item:hover
        {
            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #ca0619);
            color: #000000;
        }
        
        QWidget:item:selected
        {
            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
        }
        
        

        QWidget:disabled
        {
            color: #808080;
            background-color: #323232;
        }
        
        QAbstractItemView
        {
            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4d4d4d, stop: 0.1 #646464, stop: 1 #5d5d5d);
        }
        
        QWidget:focus
        {
            /*border: 1px solid darkgray;*/
        }
        
        QLineEdit
        {
            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4d4d4d, stop: 0 #646464, stop: 1 #5d5d5d);
            padding: 1px;
            height: 30px;
            border-style: solid;
            border: 1px solid #1e1e1e;
            border-radius: 5;
            font-size: 18px;
        }
        
        QPushButton
        {
            color: #b1b1b1;
            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);
            border-width: 1px;
            height: 20px;
            border-color: #1e1e1e;
            border-style: solid;
            border-radius: 6;
            padding: 3px;
            font-size: 15px;
            padding-left: 5px;
            padding-right: 5px;
            min-width: 40px;
        }
        
        QPushButton:pressed
        {
            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2d2d2d, stop: 0.1 #2b2b2b, stop: 0.5 #292929, stop: 0.9 #282828, stop: 1 #252525);
        }
        
        QComboBox
        {
            selection-background-color: #ffaa00;
            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);
            border-style: solid;
            height: 30px;
            width: 150px;
            border: 1px solid #1e1e1e;
            border-radius: 5;
        }
        
        QComboBox:hover,QPushButton:hover
        {
            border: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
        }
        
        
        QComboBox:on
        {
            padding-top: 3px;
            padding-left: 4px;
            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2d2d2d, stop: 0.1 #2b2b2b, stop: 0.5 #292929, stop: 0.9 #282828, stop: 1 #252525);
            selection-background-color: #ffaa00;
        }
        
        QComboBox QAbstractItemView
        {
            border: 2px solid darkgray;
            selection-background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
        }
        
        QComboBox::drop-down
        {
             subcontrol-origin: padding;
             subcontrol-position: top right;
             width: 15px;
        
             border-left-width: 0px;
             border-left-color: darkgray;
             border-left-style: solid; /* just a single line */
             border-top-right-radius: 3px; /* same radius as the QComboBox */
             border-bottom-right-radius: 3px;
         }
        
        QComboBox::down-arrow
        {
        
             image: url(:/qss_icons/DarkOrange/down_arrow.png);
        }
        
        QGroupBox
        {
            border: 1px solid darkgray;
            margin-top: 10px;
        }
        
        QGroupBox:focus
        {
            border: 1px solid darkgray;
        }
        
        QTextEdit:focus
        {
            border: 1px solid darkgray;
        }
        
        QScrollBar:horizontal {
             border: 1px solid #222222;
             background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.0 #121212, stop: 0.2 #282828, stop: 1 #484848);
             height: 7px;
             margin: 0px 16px 0 16px;
        }
        
        QScrollBar::handle:horizontal
        {
              background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ffa02f, stop: 0.5 #d7801a, stop: 1 #ffa02f);
              min-height: 20px;
              border-radius: 2px;
        }
        
        QScrollBar::add-line:horizontal {
              border: 1px solid #1b1b19;
              border-radius: 2px;
              background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ffa02f, stop: 1 #d7801a);
              width: 14px;
              subcontrol-position: right;
              subcontrol-origin: margin;
        }
        
        QScrollBar::sub-line:horizontal {
              border: 1px solid #1b1b19;
              border-radius: 2px;
              background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ffa02f, stop: 1 #d7801a);
              width: 14px;
             subcontrol-position: left;
             subcontrol-origin: margin;
        }
        
        QScrollBar::right-arrow:horizontal, QScrollBar::left-arrow:horizontal
        {
              border: 1px solid black;
              width: 1px;
              height: 1px;
              background: white;
        }
        
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
        {
              background: none;
        }
        
        QScrollBar:vertical
        {
              background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0.0 #121212, stop: 0.2 #282828, stop: 1 #484848);
              width: 7px;
              margin: 16px 0 16px 0;
              border: 1px solid #222222;
        }
        
        QScrollBar::handle:vertical
        {
              background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 0.5 #d7801a, stop: 1 #ffa02f);
              min-height: 20px;
              border-radius: 2px;
        }
        
        QScrollBar::add-line:vertical
        {
              border: 1px solid #1b1b19;
              border-radius: 2px;
              background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
              height: 14px;
              subcontrol-position: bottom;
              subcontrol-origin: margin;
        }
        
        QScrollBar::sub-line:vertical
        {
              border: 1px solid #1b1b19;
              border-radius: 2px;
              background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #d7801a, stop: 1 #ffa02f);
              height: 14px;
              subcontrol-position: top;
              subcontrol-origin: margin;
        }
        
        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical
        {
              border: 1px solid black;
              width: 1px;
              height: 1px;
              background: white;
        }
        
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
        {
              background: none;
        }
        
        QTextEdit
        {
            background-color: #242424;
        }
        
        QPlainTextEdit
        {
            background-color: #242424;
        }
        
        QHeaderView::section
        {
            background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #616161, stop: 0.5 #505050, stop: 0.6 #434343, stop:1 #656565);
            color: white;
            padding-left: 4px;
            border: 1px solid #6c6c6c;
        }
        
        QCheckBox:disabled
        {
        color: #414141;
        }
        
        QDockWidget::title
        {
            text-align: center;
            spacing: 3px; /* spacing between items in the tool bar */
            background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop: 0.5 #242424, stop:1 #323232);
        }
        
        QDockWidget::close-button, QDockWidget::float-button
        {
            text-align: center;
            spacing: 1px; /* spacing between items in the tool bar */
            background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop: 0.5 #242424, stop:1 #323232);
        }
        
        QDockWidget::close-button:hover, QDockWidget::float-button:hover
        {
            background: #242424;
        }
        
        QDockWidget::close-button:pressed, QDockWidget::float-button:pressed
        {
            padding: 1px -1px -1px 1px;
        }
        
        QMainWindow::separator
        {
            background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161616, stop: 0.5 #151515, stop: 0.6 #212121, stop:1 #343434);
            color: white;
            padding-left: 4px;
            border: 1px solid #4c4c4c;
            spacing: 3px; /* spacing between items in the tool bar */
        }
        
        QMainWindow::separator:hover
        {
        
            background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d7801a, stop:0.5 #b56c17 stop:1 #ffa02f);
            color: white;
            padding-left: 4px;
            border: 1px solid #6c6c6c;
            spacing: 3px; /* spacing between items in the tool bar */
        }
        
        QToolBar::handle
        {
             spacing: 3px; /* spacing between items in the tool bar */
             background: url(:/qss_icons/DarkOrange/handle.png);
        }
        
        QMenu::separator
        {
            height: 2px;
            background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161616, stop: 0.5 #151515, stop: 0.6 #212121, stop:1 #343434);
            color: white;
            padding-left: 4px;
            margin-left: 10px;
            margin-right: 5px;
        }
        
        QProgressBar
        {
            border: 2px solid grey;
            border-radius: 5px;
            text-align: center;
        }
        
        QProgressBar::chunk
        {
            background-color: #d7801a;
            width: 2.15px;
            margin: 0.5px;
        }
        
        QTabBar::tab {
            color: #b1b1b1;
            border: 1px solid #444;
            border-bottom-style: none;
            background-color: #323232;
            padding-left: 10px;
            padding-right: 10px;
            padding-top: 3px;
            padding-bottom: 2px;
            margin-right: -1px;
        }
        
        QTabWidget::pane {
            border: 1px solid #444;
            top: 1px;
        }
        
        QTabBar::tab:last
        {
            margin-right: 0; /* the last selected tab has nothing to overlap with on the right */
            border-top-right-radius: 3px;
        }
        
        QTabBar::tab:first:!selected
        {
         margin-left: 0px; /* the last selected tab has nothing to overlap with on the right */
        
        
            border-top-left-radius: 3px;
        }
        
        QTabBar::tab:!selected
        {
            color: #b1b1b1;
            border-bottom-style: solid;
            margin-top: 3px;
            background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:1 #212121, stop:.4 #343434);
        }
        
        QTabBar::tab:selected
        {
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
            margin-bottom: 0px;
        }
        
        QTabBar::tab:!selected:hover
        {
            /*border-top: 2px solid #ffaa00;
            padding-bottom: 3px;*/
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
            background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:1 #212121, stop:0.4 #343434, stop:0.2 #343434, stop:0.1 #ffaa00);
        }
        
        QRadioButton::indicator:checked, QRadioButton::indicator:unchecked{
            color: #b1b1b1;
            background-color: #323232;
            border: 1px solid #b1b1b1;
            border-radius: 6px;
        }
        
        QRadioButton::indicator:checked
        {
            background-color: qradialgradient(
                cx: 0.5, cy: 0.5,
                fx: 0.5, fy: 0.5,
                radius: 1.0,
                stop: 0.25 #ffaa00,
                stop: 0.3 #323232
            );
        }
        
        QCheckBox::indicator{
            color: #b1b1b1;
            background-color: #323232;
            border: 1px solid #b1b1b1;
            width: 9px;
            height: 9px;
        }
        
        QRadioButton::indicator
        {
            border-radius: 6px;
        }
        
        QRadioButton::indicator:hover, QCheckBox::indicator:hover
        {
            border: 1px solid #ffaa00;
        }
        
        QCheckBox::indicator:checked
        {
            image:url(:/qss_icons/DarkOrange/checkbox.png);
        }
        
        QCheckBox::indicator:disabled, QRadioButton::indicator:disabled
        {
            border: 1px solid #444;
        }
        
        
        QSlider::groove:horizontal {
            border: 1px solid #3A3939;
            height: 8px;
            background: #201F1F;
            margin: 2px 0;
            border-radius: 2px;
        }
        
        QSlider::handle:horizontal {
            background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1,
              stop: 0.0 silver, stop: 0.2 #a8a8a8, stop: 1 #727272);
            border: 1px solid #3A3939;
            width: 14px;
            height: 14px;
            margin: -4px 0;
            border-radius: 2px;
        }
        
        QSlider::groove:vertical {
            border: 1px solid #3A3939;
            width: 8px;
            background: #201F1F;
            margin: 0 0px;
            border-radius: 2px;
        }
        
        QSlider::handle:vertical {
            background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.0 silver,
              stop: 0.2 #a8a8a8, stop: 1 #727272);
            border: 1px solid #3A3939;
            width: 14px;
            height: 14px;
            margin: 0 -4px;
            border-radius: 2px;
        }
        
        QAbstractSpinBox {
            padding-top: 2px;
            padding-bottom: 2px;
            border: 1px solid darkgray;
        
            border-radius: 2px;
            min-width: 50px;
        }
        
        

        """
        self.setStyleSheet(stylesheet)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = HazardManager()
    sys.exit(app.exec_())
