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
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)

        self.dicom_image_path = './IM-0008-0034.dcm'

        # '----------set up dicom reader---------------'
        self.dcmReader = vtk.vtkDICOMImageReader()
        self.dcmReader.SetDataByteOrderToLittleEndian()
        self.dcmReader.SetDirectoryName(r"D:\Users\user\Desktop\NTUCT\1323\Ct_Without_ContrastBrain - 1323\InnerEar_C_06_U70u_4")
        self.dcmReader.Update()

        # '----------init render---------------'
        self.ren = vtk.vtkRenderer()


        # '---------set up mapper----------'
        self.slice_mapper = vtk.vtkImageSliceMapper()
        self.slice_mapper.SetInputConnection(self.dcmReader.GetOutputPort())
        # set random slice number
        # self.slice_mapper.SetSliceNumber(50)

        # set up image_slice
        self.image_slice = vtk.vtkImageSlice()
        self.image_slice.SetMapper(self.slice_mapper)

        # '-----set up window and level of image_slice----'
        # self.MinMax = self.dcmReader.GetOutput().GetScalarRange()
        # self.image_slice_property = self.image_slice.GetProperty()
        # self.image_slice_property.SetColorWindow(self.MinMax[1])
        # self.image_slice_property.SetColorLevel((self.MinMax[1] - self.MinMax[0]) / 2)
        # self.image_slice.Update()

        # '---------set image_slice as input for renderer------'
        self.ren.AddViewProp(self.image_slice)


        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.dcmReader.GetOutputPort())
        # # Create an actor
        # actor = vtk.vtkActor()
        # actor.SetMapper(mapper)
        # self.ren.AddActor(actor)

        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        self.ren.ResetCamera()

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        self.show()
        self.iren.Initialize()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()

    sys.exit(app.exec_())
