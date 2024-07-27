import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView

class WebEngineApp(QDialog):
    def __init__(self):
        super().__init__()

        self.init_sunburst_chart()

    def init_sunburst_chart(self):
        # Set up the main layout
        self.layout = QVBoxLayout()

        # Create a QWebEngineView widget
        self.webEngineView = QWebEngineView()

        # Create combo boxes for selecting data keys
        self.comboBox1 = QComboBox()
        self.comboBox2 = QComboBox()
        self.comboBox1.addItems(['Department', 'Lifecycle', 'Status'])
        self.comboBox2.addItems(['Department', 'Lifecycle', 'Status'])

        # Create a horizontal layout for the combo boxes
        comboLayout = QHBoxLayout()
        comboLayout.addWidget(self.comboBox1)
        comboLayout.addWidget(self.comboBox2)

        # Create a button to display the Plotly chart
        self.showButton = QPushButton('Show Plotly Chart')
        self.showButton.clicked.connect(self.display_plotly_chart)

        # Add the combo boxes, button, and the web view to the layout
        self.layout.addLayout(comboLayout)
        self.layout.addWidget(self.showButton)
        self.layout.addWidget(self.webEngineView)

        # Set the layout for the main window
        self.setLayout(self.layout)

        # Set the main window properties
        self.setWindowTitle('QWebEngineView with Plotly Chart')
        self.setGeometry(100, 100, 800, 800)

    def display_plotly_chart(self):
        # Generate the Plotly chart as HTML
        html = self.generate_plotly_chart()

        # Load the HTML into the QWebEngineView
        self.webEngineView.setHtml(html)

    def generate_plotly_chart(self):
        # Sample data for change requests
        data = {
            'Department': np.random.choice(['Software', 'Electrical', 'Mechanical'], size=100),
            'Lifecycle': np.random.choice(['Concept', 'Design', 'Production', 'Post-Production', 'Validation', 'Verification', 'Storage'], size=100),
            'Status': np.random.choice(['Pending', 'Approved', 'Rejected'], size=100)
        }

        # Create a DataFrame
        df = pd.DataFrame(data)

        # Get the selected keys from the combo boxes
        key1 = self.comboBox1.currentText()
        key2 = self.comboBox2.currentText()

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
            plot_bgcolor='white'    # Set the background color of the plot area
        )

        # Generate the HTML representation of the Plotly chart
        html = fig.to_html(include_plotlyjs='cdn')

        return html

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WebEngineApp()
    ex.show()
    sys.exit(app.exec_())
