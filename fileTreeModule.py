from PyQt5.Qt import QStandardItem
from PyQt5.QtGui import QFont, QColor


class MyItem(QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0, 0, 0)):
        super().__init__()
        fnt = QFont('Arial', font_size)
        fnt.setBold(set_bold)
        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)


class DcmItem(QStandardItem):
    def __init__(self, font_size=10, set_bold=False, color=QColor(0, 0, 0)):
        super().__init__()
        fnt = QFont('Arial', font_size)
        fnt.setBold(set_bold)
        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)

