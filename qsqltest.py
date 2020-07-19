import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QHBoxLayout
from PyQt5.QtGui import QStandardItemModel,QStandardItem

class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = QStandardItemModel()
        self.treeView = QTreeView(self)
        self.treeView.setModel(self.model)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.treeView)
        self.setLayout(self.layout)

    # def initUI(self):
    #     root = self.model.invisibleRootItem()
    #     for i in range(4):
    #         item = QStandardItem(str(i))
    #         for j in range(3):
    #             chidItem1 = QStandardItem(str(j))
    #             item.setChild(j, chidItem1)
    #             for k in range(5):
    #                 chidItem2 = QStandardItem(str(k))
    #                 chidItem1.setChild(k, chidItem2)
    #                 for l in range(2):
    #                     chidItem3 = QStandardItem(str(l))
    #                     chidItem2.setChild(l, chidItem3)
    #         root.setChild(i, item)


 #        self.listToParse=[[('0965^^^^', '0965', 'Topogram  0.6  T80s', 'D:\\Users\\user\\Desktop\\NTUCT\\0965\\Ct_Without_ContrastBrain - 0965\\Localizers_602\\IM-0007-0001.dcm,D:\\Users\\user\\Desktop\\NTUCT\\0965\\Ct_Without_ContrastBrain - 0965\\Localizers_602\\IM-0007-0002.dcm,D:\\Users\\user\\Desktop\\NTUCT\\0965\\Ct_Without_ContrastBrain - 0965\\Localizers_602\\IM-0007-0003.dcm'),
 # ('0965^^^^', '0965', 'Patient Protocol', 'D:\\Users\\user\\Desktop\\NTUCT\\0965\\Ct_Without_ContrastBrain - 0965\\Patient_Protocol_501\\IM-0006-0000.dcm'),
 # ('0965^^^^', '0965', 'InnerEar  0.6  U70u', 'D:\\Users\\user\\Desktop\\NTUCT\\0965\\Ct_Without_ContrastBrain - 0965\\InnerEar_06_U70u_2\\IM-0005-0001.dcm,D:\\Users\\user\\Desktop\\NTUCT\\0965\\Ct_Without_ContrastBrain - 0965\\InnerEar_06_U70u_2\\IM-0005-0002.dcm)]]

    # def initUI(self):
    #     root = self.model.invisibleRootItem()
    #     for it in self.listToParse:
    #         for item in it:
    #     root.setChild(i, item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWidget()
    window.initUI()
    window.resize(400, 200)
    window.show()

    sys.exit(app.exec_())