import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QAction, QDirModel, QStyle, QToolBar
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtCore import Qt
from appUI import *


class MyMainWindow(QMainWindow, Ui_MainWindow):

    file_path = ''

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.setupUi(self)

        # Set Window Icon
        self.setWindowIcon(QApplication.style().standardIcon(QStyle.SP_TitleBarMenuButton))
        # MainWindow Title
        self.setWindowTitle('QIcon Test!!')
        # StatusBar
        self.statusBar().showMessage('TEST Again!!!')

        #   Actions
        action_open_folder = self.actionOpen_Folder
        action_open_folder.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogOpenButton))
        action_open_folder.triggered.connect(self.open_file)
        action_open_folder.setShortcut(QKeySequence.Open)

        # toolbar
        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)
        # disable context menu on toolbar to prevent users from hiding toolbar
        toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        toolbar.addAction(action_open_folder)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

    def update_tree_view(self, p):
        # TREE VIEW
        file_tree_view = self.treeView
        model = QDirModel()
        file_tree_view.setModel(model)
        file_tree_view.setRootIndex(model.index(p))
        file_tree_view.show()

    def open_file(self):
        path = QFileDialog.getExistingDirectory(self, "Open")
        if path:
            file_path = path
            self.update_tree_view(file_path)
            print('path=', file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
