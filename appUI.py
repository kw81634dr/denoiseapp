# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'appUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1008, 667)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame_Vtk = QtWidgets.QFrame(self.centralwidget)
        self.frame_Vtk.setGeometry(QtCore.QRect(20, 20, 361, 361))
        self.frame_Vtk.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Vtk.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Vtk.setObjectName("frame_Vtk")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1008, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuImport_DICOM_files = QtWidgets.QMenu(self.menuFile)
        self.menuImport_DICOM_files.setObjectName("menuImport_DICOM_files")
        self.menuOpen_DICOM = QtWidgets.QMenu(self.menuFile)
        self.menuOpen_DICOM.setObjectName("menuOpen_DICOM")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuWindow_W = QtWidgets.QMenu(self.menubar)
        self.menuWindow_W.setObjectName("menuWindow_W")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget = QtWidgets.QDockWidget(MainWindow)
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeView = QtWidgets.QTreeView(self.dockWidgetContents)
        self.treeView.setObjectName("treeView")
        self.verticalLayout.addWidget(self.treeView)
        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionUndo = QtWidgets.QAction(MainWindow)
        self.actionUndo.setObjectName("actionUndo")
        self.actionReset_All = QtWidgets.QAction(MainWindow)
        self.actionReset_All.setObjectName("actionReset_All")
        self.actionLoad_Weight_File = QtWidgets.QAction(MainWindow)
        self.actionLoad_Weight_File.setObjectName("actionLoad_Weight_File")
        self.actionLayout = QtWidgets.QAction(MainWindow)
        self.actionLayout.setObjectName("actionLayout")
        self.action_Image_Converter = QtWidgets.QAction(MainWindow)
        self.action_Image_Converter.setObjectName("action_Image_Converter")
        self.actionfrom_PACS = QtWidgets.QAction(MainWindow)
        self.actionfrom_PACS.setObjectName("actionfrom_PACS")
        self.actionfrom_CD_DVD = QtWidgets.QAction(MainWindow)
        self.actionfrom_CD_DVD.setObjectName("actionfrom_CD_DVD")
        self.actionParse_DICOMDIR = QtWidgets.QAction(MainWindow)
        self.actionParse_DICOMDIR.setObjectName("actionParse_DICOMDIR")
        self.actionOpen_CD = QtWidgets.QAction(MainWindow)
        self.actionOpen_CD.setObjectName("actionOpen_CD")
        self.actionHierarchy_Orgnizer = QtWidgets.QAction(MainWindow)
        self.actionHierarchy_Orgnizer.setObjectName("actionHierarchy_Orgnizer")
        self.actionDICOM_Tags = QtWidgets.QAction(MainWindow)
        self.actionDICOM_Tags.setObjectName("actionDICOM_Tags")
        self.actionDICOMDIR_Parser = QtWidgets.QAction(MainWindow)
        self.actionDICOMDIR_Parser.setObjectName("actionDICOMDIR_Parser")
        self.actionOpen_Single_Image = QtWidgets.QAction(MainWindow)
        self.actionOpen_Single_Image.setObjectName("actionOpen_Single_Image")
        self.actionScan_Image_Folder = QtWidgets.QAction(MainWindow)
        self.actionScan_Image_Folder.setObjectName("actionScan_Image_Folder")
        self.menuImport_DICOM_files.addAction(self.actionParse_DICOMDIR)
        self.menuImport_DICOM_files.addAction(self.actionOpen_CD)
        self.menuOpen_DICOM.addAction(self.actionOpen_Single_Image)
        self.menuOpen_DICOM.addAction(self.actionScan_Image_Folder)
        self.menuFile.addAction(self.menuOpen_DICOM.menuAction())
        self.menuFile.addAction(self.menuImport_DICOM_files.menuAction())
        self.menuFile.addAction(self.actionLoad_Weight_File)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionReset_All)
        self.menuView.addAction(self.actionDICOM_Tags)
        self.menuTools.addAction(self.action_Image_Converter)
        self.menuTools.addAction(self.actionDICOMDIR_Parser)
        self.menuWindow_W.addAction(self.actionLayout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuWindow_W.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File(&F)"))
        self.menuImport_DICOM_files.setTitle(_translate("MainWindow", "Import From"))
        self.menuOpen_DICOM.setTitle(_translate("MainWindow", "Open DICOM"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit(&E)"))
        self.menuView.setTitle(_translate("MainWindow", "View(&V)"))
        self.menuTools.setTitle(_translate("MainWindow", "Tools(&T)"))
        self.menuWindow_W.setTitle(_translate("MainWindow", "Window(&W)"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.dockWidget.setWindowTitle(_translate("MainWindow", "FileBrowser"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionUndo.setText(_translate("MainWindow", "Undo"))
        self.actionReset_All.setText(_translate("MainWindow", "Reset All"))
        self.actionLoad_Weight_File.setText(_translate("MainWindow", "Load Weight File"))
        self.actionLayout.setText(_translate("MainWindow", "Layout"))
        self.action_Image_Converter.setText(_translate("MainWindow", "Image Conveter"))
        self.actionfrom_PACS.setText(_translate("MainWindow", "from PACS"))
        self.actionfrom_CD_DVD.setText(_translate("MainWindow", "from CD/DVD"))
        self.actionParse_DICOMDIR.setText(_translate("MainWindow", "DICOMDIR"))
        self.actionOpen_CD.setText(_translate("MainWindow", "CD/DVD"))
        self.actionHierarchy_Orgnizer.setText(_translate("MainWindow", "Hierarchy Organizer"))
        self.actionDICOM_Tags.setText(_translate("MainWindow", "DICOM Tags"))
        self.actionDICOMDIR_Parser.setText(_translate("MainWindow", "DICOM Hierarchy Organizer"))
        self.actionOpen_Single_Image.setText(_translate("MainWindow", "Single Image File"))
        self.actionScan_Image_Folder.setText(_translate("MainWindow", "by Scanning a Folder"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

