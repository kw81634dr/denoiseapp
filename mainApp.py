import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QAction, QDirModel, QStyle, QToolBar, qApp, \
    QDesktopWidget, QMessageBox
from PyQt5.QtGui import QKeySequence, QFont, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.Qt import QStandardItemModel
from appUI import *
from pathlib import Path
# Custom Module
from dcmModule import DcmViewCalibration, DcmDataBase
from dicomDirParserModule import DicomDirParser
from fileTreeModule import DcmItem

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
        self.file_model = QDirModel()
        self.dcm_model = QStandardItemModel()
        self.dcm_model.invisibleRootItem()
        '---------------------------------------------'
        taiwan = DcmItem('Taiwan', 16, set_bold=True)
        taipei = DcmItem('Taipei', 14, color=QColor(255, 110, 0))
        banqiao = DcmItem('Banqiao', 12)
        taiwan.appendRow(taipei)
        taipei.appendRow(banqiao)

        america = DcmItem('USA', 16, set_bold=True)
        ca = DcmItem('CA', 14, color=QColor(0, 102, 255))
        sanjose = DcmItem('San Jose', 12)
        sanfrancisco = DcmItem('San Francisco', 12, color=QColor(0, 112, 31))
        america.appendRow(ca)
        ca.appendRow(sanjose)
        ca.appendRow(sanfrancisco)

        self.dcm_model.appendRow(taiwan)
        self.dcm_model.appendRow(america)

        # Tree-view define
        self.treeView.setHeaderHidden(True)
        # self.treeView.doubleClicked.connect(self.get_selected_item_path)
        self.treeView.doubleClicked.connect(get_clicked_value)
        self.treeView.setModel(self.dcm_model)
        self.treeView.expandAll()

    def make_app_in_screen_center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        print('Position to screen Center!!')

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
        # toolbar.addAction(action_ScanDcmDir)
        """"Set ToolBar Buttons Icon"""
        action_opnDcm.setIcon(QApplication.style().standardIcon(QStyle.SP_DirOpenIcon))
        # action_ScanDcmDir.setIcon(QApplication.style().standardIcon(QStyle.SP_FileDialogContentsView))

    def parseDICOMDIR(self):
        p, _ = QFileDialog.getOpenFileName(self, 'Open \"DICOMDIR\" File', 'DICOMDIR', 'DICOMDIR File (*)')
        if Path(p).stem == 'DICOMDIR':
            DicomDirParser(source=p, destination=p).parseDIR()

    def addToDB(self, p):
        p = QFileDialog.getExistingDirectory(self, "Choose Folder to Scan for DICOM")
        DcmDataBase(db_name='KW-DB').createDBbyScan(path_to_scan=p)
        print("DB Imported!")

    def open_one_dcm(self):
        p = QFileDialog.getOpenFileName(self, 'choose DICOM File to Open', '', 'DICOM Image File (*.dcm)')[0]
        if Path(p).is_file():
            file_path = Path(p)
            print('path=', file_path)
            self.statusBar().showMessage('Reading DICOM File.')
            self.vtk_display(str(file_path))
            # dcm_ds, default_wl, default_ww, rescale_intercept, rescale_slope = read_dcm_file(file_path)
            # dcm_image_scaled = ct_windowed(dcm_ds, default_wl, default_ww, np.uint8, (0, 255))
            # image = cv2.cvtColor(dcm_image_scaled, cv2.COLOR_GRAY2RGB)
            # cv2.imshow('DICOM', image)
            # cv2.waitKey(0)
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
