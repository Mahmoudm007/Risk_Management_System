from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QLineEdit


class SortableTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        if isinstance(other, QTableWidgetItem):
            column = self.column()
            if column == 7 or column == 10:
                widget1 = self.tableWidget().cellWidget(self.row(), column)
                widget2 = self.tableWidget().cellWidget(other.row(), column)
                if isinstance(widget1, QWidget) and isinstance(widget2, QWidget):
                    if column == 7:
                        return widget1.findChild(QLineEdit).text() < widget2.findChild(QLineEdit).text()
                    elif column == 10:
                        return widget1.findChild(QLineEdit).text() < widget2.findChild(QLineEdit).text()
            return QTableWidgetItem.__lt__(self, other)

        return super(SortableTableWidgetItem, self).__lt__(other)
