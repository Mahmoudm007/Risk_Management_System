import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl


class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Simple Browser')
        self.setGeometry(100, 100, 1200, 800)

        # Create a QWebEngineView widget
        self.webview = QWebEngineView()

        # Set the URL to a simple web page
        self.webview.setUrl(QUrl("https://www.google.com"))

        # Set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.webview)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleBrowser()
    window.show()
    sys.exit(app.exec_())
