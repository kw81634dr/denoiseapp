#!/usr/bin/env python

import sys
import vtk
from PyQt5 import QtCore, QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules import vtkInteractionStyle
from vtkmodules.vtkIOImage import vtkDICOMImageReader
from PyQt5.QtWidgets import QFrame
from pathlib import Path


class DcmViewFrame(QFrame):
    def __init__(self, dcm_dir='', view_plane='Transverse'):
        """
        建立DICOM VTK 畫布
        :param dcm_dir: 影像路徑
        :param view_plane: 切面:預設'Transverse',可選'Coronal','Sagittal'
        """
        QFrame.__init__(self, parent=None)
        self.vl = QtWidgets.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vl.addWidget(self.vtkWidget)

        if dcm_dir != '':
            self.dcm_series_path = Path(dcm_dir).expanduser()

        # set up VTK dicom reader
        self.dcmReader = vtkDICOMImageReader()
        self.dcmReader.SetDataByteOrderToLittleEndian()
        self.dcmReader.SetDirectoryName(str(self.dcm_series_path))
        self.dcmRescaleSlope = self.dcmReader.GetRescaleSlope()
        self.dcmRescaleOffset = self.dcmReader.GetRescaleOffset()
        self.dcmReader.Update()
        # '------default with WW & WL-----'
        self.ww = 3500  # WW
        self.wl = 600  # WL
        # '----------viewer---------'
        self.dcmViewer = vtk.vtkImageViewer2()
        self.dcmViewer.SetInputConnection(self.dcmReader.GetOutputPort())
        self.dcmViewer.SetColorLevel(500)
        self.dcmViewer.SetColorWindow(3500)
        self.dcmViewer.SetSize(600, 600)
        self.dcmViewer.UpdateDisplayExtent()
        # #!下面那一行確保不會多渲染出一個視窗物件! ##
        self.dcmViewer.SetRenderWindow(self.vtkWidget.GetRenderWindow())  # #!這一行確保不會多渲染出一個視窗物件! # #
        # #!上面那一行確保不會多渲染出一個視窗物件! ##
        #   下面三個方法可渲染不同人體不同的切面
        self.viewPlane = view_plane
        if self.viewPlane == 'Coronal':
            self.dcmViewer.SetSliceOrientationToXZ()    # 冠狀面 (Coronal plane)
        elif self.viewPlane == 'Sagittal':
            self.dcmViewer.SetSliceOrientationToYZ()  # 縱切面 (Sagittal plane)
        else:
            self.dcmViewer.SetSliceOrientationToXY()  # Default: 橫狀面 (Transverse plane)

        # '----------TextOverLay---------'
        # slice status message
        self.sliceTextProp = vtk.vtkTextProperty()
        self.sliceTextProp.SetFontFamilyToCourier()
        self.sliceTextProp.SetFontSize(60)
        self.sliceTextProp.SetVerticalJustificationToBottom()
        self.sliceTextProp.SetJustificationToLeft()
        # '---------set up Text Overlay mapper----------'
        self.sliceTextMapper = vtk.vtkTextMapper()
        self.current_slice = self.dcmViewer.GetSlice()
        print('cur_slice  = ', self.current_slice, ' viewer.GetSliceMax() = ', self.dcmViewer.GetSliceMax())
        msg = (' %d / %d ' % (self.dcmViewer.GetSlice() + 1, self.dcmViewer.GetSliceMax() + 1))
        self.sliceTextMapper.SetInput(msg)
        # '---------set up Text Overlay Actor----------'
        self.sliceTextActor = vtk.vtkActor2D()
        self.sliceTextActor.SetMapper(self.sliceTextMapper)
        self.sliceTextActor.SetPosition(15, 10)

        # ########--Get RENDERER--############
        self.renderer = self.dcmViewer.GetRenderer()
        self.renderer.AddActor2D(self.sliceTextActor)
        # ########--Set Up RENDER Window--############
        self.renderWindow = self.vtkWidget.GetRenderWindow()
        self.renderWindow.AddRenderer(self.renderer)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        # '---------    Interactor  ----------'
        self.inter = self.renderWindow.GetInteractor()
        # ----!Stay in 2D View!-----
        self.inter.SetInteractorStyle(vtkInteractionStyle.vtkInteractorStyleImage())

        # '----------add keyboard observer---------'
        self.vtkWidget.AddObserver(vtk.vtkCommand.KeyPressEvent, self.keyboard_callback_func)
        self.cam = self.renderer.GetActiveCamera()
        if self.viewPlane == 'Coronal':
            # self.cam.SetFocalPoint(0, 0, 0)     # 设焦点
            # self.cam.SetPosition(0, 0, -1)  # Camera in Z so it display XY planes. # 设观察对象位
            self.cam.SetViewUp(0, 0, -1)    # Up direction is the X not the y. #(0,0,-1) for Coronal plane
        # self.cam.ComputeViewPlaneNormal()  # 自动

        self.renderer.ResetCamera()
        self.setLayout(self.vl)
        # self.show()
        self.inter.Initialize()


    def keyboard_callback_func(self, obj, event_id):
        print(obj.GetKeySym())
        cur_slice = self.dcmViewer.GetSlice()
        if obj.GetKeySym() == 'Right' or obj.GetKeySym() == 'Down':
            cur_slice = (cur_slice + 1) % (self.dcmViewer.GetSliceMax() + 1)
            self.dcmViewer.SetSlice(cur_slice)
        if obj.GetKeySym() == 'Left' or obj.GetKeySym() == 'Up':
            cur_slice = (cur_slice + self.dcmViewer.GetSliceMax()) % (self.dcmViewer.GetSliceMax() + 1)
            self.dcmViewer.SetSlice(cur_slice)
        msg = (' %d / %d ' % (cur_slice + 1, self.dcmViewer.GetSliceMax() + 1))
        print(msg)
        self.sliceTextMapper.SetInput(msg)
        self.renderWindow.Render()

