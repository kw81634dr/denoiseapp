import pydicom
from pydicom.misc import is_dicom
from pydicom.tag import Tag
import numpy as np
from pathlib import Path
from dbmodule import SQLiteTools
import datetime
from pprint import pprint
from PyQt5.QtWidgets import QMessageBox


class DcmViewCalibration:

    @staticmethod
    def window_scale(data, wl, ww, dtype, out_range):
        """
        Scale pixel intensity data using specified window level, width, and intensity range.
        """
        data_new = np.empty(data.shape, dtype=np.double)
        data_new.fill(out_range[1] - 1)

        data_new[data <= (wl - ww / 2.0)] = out_range[0]
        data_new[(data > (wl - ww / 2.0)) & (data <= (wl + ww / 2.0))] = \
            ((data[(data > (wl - ww / 2.0)) & (data <= (wl + ww / 2.0))] - (wl - 0.5)) / (ww - 1.0) + 0.5) * (
                        out_range[1] - out_range[0]) + out_range[0]
        data_new[data > (wl + ww / 2.0)] = out_range[1] - 1
        return data_new.astype(dtype)

    @staticmethod
    def ct_windowed(dcm_ds, wl, ww, dtype, out_range):
        """
        Scale CT image represented as a `pydicom.dataset.FileDataset` instance.
        """
        # Convert pixel data from Houndsfield units to intensity:
        intercept = int(dcm_ds.RescaleIntercept)
        slope = int(dcm_ds.RescaleSlope)
        data = slope * dcm_ds.pixel_array + intercept
        # Scale intensity:
        return DcmViewCalibration.window_scale(data, wl, ww, dtype, out_range)

    @staticmethod
    def read_dcm_file(image_path):
        try:
            dcm_ds = pydicom.dcmread(str(image_path))
            default_wl = 0
            default_ww = 0
            if type(dcm_ds.WindowCenter) is pydicom.multival.MultiValue:
                default_wl = float(dcm_ds.WindowCenter[0])
            elif type(dcm_ds.WindowCenter) is pydicom.valuerep.DSfloat:
                default_wl = float(dcm_ds.WindowCenter)
            if type(dcm_ds.WindowWidth) is pydicom.multival.MultiValue:
                default_ww = float(dcm_ds.WindowWidth[0])
            elif type(dcm_ds.WindowWidth) is pydicom.valuerep.DSfloat:
                default_ww = float(dcm_ds.WindowWidth)

            rescale_intercept = float(dcm_ds.RescaleIntercept)
            rescale_slope = float(dcm_ds.RescaleSlope)

            return dcm_ds, default_wl, default_ww, rescale_intercept, rescale_slope

        except Exception as e:
            pass
            print('Exception', e)
        print("Cannot read DICOM! ", image_path)


def scan_dcm(path):
    fl = []
    pathToGlob = Path(path)
    if pathToGlob.exists():
        f_list = list(pathToGlob.rglob("*"))
        # pprint(f_list)
        for i in f_list:
            if i.is_file():
                fl.append(i)
        return fl


