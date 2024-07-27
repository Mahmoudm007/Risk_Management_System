import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, \
    QTableWidget, QTableWidgetItem, QWidget, QDialog, QDialogButtonBox, QAbstractItemView, QLabel, QHBoxLayout


class DeviceSelected(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Tree View with Checkboxes Example')
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(['Devices'])
        self.populate_tree()

        self.layout.addWidget(self.tree)

        self.add_button = QPushButton('Save devices settings')
        self.add_button.clicked.connect(self.add_checked_items)
        self.layout.addWidget(self.add_button)

        self.checked_items = []

    def populate_tree(self):
        all_devices = QTreeWidgetItem(self.tree, ['All Devices'])
        all_devices.setCheckState(0, 0)

        ezvent = QTreeWidgetItem(all_devices, ['EzVent'])
        ezvent.setCheckState(0, 0)

        QTreeWidgetItem(ezvent, ['EzVent 101']).setCheckState(0, 0)
        QTreeWidgetItem(ezvent, ['EzVent 202']).setCheckState(0, 0)
        QTreeWidgetItem(ezvent, ['EzVent 201']).setCheckState(0, 0)

        QTreeWidgetItem(all_devices, ['SleepEZ']).setCheckState(0, 0)
        QTreeWidgetItem(all_devices, ['Syringe pump']).setCheckState(0, 0)
        QTreeWidgetItem(all_devices, ['Oxygen concentrator']).setCheckState(0, 0)

    def add_checked_items(self):
        self.checked_items = self.get_checked_items(self.tree.invisibleRootItem())
        self.accept()

    def get_checked_items(self, item):
        checked_items = []
        if item.checkState(0) == 2:
            checked_items.append(item.text(0))

        for i in range(item.childCount()):
            checked_items.extend(self.get_checked_items(item.child(i)))

        return checked_items
