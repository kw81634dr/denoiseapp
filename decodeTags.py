import pydicom
from pydicom.tag import Tag
from pathlib import Path
from pydicom.uid import generate_uid
import chardet
from pydicom.filebase import DicomBytesIO
import warnings

# filename = Path(r'D:\Users\user\Desktop\kwmri\DICOM\ST000000\SE000005\MR000003.TRUE')
filename = Path(r'D:\Users\user\Desktop\NTUCT\8252\Ct_Without_ContrastBrain - 16683\IAC_2\IM-0008-0002.dcm')
filename = Path(r'D:\Users\user\Desktop\NTUCT\8252\Ct_Without_ContrastBrain - 16683\AXIAL_303\IM-0009-0003.dcm')
# coding = 'big5'
coding = 'utf8'
ds = pydicom.dcmread(str(filename))
DcmTagValDict = {}
DcmTagNameDict = {
    Tag(0x33, 0x1013): 'NTUPatientName',
    Tag(0x33, 0x1014): 'NTUPatientId',
    Tag(0x33, 0x1018): 'NTUDoctorName',
    Tag(0x0028, 0x1050): 'wl',
    Tag(0x0028, 0x1051): 'ww',
    Tag(0x20, 0x10): 'StudyID',
    Tag(0x20, 0x11): 'Series#',
    Tag(0x20, 0x13): 'Instance#',
    Tag(0x10, 0x10): 'PatientName',
    Tag(0x10, 0x20): 'PatientID',
    Tag(0x10, 0x1010): 'PatientAge',
    Tag(0x10, 0x40): 'PatientSex',
    Tag(0x10, 0x30): 'PatientBirthDate',
    Tag(0x08, 0x20): 'StudyDate',
    Tag(0x08, 0x30): 'StudyTime',
    Tag(0x08, 0x1030): 'studyDescription',
    Tag(0x08, 0x103E): 'seriesDescription',
    Tag(0x20, 0x0D): 'studyInstanceUID',
    Tag(0x20, 0x0E): 'seriesInstanceUID',
    Tag(0x20, 0x13): 'instanceNumber'
}
for key, val in DcmTagNameDict.items():
    DcmTagValDict.update({'path': filename})
    if key in ds:
        if ds[key].VR == 'PN':
            DcmTagValDict.update({val: ds[key].value.decode(coding)})
        else:
            DcmTagValDict.update({val: ds[key].value})
for k, v in DcmTagValDict.items():
    print(k, ':', v)

uuid = generate_uid(entropy_srcs=[str(DcmTagValDict['PatientID']), DcmTagValDict['studyInstanceUID'], DcmTagValDict['seriesInstanceUID'], str(DcmTagValDict['instanceNumber'])])

wl = DcmTagValDict['wl']
if type(wl) is pydicom.multival.MultiValue:
    print('多個 wl')
elif type(wl) is pydicom.valuerep.DSfloat:
    print('單個 wl')
print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
print('個案: {}({}) {} {}歲 生日{}'.format(DcmTagValDict['NTUPatientName'], DcmTagValDict['NTUPatientId'],
                                  DcmTagValDict['PatientSex'], DcmTagValDict['PatientAge'], DcmTagValDict['PatientBirthDate']))
print('醫師: {} 檢號#{} 日期{}'.format(DcmTagValDict['NTUDoctorName'], DcmTagValDict['StudyID'],
                                  DcmTagValDict['StudyDate']))
print('uuidBaseOnImg=', uuid)
print(generate_uid())
