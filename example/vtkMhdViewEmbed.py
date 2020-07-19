#!/usr/bin/env python

import sys
import vtk
from PyQt5 import QtCore, QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules import vtkInteractionStyle
"""
在讀入圖像後，依次建立
vtkImageActor（vtk圖像演員），
vtkRender（vtk渲染），
vtkRenderWindow（vtk渲染窗口），
vtkRenderWindowInteractor（vtk渲染窗口交互器）
共四個類的對象，並組裝為管線。
***為了屏蔽旋轉操作，建立vtkInteractorStyleImage對象，
並通過vtkRenderWindowInteractor->SetInteractorStyle(style)設置交互對象。
***需要注意的是，vtkImageActor接收的圖像vtkImageData數據類型必須為unsigned char類型，
因此在顯示之前，必要的時候需要利用vtkImageCast將圖像數據類型轉換為unsigned char。
"""


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.frame = QtWidgets.QFrame()
        self.vl = QtWidgets.QVBoxLayout()
        # self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)

        self.dicom_image_path = './IM-0008-0034.dcm'

        # '----------set up dicom reader---------------'
        self.dcmReader = vtk.vtkDICOMImageReader()
        self.dcmReader.SetDataByteOrderToLittleEndian()
        self.dcmReader.SetDirectoryName(r"D:\Users\user\Desktop\NTUCT\1323\Ct_Without_ContrastBrain - 1323\InnerEar_C_06_U70u_4")
        self.dcmRescaleSlope = self.dcmReader.GetRescaleSlope()
        self.dcmRescaleOffset = self.dcmReader.GetRescaleOffset()
        self.dcmReader.Update()
        # '------deal with WW & WL-----'
        self.ww = 2000  # WW
        self.wl = 600  # WL
        # windowlevel = vtkImageMapToWindowLevelColors()
        # windowlevel.SetInput(reader.GetOutput())
        # '----------viewer---------'
        self.dcmViewer = vtk.vtkImageViewer2()
        self.dcmViewer.SetInputConnection(self.dcmReader.GetOutputPort())
        self.dcmViewer.SetColorLevel(500)
        self.dcmViewer.SetColorWindow(3500)
        self.dcmViewer.SetSize(600, 600)

        self.dcmViewer.UpdateDisplayExtent()
        self.dcmViewer.SetRenderWindow(self.vtkWidget.GetRenderWindow())  # !這行確保不會多渲染出一個視窗物件!
        # self.dcmViewer.SetSliceOrientationToXZ()  # 冠狀面 (Coronal plane)
        self.dcmViewer.SetSliceOrientationToYZ()    # 縱切面 (Sagittal plane)
        # self.dcmViewer.SetSliceOrientationToXY()  # 橫狀面 (Transverse plane)


        ######Get RENDERER?????###############
        self.renderer = self.dcmViewer.GetRenderer()
        self.renwin = self.vtkWidget.GetRenderWindow()

        self.renwin.AddRenderer(self.renderer)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)

        # '----------TextOverLay---------'
        # slice status message
        self.sliceTextProp = vtk.vtkTextProperty()
        self.sliceTextProp.SetFontFamilyToCourier()
        self.sliceTextProp.SetFontSize(20)
        self.sliceTextProp.SetVerticalJustificationToBottom()
        self.sliceTextProp.SetJustificationToLeft()
        # '---------set up Text Overlay mapper----------'
        self.sliceTextMapper = vtk.vtkTextMapper()
        self.current_slice = self.dcmViewer.GetSlice()
        print('cur_slice  = ', self.current_slice, ' viewer.GetSliceMax() = ', self.dcmViewer.GetSliceMax())
        msg = (' %d / %d ' % (self.dcmViewer.GetSlice() + 1, self.dcmViewer.GetSliceMax() + 1))
        # '---------set up Text Overlay Actor----------'
        self.sliceTextMapper.SetInput(msg)
        sliceTextActor = vtk.vtkActor2D()
        sliceTextActor.SetMapper(self.sliceTextMapper)
        sliceTextActor.SetPosition(15, 10)
        # '---------End of Text Overlay mapper----------'

        # '---------    Interactor  ----------'
        self.inter = self.renwin.GetInteractor()
        self.inter.SetInteractorStyle(vtkInteractionStyle.vtkInteractorStyleImage())  # ----!Stay in 2D View!-----

        # '----------add keyboard observer---------'
        # self.dcmViewer.GetRenderer().AddActor2D(sliceTextActor)
        self.renderer.AddActor2D(sliceTextActor)
        self.vtkWidget.AddObserver(vtk.vtkCommand.KeyPressEvent, self.keyboard_callback_func)
        # self.vtkWidget.AddObserver(vtk.vtkCommand.MouseWheelForwardEvent, self.keyboard_callback_func)

        self.cam = self.renderer.GetActiveCamera()
        # self.cam.SetFocalPoint(0, 0, 0)     # 设焦点
        # self.cam.SetPosition(0, 0, -1)  # Camera in Z so it display XY planes. # 设观察对象位
        self.cam.SetViewUp(0, 0, -1)    # Up direction is the X not the y. #(0,0,-1) for Coronal plane
        # self.cam.ComputeViewPlaneNormal()  # 自动

        self.renderer.ResetCamera()
        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        self.show()

        self.inter.Initialize()
        # self.inter.Start()

    def keyboard_callback_func(self, obj, event_id):
        print(obj.GetKeySym())
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
        self.renwin.Render()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
