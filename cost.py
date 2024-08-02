import sys
import pandas as pd
import numpy as np
from IPython.external.qt_for_kernel import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, \
    QPushButton, QWidget, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor


class BudgetApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize data
        self.df, self.material_encoder, self.elasticity_encoder, self.color_encoder, self.connection_encoder, self.model = self.initialize_data()
        self.components = self.df.to_dict('records')
        self.current_budget = self.calculate_overall_budget(self.components)

        # Set up UI
        self.setWindowTitle('Medical Device Component Budget Calculator')
        self.setGeometry(100, 100, 1000, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.Hlayout = QHBoxLayout(self.central_widget)

        self.layout = QVBoxLayout()
        self.budget_label = QLabel(f"Current Budget: ${self.current_budget:.2f}", self)
        self.budget_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.budget_label)

        self.combo_layout = QHBoxLayout()
        self.layout.addLayout(self.combo_layout)

        self.component_combo = QComboBox(self)
        self.component_combo.addItems([f"Component {i + 1}" for i in range(len(self.components))])
        self.component_combo.currentIndexChanged.connect(self.display_component_details)

        self.component_details_label = QLabel("Select a component to see details.", self)
        self.combo_layout.addWidget(self.component_details_label)
        self.combo_layout.addWidget(self.component_combo)

        # Layout for displaying old component labels
        self.old_component_labels_layout = QVBoxLayout()
        self.layout.addLayout(self.old_component_labels_layout)
        self.old_labels = {
            'Length': QLabel("Length: ", self),
            'Width': QLabel("Width: ", self),
            'Height': QLabel("Height: ", self),
            'Edges': QLabel("Edges: ", self),
            'Colors': QLabel("Colors: ", self),
            'Material': QLabel("Material: ", self),
            'Elasticity': QLabel("Elasticity: ", self),
            'Connection': QLabel("Connection: ", self),
        }
        for label in self.old_labels.values():
            self.old_component_labels_layout.addWidget(label)

        # Layout for new component inputs and labels
        self.new_component_layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.new_component_layout)
        self.layout.addLayout(self.buttons_layout)
        self.Hlayout.addLayout(self.layout)

        # Add new component input fields
        self.length_input = QLineEdit(self)
        self.length_input.setPlaceholderText("Length (mm)")
        self.new_component_layout.addWidget(self.length_input)

        self.width_input = QLineEdit(self)
        self.width_input.setPlaceholderText("Width (mm)")
        self.new_component_layout.addWidget(self.width_input)

        self.height_input = QLineEdit(self)
        self.height_input.setPlaceholderText("Height (mm)")
        self.new_component_layout.addWidget(self.height_input)

        self.edges_input = QLineEdit(self)
        self.edges_input.setPlaceholderText("Edges")
        self.new_component_layout.addWidget(self.edges_input)

        self.colors_input = QLineEdit(self)
        self.colors_input.setPlaceholderText("Colors (Red, Green, Blue, Black, White)")
        self.new_component_layout.addWidget(self.colors_input)

        self.material_input = QLineEdit(self)
        self.material_input.setPlaceholderText("Material (Plastic, Metal, Ceramic, Composite)")
        self.new_component_layout.addWidget(self.material_input)

        self.elasticity_input = QLineEdit(self)
        self.elasticity_input.setPlaceholderText("Elasticity (Low, Medium, High)")
        self.new_component_layout.addWidget(self.elasticity_input)

        self.connection_input = QLineEdit(self)
        self.connection_input.setPlaceholderText("Connection (Wired, Wireless)")
        self.new_component_layout.addWidget(self.connection_input)


        # New component button and prediction button
        self.update_button = QPushButton("Update Component", self)
        self.update_button.clicked.connect(self.update_component)
        self.buttons_layout.addWidget(self.update_button)

        self.predict_button = QPushButton("Predict Cost", self)
        self.predict_button.clicked.connect(self.predict_cost_display)
        self.buttons_layout.addWidget(self.predict_button)

        self.load_button = QPushButton("Load New Component Data", self)
        self.load_button.clicked.connect(self.load_new_data)
        self.buttons_layout.addWidget(self.load_button)

        self.save_button = QPushButton("Save Data", self)
        self.save_button.clicked.connect(self.save_data)
        self.buttons_layout.addWidget(self.save_button)


        # Horizontal layout for web view and URL input
        self.web_layout = QVBoxLayout()
        self.Hlayout.addLayout(self.web_layout)

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter URL")
        self.web_layout.addWidget(self.url_input)

        self.update_url_button = QPushButton("Update URL", self)
        self.update_url_button.clicked.connect(self.update_url)
        self.web_layout.addWidget(self.update_url_button)

        self.web_view = QWebEngineView()
        self.web_layout.addWidget(self.web_view)
        self.web_view.setUrl(QtCore.QUrl("file:///D:/data-sheets-safety-valve-sapag-en-en-5195230.html"))  # Change to your desired URL

        self.display_component_details(0)
        self.apply_styles()


    def initialize_data(self):
        np.random.seed(0)
        data = {
            'Component': ['Comp' + str(i) for i in range(1, 101)],
            'Length': np.random.uniform(5, 200, 100),
            'Width': np.random.uniform(5, 200, 100),
            'Height': np.random.uniform(5, 200, 100),
            'Edges': np.random.randint(0, 6, 100),
            'Colors': np.random.choice(['Red', 'Green', 'Blue', 'Black', 'White'], 100),
            'Material': np.random.choice(['Plastic', 'Metal', 'Ceramic', 'Composite'], 100),
            'Elasticity': np.random.choice(['Low', 'Medium', 'High'], 100),
            'Connection': np.random.choice(['Wired', 'Wireless'], 100),
            'Cost (USD)': np.random.uniform(5, 1000, 100)
        }
        df = pd.DataFrame(data)
        df.to_csv('component_data.csv', index=False)

        # Initialize LabelEncoders
        material_encoder = LabelEncoder()
        elasticity_encoder = LabelEncoder()
        connection_encoder = LabelEncoder()
        color_encoder = LabelEncoder()

        df['Material'] = material_encoder.fit_transform(df['Material'])
        df['Elasticity'] = elasticity_encoder.fit_transform(df['Elasticity'])
        df['Connection'] = connection_encoder.fit_transform(df['Connection'])
        df['Colors'] = color_encoder.fit_transform(df['Colors'])

        X = df[['Length', 'Width', 'Height', 'Edges', 'Colors', 'Material', 'Elasticity', 'Connection']]
        y = df['Cost (USD)']

        model = RandomForestRegressor(n_estimators=100, random_state=0)
        model.fit(X, y)

        return df, material_encoder, elasticity_encoder, color_encoder, connection_encoder, model

    def display_component_details(self, index):
        component = self.components[index]
        details = f"Length: {component['Length']} mm, Width: {component['Width']} mm, Height: {component['Height']} mm, " \
                  f"Edges: {component['Edges']}, Colors: {component['Colors']}, Material: {component['Material']}, " \
                  f"Elasticity: {component['Elasticity']}, Connection: {component['Connection']}, Cost: ${component['Cost (USD)']:.2f}"

        # Update old component labels
        old_component = self.components[index]
        self.old_labels['Length'].setText(f"Length: {old_component['Length']} mm")
        self.old_labels['Width'].setText(f"Width: {old_component['Width']} mm")
        self.old_labels['Height'].setText(f"Height: {old_component['Height']} mm")
        self.old_labels['Edges'].setText(f"Edges: {old_component['Edges']}")
        self.old_labels['Colors'].setText(f"Colors: {old_component['Colors']}")
        self.old_labels['Material'].setText(f"Material: {old_component['Material']}")
        self.old_labels['Elasticity'].setText(f"Elasticity: {old_component['Elasticity']}")
        self.old_labels['Connection'].setText(f"Connection: {old_component['Connection']}")

    def predict_cost_display(self):
        try:
            length = float(self.length_input.text().strip())
            width = float(self.width_input.text().strip())
            height = float(self.height_input.text().strip())
            edges = int(self.edges_input.text().strip())
            colors = self.colors_input.text().strip()
            material = self.material_input.text().strip()
            elasticity = self.elasticity_input.text().strip()
            connection = self.connection_input.text().strip()

            predicted_cost = self.predict_cost(length, width, height, edges, colors, material, elasticity, connection)
            self.component_details_label.setText(f"Predicted Cost: ${predicted_cost:.2f}")
        except ValueError:
            self.component_details_label.setText("Please enter valid inputs for prediction.")

    def predict_cost(self, length, width, height, edges, colors, material, elasticity, connection):
        # Transform categorical inputs to numeric
        colors_encoded = self.color_encoder.transform([colors])[0]
        material_encoded = self.material_encoder.transform([material])[0]
        elasticity_encoded = self.elasticity_encoder.transform([elasticity])[0]
        connection_encoded = self.connection_encoder.transform([connection])[0]

        # Create feature array
        features = np.array([[length, width, height, edges, colors_encoded, material_encoded, elasticity_encoded, connection_encoded]])
        print(features)
        # Predict cost
        predicted_cost = self.model.predict(features)
        return predicted_cost[0]

    def update_component(self):
        index = self.component_combo.currentIndex()
        try:
            length = float(self.length_input.text().strip())
            width = float(self.width_input.text().strip())
            height = float(self.height_input.text().strip())
            edges = int(self.edges_input.text().strip())
            colors = self.colors_input.text().strip()
            material = self.material_input.text().strip()
            elasticity = self.elasticity_input.text().strip()
            connection = self.connection_input.text().strip()

            self.df.at[index, 'Length'] = length
            self.df.at[index, 'Width'] = width
            self.df.at[index, 'Height'] = height
            self.df.at[index, 'Edges'] = edges
            self.df.at[index, 'Colors'] = colors
            self.df.at[index, 'Material'] = material
            self.df.at[index, 'Elasticity'] = elasticity
            self.df.at[index, 'Connection'] = connection

            self.df.to_csv('component_data.csv', index=False)
            self.current_budget = self.calculate_overall_budget(self.df.to_dict('records'))
            self.budget_label.setText(f"Current Budget: ${self.current_budget:.2f}")
            self.display_component_details(index)
        except ValueError:
            self.component_details_label.setText("Please enter valid inputs to update component.")

    def load_new_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            new_df = pd.read_csv(file_name)
            self.df = pd.concat([self.df, new_df], ignore_index=True)
            self.df.to_csv('component_data.csv', index=False)
            self.components = self.df.to_dict('records')
            self.current_budget = self.calculate_overall_budget(self.components)
            self.budget_label.setText(f"Current Budget: ${self.current_budget:.2f}")
            self.component_combo.addItems([f"Component {i + 1}" for i in range(len(self.components) - len(new_df), len(self.components))])
            self.component_details_label.setText("New data loaded successfully!")

    def save_data(self):
        self.df.to_csv('component_data.csv', index=False)
        self.component_details_label.setText("Data saved successfully!")

    def calculate_overall_budget(self, components):
        return sum(component['Cost (USD)'] for component in components)

    def update_url(self):
        url = self.url_input.text().strip()
        if url:
            print(url)
            self.web_view.setUrl(QtCore.QUrl(url))

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
    window = BudgetApp()
    window.show()
    sys.exit(app.exec_())
