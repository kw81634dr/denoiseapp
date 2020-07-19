# coding:utf-8

import os
import sqlite3
import datetime
import time


class SQLiteTools():
    def __init__(self):
        pass

    # region 建立資料庫連結和資料庫

    def createConnection(self, DB_name):
        """ 创建数据库连接 """
        # 開啟資料庫，若不存在則建立該資料庫
        self.con = sqlite3.connect(DB_name)
        # 建立一個游標物件
        self.cur = self.con.cursor()

    def selectTableExist(self, tbname):
        """
        判断指定数据表是否存在
        :param tbname: 数据表名称
        :return: 存在范围True,否则返回False
        """
        sql = "select * from sqlite_master where type='table' and name = '" + tbname + "';"
        self.cur.execute(sql)
        cursor = self.cur.fetchall()
        if cursor:
            return True
        else:
            return False

    def createSQLtable(self, tbname, with_unique=False, unique_name='', unique_datatype='TEXT'):
        """
        创建通用数据表，默认第一列为主键，名称:ID，类型:INTEGER, 自增
        :param tbname: 資料表名稱
        :param with_unique: 是否建立'值'不能重複的UNIQUE直欄?
        :param unique_name: UNIQUE直欄的名稱
        :param unique_datatype: UNIQUE直欄的資料類型
        """
        # CREATE TABLE if not exists 表名 (ID INTEGER PRIMARY KEY AUTOINCREMENT);
        if with_unique:
            sql = "CREATE TABLE "+tbname+" (ID INTEGER, "+unique_name+" "+unique_datatype+" UNIQUE, PRIMARY KEY(ID AUTOINCREMENT));"
            # sql = "CREATE TABLE files (ID INTEGER, zUUID TEXT UNIQUE, PRIMARY KEY (ID AUTOINCREMENT));"
        else:
            sql = u"CREATE TABLE if not exists " + tbname + u" (ID INTEGER PRIMARY KEY AUTOINCREMENT);"
        self.cur.execute(sql)
        self.con.commit()  # 提交更新至数据库文件

    # endregion

    # region 添加表格数据

    def addSQLtableColumn(self, tbname, columnName, genre):
        """
        指定数据表添加列
        :param tbname: 表名
        :param columnName: 直行数
        :param genre: 添加列类型
        """
        # ALTER TABLE: 更改資料表限制
        # sytax: ALTER TABLE 表名 ADD 列名 列类型;
        # if isUNIQUE:
        #     sql = u"ALTER TABLE " + tbname + u" ADD " + columnName + " " + genre + ";"
        #     self.cur.execute(sql)
        #     sql = u"CREATE UNIQUE INDEX " + u"index_" + columnName + u" ON " + tbname + " (" + columnName + ")" + ";"
        # else:
        #     sql = u"ALTER TABLE " + tbname + u" ADD " + columnName + " " + genre + ";"
        sql = u"ALTER TABLE " + tbname + u" ADD " + columnName + " " + genre + ";"
        self.cur.execute(sql)
        self.con.commit()  # 提交更新至数据库文件

    def addSQLtableRow(self, tbname, rowNum):
        """
        指定数据表添加指定行
        :param tbname: 表格名称
        :param rowNum: 橫列數
        :return: None
        """
        # INSERT INTO 表名 (ID) VALUES (行);
        rownum = [(i,) for i in range(rowNum)]
        sql = "INSERT INTO " + tbname + " (ID) VALUES (?);"
        self.cur.executemany(sql, rownum)

        # for row in range(1, rowNum+1):
        #     sql = "INSERT INTO " + tbname + " (ID) VALUES (" + str(row) + ");"
        #     self.cur.execute(sql)

        self.con.commit()  # 提交更新至数据库文件

    def setSQLtableValue(self, tbname, column, row, value):
        """
        更新数据表指定位置的值
        :param tbname: 数据表名称
        :param row: 橫列數
        :param column: 直行数
        :param value: 值
        """
        # UPDATE 表名 SET 列名=值 WHERE ID=行;
        sql = u"UPDATE " + tbname + u" SET " + column + "='" + value + "' WHERE ID=" + str(row) + ";"
        self.cur.execute(sql)
        self.con.commit()  # 提交更新至数据库文件

    # endregion

    # region 获取表格数据
    def getSQLtableRowNum(self, tbname):
        """
        获取指定表格总行数
        :param tbname: 表格名称
        :return: 橫列數
        """
        result = 0
        sql = "SELECT COUNT(*) FROM " + tbname + ";"
        self.cur.execute(sql)
        for value in self.cur:
            return value[0]
        return result

    def getSQLtableColumnName(self, tbname):
        """
        获取指定表所有字段名称
        :param taname:  表格名称
        :return:  返回直行名称列表
        """
        sql = "PRAGMA table_info([" + tbname + "])"
        self.cur.execute(sql)
        NameList = []
        for value in self.cur:
            result = value[1]
            if result and result != "ID":
                NameList.append(result)
        return NameList

    def getSQLtableValue(self, tbname, column, row):
        """
        读取指定数据表的指定数据
        :param tbname: 数据表名称
        :param row: 数据橫列
        :param column: 数据直行
        :return 返回查询到的值
        """
        # SELECT 列名 FROM 表名 WHERE ID = 行号;
        sql = "SELECT " + column + " FROM " + tbname + " WHERE ID=" + str(row) + ";"
        self.cur.execute(sql)
        for value in self.cur:
            return value[0]

    def getSQLtableColumn(self, tbname, column):
        """
        读取数据表指定列的所有数据
        :param tbname: 数据表名称
        :param column: 直行名称
        :return 返回查询到的值列表
        """
        # SELECT 列名 FROM 表名;
        sql = "SELECT " + column + " FROM " + tbname + ";"
        valueList = []
        self.cur.execute(sql)
        for value in self.cur:
            valueList.append(value[0])
        return valueList

    def getSQLtableRow(self, tbname, row):
        """
        获取指定表格指定行数据
        :param tbname: 表格名称
        :param row: 橫列
        :return: 值列表
        """
        # SELECT * FROM 表名 WHERE ID=行数;
        sql = "SELECT * FROM " + tbname + " WHERE ID=" + str(row) + ";"
        self.cur.execute(sql)
        for value in self.cur:
            valueList = list(value)
            valueList.pop(0)
            return valueList

    # endregion

    # region 操作数据表

    def delSQLtableRow(self, tbname, startRow, rowNum=1):
        """
        指定数据表删除指定行数
        :param tbname: 表格名称
        :param rowNum: 开始橫列數
        :param rowNum: 橫列数
        """
        # DELETE FROM 表名 WHERE ID = 行;
        rowList = [(i,) for i in range(startRow, startRow + rowNum)]
        sql = "DELETE FROM " + tbname + " WHERE ID = ?;"
        self.cur.executemany(sql, rowList)

        # for row in range(startRow, startRow + rowNum):
        #     sql = "DELETE FROM " + tbname + " WHERE ID = " + str(row) + ";"
        #     self.cur.execute(sql)

        self.con.commit()  # 提交更新至数据库文件

    def delSQLtableColumn(self, tbname, columnName):
        """
        指定数据表删除指定列
        SQLite不支持删除列操作，采用复制新表的方式。
        :param tbname: 表名
        :param columnName: 直行名
        :param genre: 添加列类型
        """
        # ALTER TABLE 表名 drop 列名;   #SQLite不支持
        tbName = "tbName0"
        CloumnNameList = self.getSQLtableColumnName(tbname)
        if columnName in CloumnNameList:
            CloumnNameList.remove(columnName)
        CloumnNameList.insert(0, "ID")
        strName = ','.join(CloumnNameList)
        # create table 零时表名 as select 所有列名称 from 表名 where 1 = 1;
        sql = u"create table " + tbName + " as select " + strName + " from " + tbname + " where 1 = 1"
        self.cur.execute(sql)
        self.con.commit()  # 提交更新至数据库文件

        self.delSQLtable(tbname)
        self.removeSQLtableName(tbName, tbname)

    def removeSQLtableName(self, tbname, newTbname):
        """
        重命名表格
        :param oldTbName:  旧表格名称
        :param newTbName:  新表格名称
        :return:  None
        """
        # alter table 旧表格名称 rename to 新表格名称;
        sql = u"alter table " + tbname + " rename to " + newTbname + ";"
        self.cur.execute(sql)
        self.con.commit()  # 提交更新至数据库文件

    def ClearSQLtable(self, tbname):
        """
        清空指定数据表
        :param tbname: 表名
        """
        # DELETE FROM table_name WHERE[condition];
        sql = "DELETE FROM " + tbname + ";"
        self.cur.execute(sql)
        self.con.commit()  # 提交更新至数据库文件

    def delSQLtable(self, tbname):
        """
        删除指定表
        :param tbname:
        :return: None
        """
        # drop table record;
        sql = u"drop table " + tbname + ";"
        self.cur.execute(sql)
        self.con.commit()  # 提交更新至数据库文件

    # endregion


