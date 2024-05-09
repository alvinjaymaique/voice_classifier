import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QToolButton, QPushButton, QDialog, QDialog
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtCore import QStringListModel, QFileInfo
from resources_rc import *
from Ctgrz_Optn import Ui_Dialog  # Import the QDialog UI form from Ctgrz_Optn.py

class Ctgrz_Optn_Dialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(Ctgrz_Optn_Dialog, self).__init__(parent)
        self.setupUi(self)
        self.Record_Button.clicked.connect(self.record_button_clicked)
        self.Import_button.clicked.connect(self.import_button_clicked)

    def import_button_clicked(self):
        print("Import button clicked")
        file_dialog = QFileDialog(self)
        file_dialog.setModal(True)  # Ensure the dialog is modal
        file_dialog.setNameFilter("Music files (*.mp3 *.wav *.ogg)")
        file_dialog.setDefaultSuffix("mp3")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        if file_dialog.exec_():
            print("File dialog executed")
            file_path = file_dialog.selectedFiles()[0]
            print("Selected file:", file_path)
        else:
            print("File dialog canceled")





    

    def record_button_clicked(self):
        # Handle record button clicked event
        pass

    def import_button_clicked(self):
        # Handle import button clicked event
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("Vocalizer.ui", self)
        self.TV_Button.clicked.connect(self.open_tv_button_dialog)
        self.CV_Button.clicked.connect(self.open_tv_button_dialog)
        # Create an instance of the Ctgrz_Optn dialog
        self.ctgrz_optn_dialog = Ctgrz_Optn_Dialog(self)
        
        self.cv_files = []
        self.cv_model = QStringListModel()
        self.CV_List.setModel(self.cv_model)
        self.Tenor_List_2.hide()
        self.Soprano_List_2.hide()
        self.Bass_List_2.hide()
        self.Alto_List_2.hide()

        # Connect button toggled signal to adjust button positions
        self.Tenor_Bttn.toggled.connect(self.adjust_button_positions)
        self.Soprano_Bttn.toggled.connect(self.adjust_button_positions)
        self.Bass_Bttn.toggled.connect(self.adjust_button_positions)
        self.Alto_Bttn.toggled.connect(self.adjust_button_positions)

        # Set up Pause_Start_B button
        self.Pause_Start_B = self.findChild(QToolButton, "Pause_Start_B")
        self.Pause_Start_B.setIcon(QIcon("C:/Users/User/Documents/SF_&_AI/VOCA/Raw_Image/Pause_bttn.png"))  # Set the path to the pause icon
        self.Pause_Start_B.setIconSize(QtCore.QSize(64, 64))  # Adjust the size as needed
        self.Pause_Start_B.clicked.connect(self.pause_start_action)  # Connect the clicked signal to the action

    def open_tv_button_dialog(self):
        self.openFileDialog("TV")

    def openFileDialog(self, button_type):
        # Open the Ctgrz_Optn dialog
        file_path = self.ctgrz_optn_dialog.exec_()
        if file_path:
            print(f"Selected {button_type} file:", file_path)
            if button_type == "CV":
                self.cv_files = [file_path]
                self.cv_model.setStringList(self.cv_files)
            file_info = QFileInfo(file_path)
            file_name = file_info.fileName()  # Extract filename from file path
            self.cv_model.setStringList([file_name])

        # After dialog closes, adjust button positions
        self.adjust_button_positions()

    def showEvent(self, event):
        super().showEvent(event)
        # Adjust button positions when the window is shown
        self.adjust_button_positions()

    def adjust_button_positions(self):
        # Find all the QPushButtons within the SideBar
        buttons = self.SideBar.findChildren(QPushButton)
        
        # Calculate the center position of the SideBar widget
        sidebar_center = self.SideBar.rect().center()

        for button in buttons:
            # Adjust the button position to be centered horizontally within the SideBar
            button_rect = button.rect()
            button_center = button_rect.center()
            button.move(sidebar_center.x() - button_center.x(), button.y() + 1)  # Adjust vertical position

    def pause_start_action(self):
        # Toggle between Pause and Play icons
        if self.Pause_Start_B.icon().isNull() or self.Pause_Start_B.icon().name() == "C:/Users/User/Documents/SF_&_AI/VOCA/Raw_Image/Pause_bttn.png":
            self.Pause_Start_B.setIcon(QIcon("C:/Users/User/Documents/SF_&_AI/VOCA/Raw_Image/Play_bttn.png"))
        else:
            self.Pause_Start_B.setIcon(QIcon("C:/Users/User/Documents/SF_&_AI/VOCA/Raw_Image/Pause_bttn.png"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
