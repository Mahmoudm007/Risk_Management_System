import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView

class WebEngineApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Set up the main layout
        self.layout = QVBoxLayout()

        # Create a QWebEngineView widget
        self.webEngineView = QWebEngineView()

        # Create a button to load the HTML file
        self.loadButton = QPushButton('Load HTML File')
        self.loadButton.clicked.connect(self.load_html_file)

        # Add the button and the web view to the layout
        self.layout.addWidget(self.loadButton)
        self.layout.addWidget(self.webEngineView)

        # Set the layout for the main window
        self.setLayout(self.layout)

        # Set the main window properties
        self.setWindowTitle('QWebEngineView Example')
        self.setGeometry(100, 100, 800, 600)

    def load_html_file(self):
        # Open a file dialog to select the HTML file
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open HTML File', '', 'HTML Files (*.html);;All Files (*)')

        if file_name:
            # Load the selected HTML file into the QWebEngineView
            self.webEngineView.setUrl(QUrl.fromLocalFile(file_name))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WebEngineApp()
    ex.show()
    sys.exit(app.exec_())
