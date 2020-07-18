import shutil
from pydicom.filereader import read_dicomdir
from pathlib import Path

# dcm_dict = {
#         'PatientID':1998, #病患ID
#         'patientName':'Saving Private Ryan', #病患名稱
#         'age':'Steven Spielberg',#年齡
#         'studyDescription': 'Robert Rodat', #study 描述
#         'seriesDescription': 'IAC', #series 描述
#         'Stars':['Tom Hanks', 'Matt Damon', 'Tom Sizemore'],#
#         'Oscar ':['Best Director','Best Cinematography','Best Sound','Best Film Editing']
#         }


class DicomDirParser:
    """Duplicate DICOM files into user prompt directory and build hierarchy structure"""

    def __init__(self, source='', destination=''):
        self.inputPath = Path(source).expanduser()
        self.outputPath = Path(destination).expanduser()
        # self.dcmDirFilePath = self.inputPath
        self.dcmDirFilePath = self.inputPath / "DICOMDIR"     # 測試用路徑, 自動加上DICOMDIR
        """讀取DICOMDIR檔案,下一行是讀取 DICOMDIR 檔案的物件"""
        self.DICOMDIRFILE = read_dicomdir(self.dcmDirFilePath)

        self.pathL1 = ''
        self.pathL2 = ''
        self.pathL3 = ''
        DcmDIRlDict = {}

    def parseDIR(self):
        for patient_record in self.DICOMDIRFILE.patient_records:
            self.pathL1 = self.outputPath.joinpath(patient_record.PatientID)
            print('pathL1=', self.pathL1)
            studies = patient_record.children  # got through each study
            for study in studies:
                self.pathL2 = self.pathL1.joinpath(study.StudyID)
                print('pathL2=', self.pathL2)
                all_series = study.children  # go through each series
                for series in all_series:
                    self.pathL3 = self.pathL2.joinpath('series-' + str(series.SeriesNumber))
                    print('pathL3=', self.pathL3)
                    """建立目的地階層式目錄, 連同父階層建立, 若已存在則將覆蓋"""
                    try:
                        self.pathL3.mkdir(parents=True, exist_ok=True)
                    except FileExistsError:
                        print("Exist", self.pathL3, 'pass!')
                        pass
                    """取得DICOMDIR中的影像中繼資料"""
                    image_records = series.children  # go through each image
                    # print(image_records)
                    """生成輸入檔案的原始路徑"""
                    original_image_filenames = [self.inputPath.joinpath(*image_rec.ReferencedFileID)
                                                for image_rec in image_records]
                    """複製影像到目標階層目錄"""
                    for old_filename in original_image_filenames:
                        new_filename = self.pathL3.joinpath(old_filename.name)
                        print('Copy', old_filename, 'to', new_filename)
                        try:
                            shutil.copyfile(old_filename, new_filename)  # copyfile(A, B) # A,B 皆須是檔案
                        except shutil.Error:
                            print(shutil.Error)
                            pass
                        except FileNotFoundError:
                            print('File not Found')
                            pass
                print("Done")


if __name__ == "__main__":
    # 在路徑前加 r，使編譯器將整組路徑視為Raw String，字串中的跳脫字元都被當成一般字元處理。
    # 原因: 編譯器將路徑中的 C:\Users\ 視為Unicode-Escape編碼的跳脫字元
    # 因此\U被當成Unicode Code字串的起點，依照定義後面必需接8位數字 (ex. \U01000001) 來Decode
    # 在此後面接了一串字母，因此產生Decode失敗的錯誤訊息。
    in_directory = r'D:\Users\user\Desktop\NTUISO\CT1'
    out_directory = r'C:\Parsed'
    DicomDirParser(in_directory, out_directory).parseDIR()
    print("Done")
