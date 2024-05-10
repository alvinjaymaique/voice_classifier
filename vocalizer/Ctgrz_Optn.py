# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ctgrz_Optn.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(200, 70)
        Dialog.setMinimumSize(QtCore.QSize(200, 64))
        Dialog.setMaximumSize(QtCore.QSize(200, 70))
        Dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Remove title bar and buttons
        font = QtGui.QFont()
        font.setKerning(False)
        Dialog.setFont(font)
        Dialog.setStyleSheet("QDialog{\n"
"background-color: rgb(106, 106, 106);}")
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(10, 0, 182, 68))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.Record_Button = QtWidgets.QPushButton(self.widget)
        self.Record_Button.setMinimumSize(QtCore.QSize(180, 30))
        self.Record_Button.setMaximumSize(QtCore.QSize(180, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.Record_Button.setFont(font)
        self.Record_Button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Record_Button.setStyleSheet("QPushButton{\n"
"background-color: rgb(238, 238, 238);\n"
"border-style: solid;\n"
"border-color: black;\n"
"border-width: 2px;\n"
"border-radius: 5px;}\n"
"\n"
"QPushButton:checked{\n"
"    color:rgb(255, 255, 255);\n"
"    font-weight:bold;\n"
"    background-color: rgb(39, 39, 39);\n"
"    border-style: solid;\n"
"    border-color: white;\n"
"    border-width:2px;\n"
"    border-radius: 5px;\n"
"}")
        self.Record_Button.setCheckable(True)
        self.Record_Button.setAutoExclusive(True)
        self.Record_Button.setObjectName("Record_Button")
        self.verticalLayout.addWidget(self.Record_Button)
        self.pushButton_2 = QtWidgets.QPushButton(self.widget)
        self.pushButton_2.setMinimumSize(QtCore.QSize(180, 30))
        self.pushButton_2.setMaximumSize(QtCore.QSize(180, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_2.setStyleSheet("QPushButton{\n"
"background-color: rgb(238, 238, 238);\n"
"border-style: solid;\n"
"border-color: black;\n"
"border-width: 2px;\n"
"border-radius: 5px;}\n"
"\n"
"QPushButton:checked{\n"
"    color:rgb(255, 255, 255);\n"
"    font-weight:bold;\n"
"    background-color: rgb(39, 39, 39);\n"
"    border-style: solid;\n"
"    border-color: white;\n"
"    border-width:2px;\n"
"    border-radius: 5px;\n"
"}")
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setAutoExclusive(True)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.Record_Button.setText(_translate("Dialog", "Record Audio"))
        self.pushButton_2.setText(_translate("Dialog", "Import Audio"))


# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     Dialog = QtWidgets.QDialog()
#     ui = Ui_Dialog()
#     ui.setupUi(Dialog)
#     Dialog.show()
#     sys.exit(app.exec_())