class DcmDataBase:
    def __init__(self, db_name='dataBase'):
        self.DB_File = str(Path.cwd() / db_name) + ".db"
        # 如果存在mysql.ini先删除，方便下列代码的测试
        # if Path(self.DB_File).exists():
        #     Path(self.DB_File).unlink()
        self.sqlite = SQLiteTools()
        self.tableName = None
        try:
            self.sqlite.createConnection(self.DB_File)
        except Exception as e:
            print('DB Error', e)
        self.genTable()

    def genTable(self, table_name='TBImage'):
        self.tableName = table_name
        if not self.sqlite.selectTableExist(table_name):
            # 建立table的同時自動生成 Primary Key 在第一個欄位
            self.sqlite.createSQLtable(table_name)
            # 寫入直欄標籤
            self.sqlite.addSQLtableColumn(self.tableName, "zPath", "TEXT")
            self.sqlite.addSQLtableColumn(self.tableName, "zPatient_id", "TEXT")
            self.sqlite.addSQLtableColumn(self.tableName, "zPatient_name", "TEXT")
            self.sqlite.addSQLtableColumn(self.tableName, "zStudyDescription", "TEXT")
            self.sqlite.addSQLtableColumn(self.tableName, "zSeriesDescription", "TEXT")
            self.sqlite.addSQLtableColumn(self.tableName, "zStudyInstanceUID", "TEXT")
            self.sqlite.addSQLtableColumn(self.tableName, "zSeriesInstanceUID", "TEXT")
            self.sqlite.addSQLtableColumn(self.tableName, "zInstanceNumber", "TEXT")

    def genTable2(self, table_name='TBSeries'):
        self.tableName = table_name
        if not self.sqlite.selectTableExist(table_name):
            # 建立table的同時自動生成 Primary Key 在第一個欄位
            self.sqlite.createSQLtable(table_name)
            # 寫入直欄標籤
            self.sqlite.addSQLtableColumn(self.tableName, "zPatient_name", "TEXT")
            self.sqlite.addSQLtableColumn(self.tableName, "zPatient_id", "TEXT")
            self.sqlite.addSQLtableColumn(self.tableName, "zSeriesDescription", "TEXT")
            self.sqlite.addSQLtableColumn(self.tableName, "zPath", "TEXT")

    def genTable3(self, table_name='TBStudy'):
        self.tableName = table_name
        if not self.sqlite.selectTableExist(table_name):
            # 建立table的同時自動生成 Primary Key 在第一個欄位
            self.sqlite.createSQLtable(table_name)
            # 寫入直欄標籤
            self.sqlite.addSQLtableColumn(self.tableName, "zPatient_name", "TEXT")
            self.sqlite.addSQLtableColumn(self.tableName, "zPatient_id", "TEXT")
            self.sqlite.addSQLtableColumn(self.tableName, "zStusyDescription", "TEXT")
            self.sqlite.addSQLtableColumn(self.tableName, "zPath", "TEXT")

    def createDBbyScan(self, path_to_scan=''):
        # scan for dicom files
        dcm_scan_list = scan_dcm(path_to_scan)
        # pprint(dcm_scan_list)
        readyToInsertList = []

        for ds_file in dcm_scan_list:
            try:
                ds = pydicom.dcmread(ds_file)
                TagValDict = {}
                DcmTagNameDict = {
                    Tag(0x10, 0x20): 'PatientID',
                    Tag(0x10, 0x10): 'PatientName',
                    Tag(0x08, 0x1030): 'studyDescription',
                    Tag(0x08, 0x103E): 'seriesDescription',
                    Tag(0x20, 0x0D): 'studyInstanceUID',
                    Tag(0x20, 0x0E): 'seriesInstanceUID',
                    Tag(0x20, 0x13): 'instanceNumber',
                }
                for key, val in DcmTagNameDict.items():
                    TagValDict.update({'path': str(ds_file)})
                    if key in ds:
                        if ds[key].VR == 'PN':
                            TagValDict.update({val: ds[key].value.decode('utf8')})
                        else:
                            TagValDict.update({val: ds[key].value})

                # pprint(TagValDict)

                dataTuple = (str(TagValDict['path']), TagValDict['PatientID'], str(TagValDict['PatientName']),
                             TagValDict['studyDescription'], TagValDict['seriesDescription'],
                             TagValDict['studyInstanceUID'], TagValDict['seriesInstanceUID'],
                             TagValDict['instanceNumber'])
                readyToInsertList.append(dataTuple)
                # pprint(readyToInsertList)
            except Exception as e:
                # print("Invalid or Not DICOM:", ds_file, "->", e)
                pass
        # 第一個欄位寫入NULL來避免修改自動生成的 Primary Key
        sqlCmd = "INSERT OR ignore INTO " + self.tableName + " VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
        print('len=', len(readyToInsertList))
        self.sqlite.cur.executemany(sqlCmd, readyToInsertList)
        self.sqlite.con.commit()
        print('We have inserted', self.sqlite.cur.rowcount, 'records to the table.')
        self.sqlite.con.close()
        self.getSeries()
        self.getStudies()

    def getSeries(self):
        con = self.sqlite.createConnection(self.DB_File)
        self.genTable2(table_name='TBSeries')
        sql_cmd_group_by_series="SELECT zPatient_name,zPatient_id,zSeriesDescription,group_concat(zPath) FROM TBImage GROUP BY zSeriesInstanceUID  ORDER BY zPatient_name ASC"
        self.sqlite.cur.execute(sql_cmd_group_by_series)
        series_list = [value for value in self.sqlite.cur]
        sq = "INSERT OR ignore INTO TBSeries VALUES (NULL, ?, ?, ?, ?)"
        self.sqlite.cur.executemany(sq, series_list)
        self.sqlite.con.commit()
        self.sqlite.con.close()

    def getStudies(self):
        con = self.sqlite.createConnection(self.DB_File)
        self.genTable3(table_name='TBStudy')
        sql_cmd_group_by_study = "SELECT zPatient_name,zPatient_id,zStudyDescription,group_concat(zPath) FROM TBImage GROUP BY zStudyInstanceUID  ORDER BY zPatient_name ASC"
        self.sqlite.cur.execute(sql_cmd_group_by_study)
        study_list = [value for value in self.sqlite.cur]
        sq = "INSERT OR ignore INTO TBStudy VALUES (NULL, ?, ?, ?, ?)"
        self.sqlite.cur.executemany(sq, study_list)
        self.sqlite.con.commit()
        self.sqlite.con.close()


if __name__ == "__main__":
    # pathScan = r'D:\Users\user\Desktop\NTUCT'
    pathScan = r'D:\Users\user\Desktop\NTUISO\CT5'
    myDb = DcmDataBase(db_name='testDB')
    myDb.createDBbyScan(path_to_scan=pathScan)
    print("Done")
