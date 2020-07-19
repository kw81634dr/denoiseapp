#!/usr/bin/env python

import sys
import vtk
from PyQt5 import QtCore, QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.dicom_image_path = './IM-0008-0034.dcm'

        # '----------set up dicom reader---------------'
        self.dcmReader = vtk.vtkDICOMImageReader()
        self.dcmReader.SetDataByteOrderToLittleEndian()
        self.dcmReader.SetDirectoryName(r"D:\Users\user\Desktop\NTUCT\1323\Ct_Without_ContrastBrain - 1323\InnerEar_C_06_U70u_4")
        self.dcmRescaleSlope = self.dcmReader.GetRescaleSlope()
        self.dcmRescaleOffset = self.dcmReader.GetRescaleOffset()
        self.dcmReader.Update()

        # '----------viewer---------'
        self.dcmViewer = vtk.vtkImageViewer2()
        self.dcmViewer.SetInputConnection(self.dcmReader.GetOutputPort())
        # '------deal with WW & WL-----'
        self.ww = 3500  # WW
        self.wl = 600  # WL
        self.dcmViewer.SetColorLevel(self.wl)
        self.dcmViewer.SetColorWindow(self.ww)

        # '----------TextOverLay---------'
        # slice status message
        self.sliceTextProp = vtk.vtkTextProperty()
        self.sliceTextProp.SetFontFamilyToCourier()
        self.sliceTextProp.SetFontSize(20)
        self.sliceTextProp.SetVerticalJustificationToBottom()
        self.sliceTextProp.SetJustificationToLeft()
        # '---------set up Text Overlay mapper----------'
        self.sliceTextMapper = vtk.vtkTextMapper()
        cur_slice = self.dcmViewer.GetSlice()
        print('cur_slice  = ', cur_slice, ' viewer.GetSliceMax() = ', self.dcmViewer.GetSliceMax())
        msg = (' %d / %d ' % (self.dcmViewer.GetSlice() + 1, self.dcmViewer.GetSliceMax() + 1))
        # '---------set up Text Overlay Actor----------'
        self.sliceTextMapper.SetInput(msg)
        sliceTextActor = vtk.vtkActor2D()
        sliceTextActor.SetMapper(self.sliceTextMapper)
        sliceTextActor.SetPosition(15, 10)

        self.window_interactor = vtk.vtkRenderWindowInteractor()
        self.dcmViewer.SetupInteractor(self.window_interactor)

        self.dcmViewer.GetRenderer().AddActor2D(sliceTextActor)

        '----------add keyboard observer---------'
        self.window_interactor.AddObserver(vtk.vtkCommand.KeyPressEvent, self.keyboard_callback_func)
        self.window_interactor.Initialize()

        self.dcmViewer.Render()
        self.dcmViewer.GetRenderer().ResetCamera()
        self.dcmViewer.Render()
        self.window_interactor.Start()


    def keyboard_callback_func(self, obj, event_id):
        # print(obj.GetKeySym())
        cur_slice = self.dcmViewer.GetSlice()
        if obj.GetKeySym() == obj.GetKeySym() == 'Down':
            cur_slice = (cur_slice + 1) % (self.dcmViewer.GetSliceMax() + 1)
            self.dcmViewer.SetSlice(cur_slice)

        if obj.GetKeySym() == obj.GetKeySym() == 'Up':
            cur_slice = (cur_slice + self.dcmViewer.GetSliceMax()) % (self.dcmViewer.GetSliceMax() + 1)
            self.dcmViewer.SetSlice(cur_slice)

        msg = (' %d / %d ' % (cur_slice + 1, self.dcmViewer.GetSliceMax() + 1))
        print(msg)
        self.sliceTextMapper.SetInput(msg)
        self.dcmViewer.Render()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
