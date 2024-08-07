import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, \
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog
from PyQt5.QtCore import QDateTime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import Counter

class HazardManager(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setGeometry(100, 100, 700, 500)

    def initUI(self):
        self.apply_styles()
        # Layouts
        main_layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        # Name input
        self.name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        form_layout.addWidget(self.name_label)
        form_layout.addWidget(self.name_edit)

        # Hazard input
        self.hazard_label = QLabel("Hazard:")
        self.hazard_edit = QLineEdit()
        form_layout.addWidget(self.hazard_label)
        form_layout.addWidget(self.hazard_edit)

        # Priority selection
        self.priority_label = QLabel("Priority:")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["High", "Medium", "Low"])
        form_layout.addWidget(self.priority_label)
        form_layout.addWidget(self.priority_combo)

        # Add button
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_entry)
        button_layout.addWidget(self.add_button)

        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Hazard", "Priority", "Date"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Add layouts to main layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table_widget)

        # Button to display charts
        self.show_charts_button = QPushButton("Show Charts")
        self.show_charts_button.clicked.connect(self.show_charts)
        main_layout.addWidget(self.show_charts_button)

        self.setLayout(main_layout)
        self.setWindowTitle('Hazard Manager')
        self.show()

    def add_entry(self):
        # Get current date and time
        current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

        # Get inputs
        name = self.name_edit.text()
        hazard = self.hazard_edit.text()
        priority = self.priority_combo.currentText()

        # Add data to the table
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        self.table_widget.setItem(row_position, 0, QTableWidgetItem(name))
        self.table_widget.setItem(row_position, 1, QTableWidgetItem(hazard))
        self.table_widget.setItem(row_position, 2, QTableWidgetItem(priority))
        self.table_widget.setItem(row_position, 3, QTableWidgetItem(current_datetime))

        # Sort the table by priority
        self.sort_table()

    def sort_table(self):
        priorities = {"High": 0, "Medium": 1, "Low": 2}
        row_count = self.table_widget.rowCount()

        data = []
        for row in range(row_count):
            name = self.table_widget.item(row, 0).text()
            hazard = self.table_widget.item(row, 1).text()
            priority = self.table_widget.item(row, 2).text()
            date = self.table_widget.item(row, 3).text()
            data.append((name, hazard, priority, date))

        data.sort(key=lambda x: priorities[x[2]])

        self.table_widget.setRowCount(0)
        for row_data in data:
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            for col, item in enumerate(row_data):
                self.table_widget.setItem(row_position, col, QTableWidgetItem(item))

    def show_charts(self):
        row_count = self.table_widget.rowCount()
        hazards = []
        priorities = []

        for row in range(row_count):
            hazards.append(self.table_widget.item(row, 1).text())
            priorities.append(self.table_widget.item(row, 2).text())

        # Plot most frequent hazards
        hazard_counts = Counter(hazards)
        sorted_hazard_counts = sorted(hazard_counts.items(), key=lambda x: x[1], reverse=True)
        hazard_labels, hazard_values = zip(*sorted_hazard_counts)

        # Create hazard figure
        fig_hazard = Figure()
        canvas_hazard = FigureCanvas(fig_hazard)
        ax_hazard = fig_hazard.add_subplot(111)
        bars = ax_hazard.barh(hazard_labels, hazard_values)
        ax_hazard.set_xlabel('Frequency')
        ax_hazard.set_title('Most Frequent Hazards')
        ax_hazard.invert_yaxis()  # Most frequent on top

        # Annotate bars with counts
        for bar in bars:
            ax_hazard.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2, int(bar.get_width()), va='center')

        # Plot priority counts
        priority_counts = Counter(priorities)
        priority_labels, priority_values = zip(*priority_counts.items())

        # Create priority figure
        fig_priority = Figure()
        canvas_priority = FigureCanvas(fig_priority)
        ax_priority = fig_priority.add_subplot(111)
        bars_priority = ax_priority.bar(priority_labels, priority_values, color=['red', 'orange', 'green'])
        ax_priority.set_xlabel('Priority')
        ax_priority.set_ylabel('Number of Requests')
        ax_priority.set_title('Number of Requests by Priority')

        # Annotate bars with counts
        for bar in bars_priority:
            ax_priority.text(bar.get_x() + bar.get_width() / 2 - 0.1, bar.get_height() + 0.1, int(bar.get_height()), ha='center')

        # Display charts in a new dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Charts")
        layout = QVBoxLayout(dialog)
        layout.addWidget(canvas_hazard)
        layout.addWidget(canvas_priority)
        dialog.setLayout(layout)
        dialog.resize(1300, 1000)
        dialog.exec_()

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = HazardManager()
    sys.exit(app.exec_())
