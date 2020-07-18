import pydicom
from pydicom.tag import Tag
from pathlib import Path


# filename = Path('/Volumes/dataMac/測試用dcm/5B3F22C1')
# filename = Path('/Volumes/dataMac/測試用dcm/IM-0005-0001.dcm')
filename = Path('IM-0008-0034.dcm')
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
    Tag(0x10, 0x1010): 'PatientAge',
    Tag(0x10, 0x40): 'PatientSex',
    Tag(0x10, 0x30): 'PatientBirthDate',
    Tag(0x08, 0x20): 'StudyDate',
    Tag(0x08, 0x30): 'StudyTime',
}
for key, val in DcmTagNameDict.items():
    DcmTagValDict.update({'path': filename})
    if key in ds:
        if ds[key].VR == 'PN':
            DcmTagValDict.update({val: ds[key].value.decode('utf8')})
        else:
            DcmTagValDict.update({val: ds[key].value})
for k, v in DcmTagValDict.items():
    print(k, ':', v)

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