if __name__ == '__main__':
    print("Python SQLite实例")


    class sqliteTest():
        def __init__(self):
            self.DB_File = "./DBgenBydbModule.db"
            self.tableName = "files"

            # 如果存在mysql.ini先删除，方便下列代码的测试
            if os.path.exists(self.DB_File):
                os.remove(self.DB_File)

            self.sqlite = SQLiteTools()
            self.sqlite.createConnection(self.DB_File)

        # 创建表
        def createTable(self):
            if not self.sqlite.selectTableExist(self.tableName):
                self.sqlite.createSQLtable(self.tableName, with_unique=True, unique_name='zUUID', unique_datatype='TEXT')

        # 添加数据
        def addData(self):
            self.sqlite.addSQLtableColumn(self.tableName, "month1", "text")
            self.sqlite.addSQLtableColumn(self.tableName, "month2", "text")
            self.sqlite.addSQLtableColumn(self.tableName, "date", "date")

            self.sqlite.addSQLtableRow(self.tableName, 4)

            self.sqlite.setSQLtableValue(self.tableName, "month1", 0, "姓名")
            self.sqlite.setSQLtableValue(self.tableName, "month1", 1, "1-1")
            self.sqlite.setSQLtableValue(self.tableName, "month2", 2, "2-2")
            self.sqlite.setSQLtableValue(self.tableName, "month2", 3, "2-3")

            data = [("uuid.140.68.69", "Ride", "a", datetime.date(1994, 5, 5)),
                    ("uuid.140.68.70", "Water", "b", datetime.date(2017, 1, 2)),
                    ("uuid.140.68.69", "this line will be ignored", "due to identity uuid", datetime.date(2019, 3, 2))]
            self.sqlite.cur.executemany("INSERT OR IGNORE INTO files VALUES (NULL, ?, ?, ?, ?)", data)
            self.sqlite.con.commit()

        # 获取数据
        def getData(self):
            value = self.sqlite.getSQLtableRowNum(self.tableName)
            print("数据表总橫列数：", value)

            value = self.sqlite.getSQLtableColumnName(self.tableName)
            print("所有直欄的名称(不包括ID)：", value)

            value = self.sqlite.getSQLtableValue(self.tableName, "month1", 0)
            print("month1直欄,第一列位的值： ", value)

            value = self.sqlite.getSQLtableColumn(self.tableName, "month2")
            print("month2直欄的所有值： ", value)

            value = self.sqlite.getSQLtableRow(self.tableName, 1)
            print("第二橫列的所有值(不包括ID)： ", value)

        # 删除数据
        def delData(self):
            value = self.sqlite.getSQLtableRowNum(self.tableName)
            print("删除前数据表总橫列数：", value)
            self.sqlite.delSQLtableRow(self.tableName, 10, 5)
            value = self.sqlite.getSQLtableRowNum(self.tableName)
            print("删除后数据表总橫列数：", value)

            value = self.sqlite.getSQLtableColumnName(self.tableName)
            print("删除前所有直欄名(不包括ID)", value)
            self.sqlite.delSQLtableColumn(self.tableName, "month3")
            value = self.sqlite.getSQLtableColumnName(self.tableName)
            print("删除后所有直欄名(不包括ID)", value)

            self.sqlite.ClearSQLtable(self.tableName)
            self.sqlite.delSQLtable(self.tableName)


    win = sqliteTest()  # 实例工具类，创建连接
    win.createTable()  # 创建表
    win.addData()  # 添加数据
    win.getData()  # 获取数据
    # win.delData()  # 删除数据

# patientName 0033,1013
# patientID 0031,1020
# patientSex  0010,0040
# patientAge 0010,1010
# patientBirthday 0010,0030
# AcquisitionDate
# Study instance UID
# Series instance UID
# Modality
