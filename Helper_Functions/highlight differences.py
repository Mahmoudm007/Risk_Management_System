import sys
import csv
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton,
                             QFileDialog)
from PyQt5.QtCore import Qt
from fpdf import FPDF


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Change Data Comparison")
        self.setGeometry(100, 100, 800, 400)

        self.labels_texts = ["Length", "Width", "Height", "Edges", "Color", "Material", "Elasticity", "Connection"]
        self.initial_data = ["10", "20", "30", "4", "Red", "Steel", "High", "Welded"]

        self.initUI()
        self.apply_styles()

    def apply_styles(self):
        # QSS Style Sheet
        style = """
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

        QLabel
        {
        font-size: 15px;
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
        self.setStyleSheet(style)

    def initUI(self):
        layout = QVBoxLayout()
        grid_layout = QGridLayout()

        self.labels = []
        self.inputs = []
        self.comparisons = []

        for i, text in enumerate(self.labels_texts):
            label = QLabel(text)
            label.setFixedHeight(30)
            grid_layout.addWidget(label, i, 0)

            initial_label = QLabel(self.initial_data[i])
            initial_label.setFixedHeight(30)
            grid_layout.addWidget(initial_label, i, 2)

            if text == "Color":
                input_field = QComboBox()
                input_field.addItems(["Red", "Blue", "Green", "Yellow", "Black", "White"])
                input_field.currentTextChanged.connect(lambda _, idx=i: self.compare_data(idx))
            elif text in ["Material", "Connection"]:
                input_field = QComboBox()
                input_field.addItems(["Steel", "Plastic"] if text == "Material" else ["Welded", "Bolted"])
                input_field.currentTextChanged.connect(lambda _, idx=i: self.compare_data(idx))
            else:
                input_field = QLineEdit()
                input_field.textChanged.connect(lambda _, idx=i: self.compare_data(idx))

            input_field.setFixedHeight(30)
            grid_layout.addWidget(input_field, i, 1)

            self.labels.append(label)
            self.inputs.append(input_field)
            self.comparisons.append(initial_label)

        button_import = QPushButton("Import CSV")
        button_import.setFixedHeight(40)
        button_import.clicked.connect(self.import_csv)

        button_generate = QPushButton("Generate PDF")
        button_generate.setFixedHeight(40)
        button_generate.clicked.connect(self.generate_pdf)

        layout.addLayout(grid_layout)
        layout.addWidget(button_import)
        layout.addWidget(button_generate)

        self.setLayout(layout)

    def compare_data(self, index):
        if isinstance(self.inputs[index], QLineEdit):
            new_data = self.inputs[index].text()
        elif isinstance(self.inputs[index], QComboBox):
            new_data = self.inputs[index].currentText()

        initial_data = self.comparisons[index].text()

        if new_data == initial_data:
            self.labels[index].setStyleSheet("")
        else:
            self.labels[index].setStyleSheet("color: red;")

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                data = list(reader)
                for i, text in enumerate(self.labels_texts):
                    if 1 < len(data) and i + 1 < len(data):  # Ensure there are enough rows in the CSV
                        new_value = data[i + 1][1]
                        if isinstance(self.inputs[i], QLineEdit):
                            self.inputs[i].setText(new_value)
                        elif isinstance(self.inputs[i], QComboBox):
                            index = self.inputs[i].findText(new_value, Qt.MatchFixedString)
                            if index >= 0:
                                self.inputs[i].setCurrentIndex(index)
                        self.compare_data(i)

    def generate_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Create table header
        pdf.cell(50, 10, "Attribute", 1)
        pdf.cell(70, 10, "Initial Data", 1)
        pdf.cell(70, 10, "New Data", 1)
        pdf.ln()

        for i, label in enumerate(self.labels):
            text = label.text()
            initial_data = self.comparisons[i].text()
            if isinstance(self.inputs[i], QLineEdit):
                new_data = self.inputs[i].text()
            elif isinstance(self.inputs[i], QComboBox):
                new_data = self.inputs[i].currentText()

            pdf.set_text_color(0, 0, 0)  # Ensure the attribute column is black
            pdf.cell(50, 10, text, 1)
            pdf.set_text_color(0, 0, 0)  # Ensure the attribute column is black
            pdf.cell(70, 10, initial_data, 1)

            # Highlight the new data in red if it has changed
            if label.styleSheet() == "color: red;":
                pdf.set_text_color(255, 0, 0)
            else:
                pdf.set_text_color(0, 0, 0)

            pdf.cell(70, 10, new_data, 1)
            pdf.ln()

        pdf.output("Change request.pdf")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
