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
