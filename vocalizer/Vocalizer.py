import sys, os, shutil, time
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QToolButton, QPushButton, QDialog, QMessageBox, QTextEdit, QListView
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QStringListModel, QFileInfo, QDir, QTimer, QItemSelectionModel, QItemSelection
from resources_rc import *
from Ctgrz_Optn import Ui_Dialog  # Import the QDialog UI form from Ctgrz_Optn.py
from VoiceCategorizer import VoiceClassifier
from RealTimeAudioAnalyzer import RealTimeAudioAnalyzer
from InputFilename import InputFilename_Dialog

class Ctgrz_Optn_Dialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(Ctgrz_Optn_Dialog, self).__init__(parent)
        self.setupUi(self)

class InputFilenameDialog(QDialog, InputFilename_Dialog):
    def __init__(self, parent=None):
        super(InputFilenameDialog, self).__init__(parent)
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
        self.isAudioRunning = False


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

        # Instantiate cv list view
        self.cv_listview = self.findChild(QListView, 'CV_List')
        self.cv_listview.selectionModel().selectionChanged.connect(self.onclick_listview)  # Connect selectionChanged signal

        # Set up displayRecord QTextEdit
        self.display_record = self.findChild(QTextEdit, 'display_record')
        # self.display_record.setHtml('Test')

        # Stop Button
        self.btn_stop = self.findChild(QToolButton, "btn_stop")
        self.btn_stop.clicked.connect(self.stop_btn_clicked)

        self.displayTextList = ['''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
        <html><head><meta name="qrichtext" content="1" /><style type="text/css">
        p, li { white-space: pre-wrap; }
        </style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
        <p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:14pt;">''',
        '''</span></p></body></html>''']
        # self.display_record.setMarkdown(self.displayTextList[0]+'Test'+self.displayTextList[1])
        

        # Load files from cv_audio
        self.load_files()

        # For Categorize Option Dialog
        self.ctgrz_optn_dialog = Ctgrz_Optn_Dialog(self)
        self.ctgrz_optn_dialog.close()
        self.ctgrz_optn_dialog.pushButton_2.clicked.connect(self.import_button_clicked)   
        self.ctgrz_optn_dialog.Record_Button.clicked.connect(self.record_button_clicked)

        # Input filename in Categorize Voice Record
        self.input_filename = InputFilenameDialog(self)   
        self.input_filename.close()

        # Voice Classifier
        self.voice_classifier = VoiceClassifier()
        self.voice_classifier.load_model('model.keras', 'labels.json')

        # Real Time Audio Analyzer
        self.audio_analyzer = RealTimeAudioAnalyzer()

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
        self.ctgrz_optn_dialog.close()
        # isEnter = self.input_filename.get_input()
        # result_ex = self.input_filename.exec_()
        # print(result_ex)
        # if result_ex:
        #     pass    
        # else:
        #     print(False)
        # self.loop(result_ex)
        self.input_filename.show()


    
    def loop(self, result):
        if result:
            for i in range(3,0,-1):
                    self.display_record.setHtml(self.displayTextList[0]+'Recording in '+str(i)+self.displayTextList[1])
                    time.sleep(1)   
                # self.voice_classifier.record_audio('test_audio')
    
    def clicked_btn_enter(self):
        print('Success!')
        self.input_filename.close()
        print('Success!')
            
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

    def onclick_listview(self):
        self.isPauseDisplay = False
        self.Pause_Start_B.setIcon(QIcon("Raw_Image/Play_bttn.png"))

    def pause_start_action(self):
        # Toggle between Pause and Play icons
        try:
            if not self.isAudioRunning:
                filename = self.cv_listview.selectedIndexes()[0].data()
                self.audio_analyzer.play_audio_background('cv_audio\\'+filename)
                # self.voice_classifier.play_audio('cv_audio\\'+filename)
            else:
                pass
            print(filename)
        except Exception as e:
            print(e)
        # print(self.cv_listview.selectedIndexes()[0])
        # selected_item = self.cv_files[QItemSelectionModel.currentIndex(self.cv_model)]
        # if selected_item:
        #     print(selected_item)
        # else:
        #     print('No selected')
        if self.isPauseDisplay:
            print("Set to Play Button")
            self.Pause_Start_B.setIcon(QIcon("Raw_Image/Play_bttn.png"))
        elif not self.isPauseDisplay:
            print("Set to Pause Button")
            self.Pause_Start_B.setIcon(QIcon("Raw_Image/Pause_bttn.png"))
        self.isPauseDisplay = not self.isPauseDisplay

    def stop_btn_clicked(self):
        # print('HEyyy')
        self.audio_analyzer.stop_audio()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
