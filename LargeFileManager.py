#!/usr/bin/env python3

from PyQt5 import uic
from urllib.parse import urlparse
import mysql.connector
from datetime import date, datetime, timedelta
import  os
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,QWidget,QListWidgetItem,QMessageBox,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,QSizePolicy,
        QListWidget,QVBoxLayout)

class FileItem(QWidget):
    def openFile(self):
        os.system("vlc \"" + self.filenameFull + "\"")
        pass
    def __init__(self, filename, filenameFull, suggestPlay = False, parent=None):
        super(FileItem, self).__init__(parent)
        self.filename = filename
        self.filenameFull = filenameFull

        self.filenameLabel = QLabel(filename)
        self.filenameFullLabel = QLabel(filenameFull)

        self.buttonPlay = QPushButton('Play')
        self.buttonDel = QPushButton('Del')

        self.buttonDel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.buttonPlay.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.buttonDel.setStyleSheet("background-color:#ff0000;");

        self.buttonPlay.clicked.connect(self.openFile)

        if suggestPlay == True :
            self.buttonPlay.setStyleSheet("background-color:#ffff00;");
            pass

        #self.filenameLabel.setStyleSheet("background-color:#00FF00;");
        #self.filenameFullLabel.setStyleSheet("background-color:#0000FF;");

        mainLayout = QGridLayout()

        mainLayout.setColumnStretch(0, 10)
        mainLayout.setColumnStretch(1, 10)
        mainLayout.setColumnStretch(2, 300)

        mainLayout.addWidget(self.buttonPlay, 0, 0, 2, 1)
        mainLayout.addWidget(self.buttonDel, 0, 1, 2, 1)

        mainLayout.addWidget(self.filenameLabel, 0, 2, 1, 1)
        mainLayout.addWidget(self.filenameFullLabel, 1, 2, 1, 1)

        #self.setStyleSheet("background-color:#FFFF00;");

        self.setLayout(mainLayout)
        pass
    pass


