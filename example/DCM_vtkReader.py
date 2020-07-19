#!/usr/bin/env python

import sys
import vtk
from PyQt5 import QtCore, QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.frame = QtWidgets.QFrame()
        self.vl = QtWidgets.QVBoxLayout()
        self.QtInteractor = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.QtInteractor)

        self.dicom_image_path = 'IM-0008-0034.dcm'

        # '----------set up dicom reader---------------'
        self.dcmReader = vtk.vtkDICOMImageReader()
        self.dcmReader.SetDataByteOrderToLittleEndian()
        self.dcmReader.SetFileName(self.dicom_image_path)
        self.dcmReader.Update()

        # '----------init render---------------'
        self.ren = vtk.vtkRenderer()

        # show the dicom flie
        self.imageViewer = vtk.vtkImageViewer2()
        self.imageViewer.SetInputConnection(self.dcmReader.GetOutputPort())

        self.renderWindowInteractor = vtk.vtkRenderWindowInteractor()
        self.imageViewer.SetupInteractor(self.renderWindowInteractor)

        self.imageViewer.Render()
        self.imageViewer.GetRenderer().ResetCamera()
        self.imageViewer.Render()
        self.renderWindowInteractor.Start()





if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()

    sys.exit(app.exec_())
