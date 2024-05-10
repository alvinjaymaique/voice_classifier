import sys, os, shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QToolButton, QPushButton, QDialog, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QStringListModel, QFileInfo, QDir
from resources_rc import *
from Ctgrz_Optn import Ui_Dialog  # Import the QDialog UI form from Ctgrz_Optn.py
from VoiceCategorizer import VoiceClassifier

class Ctgrz_Optn_Dialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(Ctgrz_Optn_Dialog, self).__init__(parent)
        self.setupUi(self)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("Vocalizer.ui", self)
        self.TV_Button.clicked.connect(self.open_tv_button_dialog)
        self.CV_Button.clicked.connect(self.open_tv_button_dialog)    

        # Variables
        self.isPauseDisplay = True
        self.isDialogOpen = False
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
        self.Pause_Start_B.setIcon(QIcon("Raw_Image/Pause_bttn.png"))  # Set the path to the pause icon
        self.Pause_Start_B.setIconSize(QtCore.QSize(64, 64))  # Adjust the size as needed
        self.Pause_Start_B.clicked.connect(self.pause_start_action)  # Connect the clicked signal to the action

        # # Create an instance of the Ctgrz_Optn dialog
        # self.dialog = QtWidgets.QDialog()
        # self.dialog.setParent(MainWindow)
        # x = (self.pushButton.x()+10)+self.pushButton.width()
        # self.dialog.move(x, self.pushButton.y())
        # self.ctgrz_optn_dialog = Ui_Dialog()
        # self.ctgrz_optn_dialog.setupUi(self.dialog)
        # self.dialog.exec_()
        # self.ctgrz_optn_dialog = Ui_Dialog(MainWindow)

        # Load files from cv_audio
        self.load_files()

        # For Categorize Option Dialog
        self.ctgrz_optn_dialog = Ctgrz_Optn_Dialog(self)
        self.ctgrz_optn_dialog.close()
        self.ctgrz_optn_dialog.pushButton_2.clicked.connect(self.import_button_clicked)   
        self.ctgrz_optn_dialog.Record_Button.clicked.connect(self.record_button_clicked)

        # Voice Classifier
        self.voice_classifier = VoiceClassifier()
        self.voice_classifier.load_model('model.keras', 'labels.json')

    def load_files(self):
        directory = QDir('cv_audio')
        file_list = directory.entryList()
        file_list = [file for file in file_list if file not in ['.','..']]
        for file_name in file_list:
            self.cv_files.append(file_name)
        self.cv_model.setStringList(self.cv_files)

    def open_tv_button_dialog(self):
        self.openFileDialog("TV")

    def openFileDialog(self, button_type):
        if self.isDialogOpen:
            self.ctgrz_optn_dialog.close()
            self.isDialogOpen = False
        else:
            # self.ctgrz_optn_dialog = Ctgrz_Optn_Dialog(self)
            self.ctgrz_optn_dialog.show()
            self.isDialogOpen = True

        # Open the Ctgrz_Optn dialog
        file_path = self.ctgrz_optn_dialog.exec_()
        if file_path and button_type == "CV":
            print(f"Selected {button_type} file:", file_path)
            self.update_cv_list(file_path)
        # # After dialog closes, adjust button positions
        # self.adjust_button_positions()

    def import_button_clicked(self):
        # file_dialog = QFileDialog(self.parent())
        file_dialog = QFileDialog()
        file_dialog.setModal(True)  # Ensure the dialog is modal
        file_dialog.setNameFilter("Music files (*.mp3 *.wav *.ogg)")
        file_dialog.setDefaultSuffix("mp3")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)

        if file_dialog.exec_():
            # Copy file to a specific folder
            destination_folder = "cv_audio"  # Change this to your desired destination folder
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            file_path = file_dialog.selectedFiles()[0]
            # print(f"Selected {button_type} file:", file_path)
            file_name = os.path.basename(file_path)
            category = self.voice_classifier.predict_audio(file_name)
            array_path =  file_name.split('.')
            
            newfile_path = array_path[0]+'-'+category+'.'+array_path[1]
            destination_path = os.path.join(destination_folder, newfile_path)
            # destination_path = os.path.join(destination_folder, file_name)

            if not os.path.exists(destination_path):
                shutil.copy(file_path, destination_path)
                # if button_type == "CV":
                self.cv_files.append(newfile_path)
                # self.cv_files.append(file_name)
                self.cv_model.setStringList(self.cv_files)
                if file_path:
                    file_info = QFileInfo(file_path)
                    file_name = file_info.fileName()  # Extract filename from file path
                    # self.cv_model.setStringList([file_name])
                # QMessageBox.information(self, 'Success', 'File successfully copied')
            else:
                QMessageBox.critical(self, 'Error', f'The {file_name} file already exists')


    def record_button_clicked(self):
        # Handle record button clicked event
        pass

    def update_cv_list(self, file_path):
        print(f"Selected CV file: {file_path}")
        # Add the selected file path to the CV_List
        self.cv_files.append(file_path)
        self.cv_model.setStringList(self.cv_files)

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

        if self.isPauseDisplay:
            print("Set to Play Button")
            self.Pause_Start_B.setIcon(QIcon("Raw_Image/Play_bttn.png"))
        elif not self.isPauseDisplay:
            print("Set to Pause Button")
            self.Pause_Start_B.setIcon(QIcon("Raw_Image/Pause_bttn.png"))
        self.isPauseDisplay = not self.isPauseDisplay

        # print(self.Pause_Start_B.icon().name())
        # if self.Pause_Start_B.icon().isNull() or self.Pause_Start_B.icon().name() == "Raw_Image/Pause_bttn.png":
        #     print('Set to play')
        #     self.Pause_Start_B.setIcon(QIcon("Raw_Image/Play_bttn.png"))
        # else:
        #     print('Set to pause')
        #     self.Pause_Start_B.setIcon(QIcon("Raw_Image/Pause_bttn.png"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
