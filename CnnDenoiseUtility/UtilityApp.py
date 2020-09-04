from CnnDenoiseUtility.denoiseUtilityUI import *
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QStyle, QToolBar, qApp, \
    QDesktopWidget, QMessageBox
from CnnDenoiseUtility.inference import *


class MyUtilityWindow(QMainWindow, Ui_denoiseUtilityMainWindow):

    def __init__(self, parent=None):
        super(MyUtilityWindow, self).__init__(parent)
        self.input_dir = ''
        self.weight_file = ''
        self.model_path = ''
        self.test_noise_model = ''
        self.output_dir = ''
        self.isStep1Set = False
        self.isStep2Set = False
        self.isStep4Set = False
        ######val_noise_model = get_noise_model(test_noise_model)
        #####model = get_model(model_path)
        # Delegate Main Window
        self.ui = Ui_denoiseUtilityMainWindow()
        self.setupUi(self)
        self.setWindowIcon(QApplication.style().standardIcon(QStyle.SP_TitleBarMenuButton))
        self.setWindowTitle('Denoise Utility')

        self.pushButton_step1_inputdir.clicked.connect(self.prompt_input_path)
        self.pushButton_step2_weightdir.clicked.connect(self.prompt_weight_path)
        self.pushButton_step4_outputdir.clicked.connect(self.prompt_output_path)
        self.pushButton_doProcess.clicked.connect(self.exe_infer)
        self.pushButton_clearall.clicked.connect(self.clear_all)

    def prompt_input_path(self):
        p = QFileDialog.getExistingDirectory(self, "Choose Input Folder")
        if p != '':
            self.input_dir = p
            self.label_step1_inputPath.setText(p)
            self.isStep1Set = True

    def prompt_weight_path(self):
        p, _ = QFileDialog.getOpenFileName(self, 'Choose CNN weight', '', 'Weight (*.hdf5)')
        if Path(p).is_file():
            self.weight_file = p
            self.label_step2_path.setText(p)
            self.isStep2Set = True

    def prompt_output_path(self):
        p = QFileDialog.getExistingDirectory(self, "Choose Output Folder")
        if p != '':
            self.output_dir = p
            self.label_step4_outputdir.setText(p)
            self.isStep4Set = True

    def exe_infer(self):
        if self.isStep1Set and self.isStep2Set and self.isStep4Set:
            myInfer = KwInference(in_dir=self.input_dir, out_dir=self.output_dir, weightpath=self.weight_file)
            myInfer.denoise()
            print("Done")

    def clear_all(self):
        self.input_dir = ''
        self.weight_file = ''
        self.model_path = ''
        self.test_noise_model = ''
        self.output_dir = ''
        self.isStep1Set = False
        self.isStep2Set = False
        self.isStep4Set = False
        self.label_step1_inputPath.setText('')
        self.label_step2_path.setText('')
        self.label_step4_outputdir.setText('')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyUtilityWindow()
    myWin.show()
    sys.exit(app.exec_())
