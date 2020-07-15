import sys

#   Import Qt Libraries
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QAction, QDirModel, QStyle, QToolBar, qApp, QDesktopWidget, QMessageBox
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QKeySequence, QFont, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal
#   Import app UI Module
from appUI import *
#   Import other Libraries
from pathlib import Path
# import cv2
from pydicom.misc import is_dicom
from dicomIO import *

# Import VTK Lib
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

import sqlite3

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

dcm_dict = {
         'patientName':'Saving Private Ryan', #電影名稱
         'PatientID':1998, #電影上映年份
         'age':'Steven Spielberg',#導演
         'studyDescription': 'Robert Rodat', #編劇
         'Stars':['Tom Hanks', 'Matt Damon', 'Tom Sizemore'],#明星
         'Oscar ':['Best Director','Best Cinematography','Best Sound','Best Film Editing','Best Effects, Sound Effects Editing']
         #獲得的奧斯卡獎項
}


class StandardItem(QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0, 0, 0)):
        super().__init__()
        fnt = QFont('Arial', font_size)
        fnt.setBold(set_bold)
        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)


class MyMainWindow(QMainWindow, Ui_MainWindow):

    working_path = None
    files = []

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
        # Delegate VTK QFrame
        self.frame = QtWidgets.QFrame()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)

        '------------VTK-------------'
    def vtk_display(self, path):
        dicom_filename = "IM-0008-0034.dcm"
        dicom_dir = 'IAC_2'
        reader = vtk.vtkDICOMImageReader()
        reader.SetFileName(path)
        # reader.SetDirectoryName(dicom_dir)
        rescaleOffset = reader.GetRescaleOffset()
        rescaleSlope = reader.GetRescaleSlope()
        reader.Update()

        # self.viewer = vtk.vtkImageViewer()
        self.viewer = vtk.vtkImageViewer2()
        # self.viewer = vtk.vtkResliceImageViewer()
        self.viewer.SetColorLevel(500.0)
        self.viewer.SetColorWindow(3500.0)
        self.viewer.SetInputData(reader.GetOutput())
        self.viewer.SetupInteractor(self.vtkWidget)
        self.viewer.SetRenderWindow(self.vtkWidget.GetRenderWindow())

        self.viewer.Render()
        self.setCentralWidget(self.frame)
        self.show()
        self.vtkWidget.Initialize()
        '------------VTK-------------'


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
        #   Actions
        action_opnDcm = self.actionOpen_DICOM_File
        action_opnDcm.triggered.connect(self.open_one_dcm)
        action_exit_app = self.actionExit
        action_exit_app.triggered.connect(qApp.quit)    # terminate App
        action_ScanDcmDir = self.actionScan_Dcm_From_Folder
        action_ScanDcmDir.triggered.connect(self.scan_for_dcm)

        # Add action to ToolBar
        toolbar.addAction(action_opnDcm)
        toolbar.addAction(action_ScanDcmDir)
        # Set Icon
        action_opnDcm.setIcon(QApplication.style().standardIcon(QStyle.SP_DirOpenIcon))
        action_ScanDcmDir.setIcon(QApplication.style().standardIcon(QStyle.SP_FileDialogContentsView))
        # Set Short Cut
        action_opnDcm.setShortcut(QKeySequence.Open)

        # Tree-view model
        self.file_model = QDirModel()
        self.dcm_model = QStandardItemModel()
        self.dcm_model.invisibleRootItem()
        '---------------------------------------------'
        taiwan = StandardItem('Taiwan', 16, set_bold=True)
        taipei = StandardItem('Taipei', 14, color=QColor(255, 110, 0))
        banqiao = StandardItem('Banqiao', 12)
        taiwan.appendRow(taipei)
        taipei.appendRow(banqiao)

        america = StandardItem('USA', 16, set_bold=True)
        ca = StandardItem('CA', 14, color=QColor(0, 102, 255))
        sanjose = StandardItem('San Jose', 12)
        sanfrancisco = StandardItem('San Francisco', 12, color=QColor(0, 112, 31))
        america.appendRow(ca)
        ca.appendRow(sanjose)
        ca.appendRow(sanfrancisco)

        self.dcm_model.appendRow(taiwan)
        self.dcm_model.appendRow(america)

        # Tree-view define
        self.treeView.setHeaderHidden(True)
        # self.treeView.doubleClicked.connect(self.get_selected_item_path)
        self.treeView.doubleClicked.connect(self.get_clicked_treeview_value)
        self.treeView.setModel(self.dcm_model)
        self.treeView.expandAll()

    def scan_for_dcm(self):
        p = QFileDialog.getExistingDirectory(self, "Choose Folder to Scan for DICOM")
        if p != '':
            fs = Path(p).rglob("*")
            fl = []
            for f in fs:
                try:
                    if is_dicom(f):
                        fl.append(f)
                except IOError:
                    pass
            print(*fl, sep='\n')


    def get_clicked_treeview_value(self, val):
        print(val.data())
        print(val.row())
        print(val.column())

    # TREE VIEW
    def update_tree_view(self, signal):
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index(signal))
        self.treeView.show()

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
