from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTreeWidgetItem, QTreeWidget, QPushButton, QComboBox, QLineEdit, QHBoxLayout, QVBoxLayout, \
    QWidget, QDialogButtonBox, QFormLayout, QDialog, QApplication, QMainWindow
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import *
# from qtpy import QtWidgets
from search import *

class AddSubSystemReqClass(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add Child')
        self.setGeometry(100, 100, 300, 150)

        self.layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.child_name_line_edit = QLineEdit()
        form_layout.addRow('Requirement:', self.child_name_line_edit)

        self.combo_box = QComboBox()
        self.combo_box.addItems(['Software', 'Electrical', 'Mechanical', 'Usability', 'Testing'])
        form_layout.addRow('Select Type:', self.combo_box)

        self.layout.addLayout(form_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_child_info(self):
        return self.child_name_line_edit.text(), self.combo_box.currentText()


class AddControlClass(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.control_list_widget = QtWidgets.QListWidget()


        # Horizontal layout for parent text input and type selection
        self.horizontal_layout = QHBoxLayout()

        self.parent_text_line_edit = QLineEdit()
        self.parent_text_line_edit.setPlaceholderText('Enter risk control text..')
        self.horizontal_layout.addWidget(self.parent_text_line_edit)


        self.combo_box = QComboBox()
        self.combo_box.addItems(['Inherently safe design', 'Protective measure', 'information for safety'])
        self.horizontal_layout.addWidget(self.combo_box)

        self.control_list_widget.hide()

        self.parent_text_line_edit.textChanged.connect(self.update_control_ver_layout)
        self.control_list_widget.itemDoubleClicked.connect(self.add_to_risk_control_action_edit)


        self.layout.addLayout(self.horizontal_layout)

        self.layout.addWidget(self.control_list_widget)
        # Add parent button
        self.add_parent_button = QPushButton('Add control')
        self.layout.addWidget(self.add_parent_button)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(['Control', 'Type'])

        self.tree.itemDoubleClicked.connect(self.add_child_or_edit_type)

        self.layout.addWidget(self.tree)

        self.add_parent_button.clicked.connect(self.add_parent)

    def update_control_ver_layout(self):
        line_edit_type = "control"
        self.control_list_widget.show()
        text = self.parent_text_line_edit.text()
        self.update_layout_of_control_tree(self.parent_text_line_edit,self.control_list_widget, line_edit_type)

    def add_to_risk_control_action_edit(self, item):
        self.parent_text_line_edit.setText(item.text())
        parent_text = self.parent_text_line_edit.text()
        if parent_text:
            item = QTreeWidgetItem([parent_text, self.combo_box.currentText()])
            self.tree.addTopLevelItem(item)
            self.parent_text_line_edit.clear()
        self.control_list_widget.hide()

    def update_layout_of_control_tree(self, line_edit, list_widget, line_edit_type):
        search_terms = line_edit.text()
        if not search_terms:
            list_widget.clear()
            return

        if line_edit_type == "control":
            results = search_documents(search_terms, control_inverted_index, control_documents)
            highlighted_results = rank_and_highlight(results, search_terms, control_documents, scores)

        list_widget.clear()
        if not highlighted_results:
            list_widget.addItem("No results found")
        else:
            for doc_id, content, score in highlighted_results:
                list_widget.addItem(f"ID: {doc_id} \n{content}")

    def add_parent(self):
        parent_text = self.parent_text_line_edit.text()
        if parent_text:
            item = QTreeWidgetItem([parent_text, self.combo_box.currentText()])
            self.tree.addTopLevelItem(item)
            self.parent_text_line_edit.clear()

    def add_child_or_edit_type(self, item, column):
        if column == 1:
            dialog = AddSubSystemReqClass(self)
            if dialog.exec_():
                item.setText(1, dialog.get_child_info()[1])
        else:
            dialog = AddSubSystemReqClass(self)
            if dialog.exec_():
                child_text, child_type = dialog.get_child_info()
                child = QTreeWidgetItem([child_text, child_type])
                item.addChild(child)
                item.setExpanded(True)

