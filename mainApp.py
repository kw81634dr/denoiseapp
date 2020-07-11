import sys

#   Import Qt Libraries
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QAction, QDirModel, QStyle, QToolBar, qApp
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

#   Import app UI Module
from appUI import *

#   Import other Libraries
from pathlib import Path
import cv2
import pydicom


class MyMainWindow(QMainWindow, Ui_MainWindow):

    working_path = None

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.setupUi(self)

        self.setWindowIcon(QApplication.style().standardIcon(QStyle.SP_TitleBarMenuButton))
        self.setWindowTitle('KW De-noise App')
        self.statusBar().showMessage('Status Here')

        # Init ToolBar
        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)
        toolbar.setContextMenuPolicy(Qt.PreventContextMenu)  # prevent users from hiding toolbar
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        #   Actions
        action_open_folder = self.actionOpen_Folder
        action_open_folder.triggered.connect(self.open_file)
        action_exit_app = self.actionExit
        action_exit_app.triggered.connect(qApp.quit)    # terminate App
        toolbar.addAction(action_open_folder)

        # Set Icon
        action_open_folder.setIcon(QApplication.style().standardIcon(QStyle.SP_DirOpenIcon))

        # Set Short Cut
        action_open_folder.setShortcut(QKeySequence.Open)

        # Tree-view File browser
        self.model = QDirModel()
        self.treeView.doubleClicked.connect(self.get_selected_item_path)

    def update_tree_view(self, signal):
        # TREE VIEW
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index(signal))
        self.treeView.show()

    def open_file(self):
        p = QFileDialog.getExistingDirectory(self, "Open")
        if Path(p).is_dir():
            file_path = p
            self.update_tree_view(file_path)
            # print('path=', file_path)
        else:
            self.statusBar().showMessage('Please choose Folder.')

    def get_selected_item_path(self, signal):
        file_path = self.model.filePath(signal)
        print(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
