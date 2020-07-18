import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QAction, QDirModel, QStyle, QToolBar, qApp, \
    QDesktopWidget, QMessageBox, QFileSystemModel
from PyQt5.QtGui import QKeySequence, QFont, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.Qt import QStandardItemModel, QStandardItem
from appUI import *
from pathlib import Path
# Custom Module
from dcmModule import DcmViewCalibration, DcmDataBase
from dicomDirParserModule import DicomDirParser
from fileTreeModule import MyItem
import numpy as np
import cv2


# class PBarThreadClass(QThread):
#     sender = pyqtSignal(int)
#
#     def __int__(self):
#         super(PBarThreadClass, self).__init__()
#
#     def run(self):
#         cnt = 0
#         while cnt < 100:
#             cnt = cnt+1
#             time.sleep(0.3)
#             self.sender.emit(cnt)   # 迴圈完畢後發出訊號


def get_clicked_value(val):
    print(val.data())
    print(val.row())
    print(val.column())


class MyMainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        # Delegate Main Window
        self.ui = Ui_MainWindow()
        self.setupUi(self)
        self.setWindowIcon(QApplication.style().standardIcon(QStyle.SP_TitleBarMenuButton))
        self.setWindowTitle('KW De-noise App')
        self.statusBar().showMessage('Status Here')
        # #KW Custom UI Marco
        self.make_app_in_screen_center()
        self.init_toolbar()

        """TreeView"""
        # Tree-view model
        self.file_model = QFileSystemModel()
        # self.rootNode = QStandardItemModel()
        # self.rootNode.invisibleRootItem()
        data = [("Alice", [("Keys", []), ("Purse", [("Cellphone", [])])]), ("Bob", [("Wallet", [("Credit card", []), ("Money", [])])])]

        '---------------------------------------------'

        self.model = QStandardItemModel()
        self.addItems(self.model, data)
        self.treeView.setModel(self.model)
        self.model.setHorizontalHeaderLabels([self.tr("Object")])
        # Tree-view define
        # self.treeView.setHeaderHidden(True)
        self.treeView.doubleClicked.connect(get_clicked_value)
        self.treeView.expandAll()

    def addItems(self, parent, elements):
        for text, children in elements:
            item = QStandardItem(text)
        parent.appendRow(item)
        if children:
            self.addItems(item, children)



    def make_app_in_screen_center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        # print('Position to screen Center!!')

    def init_toolbar(self):
        # Init ToolBar
        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)
        toolbar.setContextMenuPolicy(Qt.PreventContextMenu)  # prevent users from hiding toolbar
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        """Actions"""
        # terminate App
        action_exit_app = self.actionExit
        action_exit_app.triggered.connect(qApp.quit)
        # Open Single Dcm
        action_opnDcm = self.actionOpen_Single_Image
        action_opnDcm.triggered.connect(self.open_one_dcm)
        # Scan folder for dcm
        action_ScanImgFolder = self.actionScan_Image_Folder
        action_ScanImgFolder.triggered.connect(self.addToDB)
        # Parse DICOMDIR
        action_ParseDcmDir = self.actionParse_DICOMDIR
        action_ParseDcmDir.triggered.connect(self.parseDICOMDIR)
        """" Set Keyboard Short Cut for actions"""
        action_opnDcm.setShortcut(QKeySequence.Open)
        """Link actions to ToolBar as Buttons"""
        toolbar.addAction(action_opnDcm)
        toolbar.addAction(action_ScanImgFolder)
        toolbar.addAction(action_ParseDcmDir)
        """"Set ToolBar Buttons Icon"""
        action_opnDcm.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogOpenButton))
        action_ScanImgFolder.setIcon(QApplication.style().standardIcon(QStyle.SP_FileDialogContentsView))
        action_ParseDcmDir.setIcon(QApplication.style().standardIcon(QStyle.SP_DriveCDIcon))

    def parseDICOMDIR(self):
        p, _ = QFileDialog.getOpenFileName(self, 'Open \"DICOMDIR\" File', 'DICOMDIR', 'DICOMDIR File (*)')
        if Path(p).stem == 'DICOMDIR':
            DicomDirParser(source=p, destination=p).parseDIR()

    def addToDB(self, p):
        p = QFileDialog.getExistingDirectory(self, "Choose Folder to Scan for DICOM")
        if p != '':
            DcmDataBase(db_name='KW-DB').createDBbyScan(path_to_scan=p)
            print("DB Import Done!")

    def open_one_dcm(self):
        p, _ = QFileDialog.getOpenFileName(self, 'choose DICOM File to Open', '', 'DICOM Image File (*.dcm)')
        if Path(p).is_file():
            file_path = Path(p)
            print('path=', file_path)
            self.statusBar().showMessage('Reading DICOM File.')
            # self.vtk_display(str(file_path))
            dcm_ds, default_wl, default_ww, rescale_intercept, rescale_slope = DcmViewCalibration.read_dcm_file(
                file_path)
            dcm_image_scaled = DcmViewCalibration.ct_windowed(dcm_ds, default_wl, default_ww, np.uint8, (0, 255))
            image = cv2.cvtColor(dcm_image_scaled, cv2.COLOR_GRAY2RGB)
            cv2.imshow('DICOM', image)
            cv2.waitKey(0)
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
