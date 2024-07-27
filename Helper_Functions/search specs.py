import sys
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
import fitz  # PyMuPDF
from docx import Document


class PDFTextExtractor(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.button = QPushButton('Browse PDF', self)
        self.button.clicked.connect(self.browse_pdf)

        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.setWindowTitle('PDF Text Extractor')
        self.setGeometry(100, 100, 300, 100)

    def browse_pdf(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_name:
            try:
                extracted_data = self.extract_text_from_pdf(file_name)
                self.save_text_to_word(extracted_data)
                QMessageBox.information(self, 'Success', 'Text extracted and saved to Word file successfully.')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'An error occurred: {e}')

    def extract_text_from_pdf(self, file_path):
        extracted_data = ""
        patterns = {
            "Sizes": re.compile(r'Sizes\s*:\s*([\d” D T]+)'),
            "Orifices": re.compile(r'Orifices\s*:\s*([\d\s]+)'),
            "Inlet Ratings": re.compile(r'Inlet Ratings\s*:\s*([\w\s,]+)'),
            "Temperature Range": re.compile(r'Minimume temp range\s*:\s*([\-+\d°C\s]+ )'),
            "Pressure Range": re.compile(r'Pressure Range\s*:\s*([\d.]+ to [\d.]+ barg)')
        }

        with fitz.open(file_path) as pdf_document:
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text = page.get_text()
                for key, pattern in patterns.items():
                    match = pattern.search(text)
                    if match:
                        extracted_data += f"{key}: {match.group(1)}\n"

        return extracted_data

    def save_text_to_word(self, text):
        doc = Document()
        doc.add_paragraph(text)
        doc.save("extracted_text.docx")

def main():
    app = QApplication(sys.argv)
    ex = PDFTextExtractor()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