class Dialog(QDialog):
    NumGridRows = 3
    NumButtons = 4

    WindoWidth = 1600
    WindowHeight = 1000

    def __init__(self):
        super(Dialog, self).__init__()

        #self.createMenu()
        self.createHorizontalGroupBox()
        #self.createGridGroupBox()
        #self.createFormGroupBox()

        bigEditor = QTextEdit()
        bigEditor.setPlainText("This widget takes up all the remaining space "
                "in the top-level layout.")

        self.fileListView = QListWidget()
        item1 = FileItem("testFilename1", "testFileNameFull1")
        item2 = FileItem("adsfasdf", "adsfasdfasdfasdf")
        item3 = FileItem("asdfasdfsdf", "asdfasdfasdfasdfsdf")

        viewItem1 = QListWidgetItem()
        viewItem2 = QListWidgetItem()
        viewItem3 = QListWidgetItem()

        viewItem1.setSizeHint(item1.sizeHint())
        viewItem2.setSizeHint(item2.sizeHint())
        viewItem3.setSizeHint(item3.sizeHint())

        self.fileListView.addItem(viewItem1)
        self.fileListView.addItem(viewItem2)
        self.fileListView.addItem(viewItem3)

        self.fileListView.setItemWidget(viewItem1, item1)
        self.fileListView.setItemWidget(viewItem2, item2)
        self.fileListView.setItemWidget(viewItem3, item3)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        #mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.horizontalGroupBox)
        #mainLayout.addWidget(self.gridGroupBox)
        #mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.fileListView)
        mainLayout.addWidget(buttonBox)

        self.fileListView.clear()

        self.setLayout(mainLayout)

        self.setWindowTitle("Basic Layouts")

        self.resize(Dialog.WindoWidth,Dialog.WindowHeight)

    def createMenu(self):
        self.menuBar = QMenuBar()

        self.fileMenu = QMenu("&File", self)
        self.exitAction = self.fileMenu.addAction("E&xit")
        self.menuBar.addMenu(self.fileMenu)

        self.exitAction.triggered.connect(self.accept)

    def getAllFiles(self,directoryName):
        MIN_FILE_SIZE = 100 * 1024 * 1024
        result = []
        if not os.path.isdir(directoryName):
            return result

        for currentdir, dirs, files in os.walk(directoryName):
            for file in files:
                tmpfullname = os.path.join(currentdir, file)
                tmpsize = os.path.getsize(tmpfullname)
                if tmpsize >= MIN_FILE_SIZE:
                    result.append(
                        {
                            "filename": file,
                            "filefullname": tmpfullname,
                            "filesize": tmpsize,
                            "filetype": file.split(".")[-1],
                            "filemodifieddate": datetime.fromtimestamp(
                                os.path.getmtime(tmpfullname)
                            ),
                            "filecreateddate": datetime.fromtimestamp(
                                os.path.getctime(tmpfullname)
                            ),
                        }
                    )

        return result

    def writeFileInfosIntoDatabase(self, filesinfos, dbconnect):
        insertsql = """  INSERT INTO `springdb`.`fileinfoindex`
                                    (`fileid`,
                                    `filename`,
                                    `filefullname`,
                                    `filesize`,
                                    `filetype`,
                                    `md5`,
                                    `sha256`,
                                    `filemodifieddate`,
                                    `filecreateddate`,
                                    `indexinfoupdateddate`)
                                    VALUES
                                    (null,
                                    %(filename)s,
                                    %(filefullname)s,
                                    %(filesize)s,
                                    %(filetype)s,
                                    null,
                                    null,
                                    %(filemodifieddate)s,
                                    %(filecreateddate)s,
                                    CURRENT_TIMESTAMP(3)) """

        cursor = dbconnect.cursor()
        for tmp in filesinfos:
            cursor.execute(insertsql, tmp)
        cursor.close()
        pass

    def clearDatabase(self, dbconnect):
        updateSql = """ DELETE FROM `springdb`.`fileinfoindex` """
        cursor = dbconnect.cursor()
        cursor.execute(updateSql)
        cursor.close()
        pass

    def getFilesWithEqualSize(self, dbconnect):
        selectsql = """ SELECT 
                            fileid, filefullname, filesize, filename
                        FROM
                            fileinfoindex
                        WHERE
                            filesize IN (SELECT 
                                    filesize
                                FROM
                                    fileinfoindex
                                GROUP BY filesize
                                HAVING COUNT(*) > 1) ORDER BY filesize DESC """

        cursor = dbconnect.cursor()
        cursor.execute(selectsql)
        tmpJoblist = []
        for (fileid, filefullname, filesize, filename) in cursor:
            tmpJoblist.append(
                {"fileid": fileid, "filefullname": filefullname, "filesize": filesize, "filename": filename})
            pass
        cursor.close()
        return tmpJoblist

    def reload(self):
        quit_msg = "Are you sure reload ?"
        reply = QMessageBox.question(self, 'Message',
                                     quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            url = urlparse("mysql://192.168.11.5:3306/springdb")

            mydb = mysql.connector.connect(
                host=url.hostname,
                port=url.port,
                user="testspring",
                passwd="testspring",
                database="springdb",
            )

            result = self.getFilesWithEqualSize(mydb)

            mydb.close()

            self.fileListView.clear()

            for itm in result:
                item1 = FileItem( str(itm["filesize"]) + "  " + itm["filename"], itm["filefullname"])

                viewItem1 = QListWidgetItem()

                viewItem1.setSizeHint(item1.sizeHint())

                self.fileListView.addItem(viewItem1)

                self.fileListView.setItemWidget(viewItem1, item1)

                pass
            pass
        else:
            pass
        pass

    def rescan(self):
        quit_msg = "Rescan will clear all info, and it takes quite a lot time to create new info"
        reply = QMessageBox.question(self, 'Message',
                                           quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            rootdir = "/mnt/home/hjd/Videos"
            rootdir2 = "/mnt/home/hjd/Downloads"
            rootdir3 = "/home/hjd/Downloads"
            rootdir4 = "/media/hjd/elements/videos"
            items1 = self.getAllFiles(rootdir)
            items2 = self.getAllFiles(rootdir2)
            items3 = self.getAllFiles(rootdir3)
            items4 = self.getAllFiles(rootdir4)

            # print(getAllFiles(rootdir))
            # print(getAllFiles(rootdir2))
            # print(getAllFiles(rootdir3))

            url = urlparse("mysql://192.168.11.5:3306/springdb")

            mydb = mysql.connector.connect(
                host=url.hostname,
                port=url.port,
                user="testspring",
                passwd="testspring",
                database="springdb",
            )

            self.clearDatabase(mydb)
            self.writeFileInfosIntoDatabase(items1, mydb)
            self.writeFileInfosIntoDatabase(items2, mydb)
            self.writeFileInfosIntoDatabase(items3, mydb)
            self.writeFileInfosIntoDatabase(items4, mydb)

            mydb.commit()
            mydb.close()
            pass
        else:
            pass

    def createHorizontalGroupBox(self):
        self.horizontalGroupBox = QGroupBox("Function Buttons")
        layout = QHBoxLayout()
        button1 = QPushButton("ReScan")
        button1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        button1.clicked.connect(self.rescan)

        button2 = QPushButton("Reload")
        button2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        button2.clicked.connect(self.reload)

        button3 = QPushButton("")
        button3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        button4 = QPushButton("")
        button4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(button1)
        layout.addWidget(button2)
        layout.addWidget(button3)
        layout.addWidget(button4)
        self.horizontalGroupBox.setLayout(layout)

    def createGridGroupBox(self):
        self.gridGroupBox = QGroupBox("Grid layout")
        layout = QGridLayout()

        for i in range(Dialog.NumGridRows):
            label = QLabel("Line %d:" % (i + 1))
            lineEdit = QLineEdit()
            layout.addWidget(label, i + 1, 0)
            layout.addWidget(lineEdit, i + 1, 1)

        self.smallEditor = QTextEdit()
        self.smallEditor.setPlainText("This widget takes up about two thirds "
                "of the grid layout.")

        layout.addWidget(self.smallEditor, 0, 2, 4, 1)

        layout.setColumnStretch(1, 10)
        layout.setColumnStretch(2, 20)
        self.gridGroupBox.setLayout(layout)

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Form layout")
        layout = QFormLayout()
        layout.addRow(QLabel("Line 1:"), QLineEdit())
        layout.addRow(QLabel("Line 2, long text:"), QComboBox())
        layout.addRow(QLabel("Line 3:"), QSpinBox())
        self.formGroupBox.setLayout(layout)

    def resizeEvent(self, QResizeEvent):
        self.setWindowTitle("Basic Layouts " + str(self.frameGeometry().width()) + " x " + str(self.frameGeometry().height()))
        #print(self.frameGeometry().width(), " ", self.frameGeometry().height())


if __name__ == '__main__':

    import sys

    #sys.exit(0)

    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())

