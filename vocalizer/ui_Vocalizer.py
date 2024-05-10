# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Vocalizer.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1020, 650)
        MainWindow.setMinimumSize(QtCore.QSize(0, 650))
        MainWindow.setMaximumSize(QtCore.QSize(1020, 650))
        MainWindow.setStyleSheet("background-color: rgb(195, 195, 195);\n"
"\n"
"QLabel{\n"
"    Layout:center;\n"
"}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.SideBar = QtWidgets.QWidget(self.centralwidget)
        self.SideBar.setGeometry(QtCore.QRect(0, 0, 261, 650))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SideBar.sizePolicy().hasHeightForWidth())
        self.SideBar.setSizePolicy(sizePolicy)
        self.SideBar.setStyleSheet("QWidget{\n"
"    background-color: rgb(106, 106, 106);\n"
"    border: 1px;\n"
"}\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"")
        self.SideBar.setObjectName("SideBar")
        self.layoutWidget = QtWidgets.QWidget(self.SideBar)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 80, 260, 591))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, 9, -1, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.CV_Button = QtWidgets.QPushButton(self.layoutWidget)
        self.CV_Button.setMinimumSize(QtCore.QSize(181, 31))
        self.CV_Button.setMaximumSize(QtCore.QSize(181, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.CV_Button.setFont(font)
        self.CV_Button.setStyleSheet("QPushButton{\n"
"background-color: rgb(238, 238, 238);\n"
"border-style: solid;\n"
"border-color: black;\n"
"border-width: 2px;\n"
"border-radius: 5px;\n"
"text-align: center;\n"
"\n"
"}\n"
"\n"
"QPushButton:checked{\n"
"    color:rgb(255, 255, 255);\n"
"    font-weight:bold;\n"
"    background-color: rgb(39, 39, 39);\n"
"    border-style: solid;\n"
"    border-color: white;\n"
"    border-width: 2px;\n"
"    border-radius: 5px;\n"
"}")
        self.CV_Button.setCheckable(True)
        self.CV_Button.setAutoExclusive(True)
        self.CV_Button.setObjectName("CV_Button")
        self.verticalLayout.addWidget(self.CV_Button)
        self.listView = QtWidgets.QListView(self.layoutWidget)
        self.listView.setMinimumSize(QtCore.QSize(0, 0))
        self.listView.setMaximumSize(QtCore.QSize(261, 111))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Black")
        self.listView.setFont(font)
        self.listView.setStyleSheet("QListView{\n"
"    background-color: rgb(255, 255, 255);\n"
"}")
        self.listView.setObjectName("listView")
        self.verticalLayout.addWidget(self.listView)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 58, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.TV_Button = QtWidgets.QPushButton(self.layoutWidget)
        self.TV_Button.setMinimumSize(QtCore.QSize(181, 31))
        self.TV_Button.setMaximumSize(QtCore.QSize(181, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.TV_Button.setFont(font)
        self.TV_Button.setStyleSheet("QPushButton{\n"
"background-color: rgb(238, 238, 238);\n"
"border-style: solid;\n"
"border-color: black;\n"
"border-width: 2px;\n"
"border-radius: 5px;\n"
"}\n"
"\n"
"QPushButton:checked{\n"
"    color:rgb(255, 255, 255);\n"
"    font-weight:bold;\n"
"    background-color: rgb(39, 39, 39);\n"
"    border-style: solid;\n"
"    border-color: white;\n"
"    border-width: 2px;\n"
"    border-radius: 5px;\n"
"}")
        self.TV_Button.setCheckable(True)
        self.TV_Button.setAutoExclusive(True)
        self.TV_Button.setObjectName("TV_Button")
        self.verticalLayout_2.addWidget(self.TV_Button)
        self.Tenor_Bttn = QtWidgets.QPushButton(self.layoutWidget)
        self.Tenor_Bttn.setMinimumSize(QtCore.QSize(161, 31))
        self.Tenor_Bttn.setMaximumSize(QtCore.QSize(161, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.Tenor_Bttn.setFont(font)
        self.Tenor_Bttn.setStyleSheet("QPushButton{\n"
"background-color: rgb(195, 195, 195);\n"
"border-style: solid;\n"
"border-color: black;\n"
"border-width: 1px;\n"
"border-radius: 2px;\n"
"}\n"
"\n"
"QPushButton:checked{\n"
"    color:rgb(255, 255, 255);\n"
"    font-weight:bold;\n"
"    background-color: rgb(39, 39, 39);\n"
"    border-style: solid;\n"
"    border-color: white;\n"
"    border-width:1px;\n"
"    border-radius: 2px;\n"
"}")
        self.Tenor_Bttn.setCheckable(True)
        self.Tenor_Bttn.setAutoExclusive(True)
        self.Tenor_Bttn.setObjectName("Tenor_Bttn")
        self.verticalLayout_2.addWidget(self.Tenor_Bttn)
        self.Tenor_List_2 = QtWidgets.QListView(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Tenor_List_2.sizePolicy().hasHeightForWidth())
        self.Tenor_List_2.setSizePolicy(sizePolicy)
        self.Tenor_List_2.setMaximumSize(QtCore.QSize(261, 111))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Black")
        self.Tenor_List_2.setFont(font)
        self.Tenor_List_2.setStyleSheet("QListView{\n"
"    background-color: rgb(255, 255, 255);\n"
"}")
        self.Tenor_List_2.setObjectName("Tenor_List_2")
        self.verticalLayout_2.addWidget(self.Tenor_List_2)
        self.Soprano_Bttn = QtWidgets.QPushButton(self.layoutWidget)
        self.Soprano_Bttn.setMinimumSize(QtCore.QSize(161, 31))
        self.Soprano_Bttn.setMaximumSize(QtCore.QSize(161, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.Soprano_Bttn.setFont(font)
        self.Soprano_Bttn.setStyleSheet("QPushButton{\n"
"background-color: rgb(195, 195, 195);\n"
"border-style: solid;\n"
"border-color: black;\n"
"border-width: 1px;\n"
"border-radius: 2px;\n"
"}\n"
"\n"
"QPushButton:checked{\n"
"    color:rgb(255, 255, 255);\n"
"    font-weight:bold;\n"
"    background-color: rgb(39, 39, 39);\n"
"    border-style: solid;\n"
"    border-color: white;\n"
"    border-width:1px;\n"
"    border-radius: 2px;\n"
"}")
        self.Soprano_Bttn.setCheckable(True)
        self.Soprano_Bttn.setAutoExclusive(True)
        self.Soprano_Bttn.setObjectName("Soprano_Bttn")
        self.verticalLayout_2.addWidget(self.Soprano_Bttn)
        self.Soprano_List_2 = QtWidgets.QListView(self.layoutWidget)
        self.Soprano_List_2.setMaximumSize(QtCore.QSize(261, 111))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Black")
        self.Soprano_List_2.setFont(font)
        self.Soprano_List_2.setStyleSheet("QListView{\n"
"    background-color: rgb(255, 255, 255);\n"
"}")
        self.Soprano_List_2.setObjectName("Soprano_List_2")
        self.verticalLayout_2.addWidget(self.Soprano_List_2)
        self.Bass_Bttn = QtWidgets.QPushButton(self.layoutWidget)
        self.Bass_Bttn.setMinimumSize(QtCore.QSize(161, 31))
        self.Bass_Bttn.setMaximumSize(QtCore.QSize(161, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.Bass_Bttn.setFont(font)
        self.Bass_Bttn.setStyleSheet("QPushButton{\n"
"background-color: rgb(195, 195, 195);\n"
"border-style: solid;\n"
"border-color: black;\n"
"border-width: 1px;\n"
"border-radius: 2px;\n"
"}\n"
"\n"
"QPushButton:checked{\n"
"    color:rgb(255, 255, 255);\n"
"    font-weight:bold;\n"
"    background-color: rgb(39, 39, 39);\n"
"    border-style: solid;\n"
"    border-color: white;\n"
"    border-width:1px;\n"
"    border-radius: 2px;\n"
"}")
        self.Bass_Bttn.setCheckable(True)
        self.Bass_Bttn.setAutoExclusive(True)
        self.Bass_Bttn.setObjectName("Bass_Bttn")
        self.verticalLayout_2.addWidget(self.Bass_Bttn)
        self.Bass_List_2 = QtWidgets.QListView(self.layoutWidget)
        self.Bass_List_2.setMinimumSize(QtCore.QSize(0, 0))
        self.Bass_List_2.setMaximumSize(QtCore.QSize(261, 111))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Black")
        self.Bass_List_2.setFont(font)
        self.Bass_List_2.setStyleSheet("QListView{\n"
"    background-color: rgb(255, 255, 255);\n"
"}")
        self.Bass_List_2.setObjectName("Bass_List_2")
        self.verticalLayout_2.addWidget(self.Bass_List_2)
        self.Alto_Bttn = QtWidgets.QPushButton(self.layoutWidget)
        self.Alto_Bttn.setMinimumSize(QtCore.QSize(161, 31))
        self.Alto_Bttn.setMaximumSize(QtCore.QSize(161, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.Alto_Bttn.setFont(font)
        self.Alto_Bttn.setStyleSheet("QPushButton{\n"
"background-color: rgb(195, 195, 195);\n"
"border-style: solid;\n"
"border-color: black;\n"
"border-width: 1px;\n"
"border-radius: 2px;\n"
"}\n"
"\n"
"QPushButton:checked{\n"
"    color:rgb(255, 255, 255);\n"
"    font-weight:bold;\n"
"    background-color: rgb(39, 39, 39);\n"
"    border-style: solid;\n"
"    border-color: white;\n"
"    border-width:1px;\n"
"    border-radius: 2px;\n"
"}")
        self.Alto_Bttn.setCheckable(True)
        self.Alto_Bttn.setAutoExclusive(True)
        self.Alto_Bttn.setObjectName("Alto_Bttn")
        self.verticalLayout_2.addWidget(self.Alto_Bttn)
        self.Alto_List_2 = QtWidgets.QListView(self.layoutWidget)
        self.Alto_List_2.setMinimumSize(QtCore.QSize(0, 0))
        self.Alto_List_2.setMaximumSize(QtCore.QSize(261, 111))
        self.Alto_List_2.setSizeIncrement(QtCore.QSize(261, 111))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Black")
        self.Alto_List_2.setFont(font)
        self.Alto_List_2.setStyleSheet("QListView{\n"
"    background-color: rgb(255, 255, 255);\n"
"}")
        self.Alto_List_2.setObjectName("Alto_List_2")
        self.verticalLayout_2.addWidget(self.Alto_List_2)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 28, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.widget = QtWidgets.QWidget(self.SideBar)
        self.widget.setGeometry(QtCore.QRect(41, 21, 157, 53))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Vocal_Icon = QtWidgets.QLabel(self.widget)
        self.Vocal_Icon.setMinimumSize(QtCore.QSize(51, 51))
        self.Vocal_Icon.setMaximumSize(QtCore.QSize(51, 51))
        self.Vocal_Icon.setText("")
        self.Vocal_Icon.setPixmap(QtGui.QPixmap(":/Raw_Image/MainLogo.png"))
        self.Vocal_Icon.setScaledContents(True)
        self.Vocal_Icon.setObjectName("Vocal_Icon")
        self.horizontalLayout.addWidget(self.Vocal_Icon)
        self.Vocal_Name = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.Vocal_Name.setFont(font)
        self.Vocal_Name.setStyleSheet("QLabel{\n"
"color: rgb(226, 226, 226);}")
        self.Vocal_Name.setObjectName("Vocal_Name")
        self.horizontalLayout.addWidget(self.Vocal_Name)
        self.MainBar = QtWidgets.QWidget(self.centralwidget)
        self.MainBar.setGeometry(QtCore.QRect(260, 0, 761, 651))
        self.MainBar.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.MainBar.setStyleSheet("QWidget{\n"
"    background-color: rgb(195, 195, 195);\n"
"    border:1px;\n"
"}")
        self.MainBar.setObjectName("MainBar")
        self.label = QtWidgets.QLabel(self.MainBar)
        self.label.setGeometry(QtCore.QRect(240, 70, 251, 231))
        self.label.setMinimumSize(QtCore.QSize(251, 231))
        self.label.setMaximumSize(QtCore.QSize(251, 231))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/Raw_Image/MainLogo.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.Tenor_Bttn.toggled['bool'].connect(self.Tenor_List_2.setHidden) # type: ignore
        self.Tenor_Bttn.toggled['bool'].connect(self.Tenor_List_2.setVisible) # type: ignore
        self.Soprano_Bttn.toggled['bool'].connect(self.Soprano_List_2.setHidden) # type: ignore
        self.Soprano_Bttn.toggled['bool'].connect(self.Soprano_List_2.setVisible) # type: ignore
        self.Bass_Bttn.toggled['bool'].connect(self.Bass_List_2.setHidden) # type: ignore
        self.Bass_Bttn.toggled['bool'].connect(self.Bass_List_2.setVisible) # type: ignore
        self.Alto_Bttn.toggled['bool'].connect(self.Alto_List_2.setHidden) # type: ignore
        self.Alto_Bttn.toggled['bool'].connect(self.Alto_List_2.setVisible) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.CV_Button.setText(_translate("MainWindow", "Categorize Voice"))
        self.TV_Button.setText(_translate("MainWindow", "Train Voice"))
        self.Tenor_Bttn.setText(_translate("MainWindow", "Tenor"))
        self.Soprano_Bttn.setText(_translate("MainWindow", "Soprano"))
        self.Bass_Bttn.setText(_translate("MainWindow", "Bass"))
        self.Alto_Bttn.setText(_translate("MainWindow", "Alto"))
        self.Vocal_Name.setText(_translate("MainWindow", "VOCALIZER"))
import resources_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())