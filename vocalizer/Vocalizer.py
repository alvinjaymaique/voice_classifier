import sys, os, shutil, time, ctypes, threading, json, wave
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QToolButton, QPushButton, QDialog, QMessageBox, QTextEdit, QListView, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QStringListModel, QFileInfo, QDir, QTimer, QItemSelectionModel, QItemSelection, QObject, pyqtSignal, QThread
from resources_rc import *
from Ctgrz_Optn import Ui_Dialog  # Import the QDialog UI form from Ctgrz_Optn.py
from VoiceCategorizer import VoiceClassifier
from RealTimeAudioAnalyzer import RealTimeAudioAnalyzer
from InputFilename import InputFilename_Dialog
from input_gender import Ui_input_gender_form
import numpy as np

# Checkpoint: Make the user train their voice make it record while following the vocal exercise audio
# Plan on how to record it dynamically based on the audio length. I just got an idea I just have to emit a signal when the audio is finished then I will end the recording

class Ctgrz_Optn_Dialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(Ctgrz_Optn_Dialog, self).__init__(parent)
        self.setupUi(self)

class InputFilenameDialog(QDialog, InputFilename_Dialog):
    def __init__(self, parent=None):
        super(InputFilenameDialog, self).__init__(parent)
        self.setupUi(self)

    def __del__(self):
        print('Input file name dialog deleted.')

class InputGenderDialog(QDialog, Ui_input_gender_form):
    # def __init__(self, parent=None):
    #     super(Ui_input_gender_form, self).__init__(parent)
    #     self.setupUi(self)

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)  # Call QDialog's __init__ method explicitly
        Ui_input_gender_form.__init__(self)  # Call Ui_input_gender_form's __init__ method explicitly
        self.setupUi(self)

    def __del__(self):
        print('Input gender dialog deleted.')

       

class Counter(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    start_record = pyqtSignal()
    play_background = pyqtSignal()

    def __init__(self, function, seconds=3, duration=61):
        super().__init__()
        self.function = function
        self.seconds = seconds
        self.duration = duration
        self.destroyed.connect(self.function) # When the instance of this class is destroyed it will call this function

    def count_down(self):
        self.play_background.emit()
        for i in range(self.seconds, 0, -1):
            self.progress.emit(i) # Emit progress
            QThread.sleep(1)
        self.start_record.emit()
        QThread.sleep(self.duration-self.seconds)
        self.finished.emit() # Signal task completion

class PlayAudio(QObject):
    started = pyqtSignal()
    progress = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, filename):
        from threading import Event
        import wave, pyaudio
        super().__init__()
        self.filename = filename
        self.chunk_size = 1024
        self.pa = pyaudio.PyAudio()
        self.is_paused = False
        self.is_stop = False
        self.pause_event = Event()

    def play(self):
        print(f"Play audio from {self.filename}")
        self.started.emit()
        self.audio_thread = QThread()
        self.audio_thread.started.connect(self._play_audio)
        self.moveToThread(self.audio_thread)  # Move object to new thread
        self.audio_thread.start()

    def _play_audio(self):
        import wave
        wf = wave.open(self.filename, 'rb')
        stream = self.pa.open(format=self.pa.get_format_from_width(wf.getsampwidth()),
                              channels=wf.getnchannels(),
                              rate=wf.getframerate(),
                              output=True)
        self.is_paused = False  # Start with audio playing
        data = wf.readframes(self.chunk_size)
        while data and not self.is_stop:
            if self.is_paused:
                print('Paused. Waiting for resume...')
                self.pause_event.wait()  # Wait until resume is called
                self.pause_event.clear()  # Clear the event flag
                print('Resumed.')
            stream.write(data)
            data = wf.readframes(self.chunk_size)

        stream.stop_stream()
        stream.close()
        wf.close()
        print("Audio playback finished")
        self.finished.emit()

    def set_filename(self, filename):
        self.filename = filename

    def pause(self):
        print('Paused')
        self.is_paused = True

    def resume(self):
        print('Resumed')
        self.is_paused = False
        self.pause_event.set()  # Set the event flag to resume playback

    def stop(self):
        print('Stopped')
        self.finished.emit()
        self.is_stop = True   

from PyQt5.QtCore import QThread, pyqtSignal

class RecordThread(QThread):
    finished = pyqtSignal()

    def __init__(self, voice_classifier, cur_path, duration):
        super().__init__()
        self.voice_classifier = voice_classifier
        self.cur_path = cur_path
        self.duration = duration

    def run(self):
        self.voice_classifier.record_audio(self.cur_path, self.duration)
        # for _ in range(int(self.duration), 0, -1):
        #     QThread.sleep(1)
        print('Record Finished')
        self.finished.emit()

    def stop(self):
        self.voice_classifier.stop_recording()
        self.voice_classifier.stop_record = True

class PlayBackgroundThread(QThread):
    finished = pyqtSignal()

    def __init__(self, audio_analyzer, cur_path):
        super().__init__()
        self.audio_analyzer = audio_analyzer
        self.cur_path = cur_path

    def run(self):
        self.audio_analyzer.play_audio_background(self.cur_path)
        self.finished.emit()

class ScoreThread(QThread):
    calculating = pyqtSignal(str)
    finished = pyqtSignal(str)  # Define a signal to emit the result

    def __init__(self, audio_analyzer, cur_path, dir_current_csv):
        super().__init__()
        self.audio_analyzer = audio_analyzer
        self.cur_path = cur_path
        self.dir_current_csv = dir_current_csv

    def run(self):
        cur_path = self.cur_path.split('.')[0]
        self.audio_analyzer.saveto_csv(cur_path)
        # result = self.audio_analyzer.read_csv(cur_path)   
        self.calculating.emit('Score Calculating...')
        score = self.audio_analyzer.score_dtw(self.audio_analyzer.read_csv(cur_path), self.audio_analyzer.read_csv(self.dir_current_csv))
        message = 'Your score is: '+ str(f"{score:.2f}") 
        print(message)
        self.finished.emit(message)  # Emit the result when finished

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("Vocalizer.ui", self)

        # Voice Classifier
        self.voice_classifier = VoiceClassifier()
        self.voice_classifier.load_model('model.keras', 'labels.json')

        # Real Time Audio Analyzer
        self.audio_analyzer = RealTimeAudioAnalyzer() 
        
        # Variables
        self.isPauseDisplay = True
        self.isDialogOpen = False
        self.cv_files = []
        self.cv_model = QStringListModel()  
        self.CV_List.setModel(self.cv_model)
        self.isAudioRunning = False
        self.cur_path = ''
        self.import_audio_dir = 'recordings'
        self.play_audio = None  # Initialize play_audio attribute
        self.thread1 = QThread()  # Create the QThread object once
        self.play_audio = PlayAudio('')
        self.prev_selected_file = ''
        self.isMale = None
        self.tv_selected_dir = ''
        self.tv_selected_item = ''
        # list of seconds for vocal warmups
        self.list_seconds = []
        self.path_for_seconds = ''
        self.seconds = None

        self.dir_current_csv = None
        self.thread4 = None
        # self.record_thread_tv = None
        # self.record_thread_tv = RecordThread(self.voice_classifier, self.cur_path, duration=120)


        # # QMain bar setup
        # self.mainbar = self.findChild(QWidget, 'MainBar')

        # For training setup
        self.tenor_list = self.findChild(QListView, 'Tenor_List_2')
        self.soprano_list = self.findChild(QListView, 'Soprano_List_2')
        self.bass_list = self.findChild(QListView, 'Bass_List_2')
        self.alto_list = self.findChild(QListView, 'Alto_List_2')

        self.tenor_files = []
        self.tenor_model = QStringListModel()  
        self.tenor_list.setModel(self.tenor_model)

        self.soprano_files = []
        self.soprano_model = QStringListModel()  
        self.soprano_list.setModel(self.soprano_model)

        self.bass_files = []
        self.bass_model = QStringListModel()  
        self.bass_list.setModel(self.bass_model)

        self.alto_files = []
        self.alto_model = QStringListModel()  
        self.alto_list.setModel(self.alto_model)

        self.categories = [self.alto_list, self.bass_list, self.tenor_list, self.soprano_list]
        for category in self.categories:
            # category.selectionModel().selectionChanged.connect(self.category_listview)
            category.clicked.connect(self.category_listview)
            # category.focusOutEvent()

        self.Tenor_List_2.hide()
        self.Soprano_List_2.hide()
        self.Bass_List_2.hide()
        self.Alto_List_2.hide()
        #

        # Connect button toggled signal to adjust button positions
        self.Tenor_Bttn.toggled.connect(self.adjust_button_positions)
        self.Soprano_Bttn.toggled.connect(self.adjust_button_positions)
        self.Bass_Bttn.toggled.connect(self.adjust_button_positions)
        self.Alto_Bttn.toggled.connect(self.adjust_button_positions)

        # Setup categorize button 
        self.cv_btn = self.findChild(QPushButton, 'CV_Button')
        self.cv_btn.clicked.connect(self.open_tv_button_dialog)   
        self.cv_btn.clicked.connect(self.adjust_button_positions)
        self.cv_btn.clicked.connect(self.clear_list_clicked)

        self.tv_btn = self.findChild(QPushButton, 'TV_Button')
        self.tv_btn.clicked.connect(self.adjust_button_positions)
        self.tv_btn.clicked.connect(self.clear_list_clicked)

        # Setup vertical layout
        self.v_layout = self.findChild(QVBoxLayout, 'verticalLayout')

        # Set up Pause_Start_B button
        self.btn_pause_start = self.findChild(QToolButton, "Pause_Start_B")
        self.btn_pause_start.setIcon(QIcon("Raw_Image/Pause_bttn.png"))  # Set the path to the pause icon
        self.btn_pause_start.setIconSize(QtCore.QSize(64, 64))  # Adjust the size as needed
        self.btn_pause_start.clicked.connect(self.pause_start_action)  # Connect the clicked signal to the action

        # Instantiate cv list view
        self.cv_listview = self.findChild(QListView, 'CV_List')
        self.cv_listview.selectionModel().selectionChanged.connect(self.onclick_listview)  # Connect selectionChanged signal
        

        # Set up displayRecord QTextEdit
        self.display_record = self.findChild(QTextEdit, 'display_record')
        # self.display_record.setHtml('Test')

        # Stop Button
        self.btn_stop = self.findChild(QToolButton, "btn_stop")
        self.btn_stop.clicked.connect(self.stop_btn_clicked)

        # Practice Button Setup
        self.btn_practice = self.findChild(QPushButton, 'btn_practice')
        self.btn_practice.clicked.connect(self.practice_clicked)
        self.btn_practice.setEnabled(False)
        self.btn_practice.setVisible(False)

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
        # Set its x and y coordinates
        x = self.cv_btn.width() + self.cv_listview.width() - 50
        y = self.cv_btn.height() + self.cv_listview.height()
        h = self.ctgrz_optn_dialog.height()
        w = self.ctgrz_optn_dialog.width()
        self.ctgrz_optn_dialog.setGeometry(x, y, h, w)

        # Check directories if it exists
        self.check_dir()

    def check_dir(self):
        # Create cv_audio directory if it does not exist   
        self.create_dir('cv_audio')
        self.create_dir(self.import_audio_dir)
        self.create_dir('recordings')
        self.create_dir('train_audio')
        self.create_dir('temp')
        categories = ['bass', 'tenor', 'alto', 'soprano']
        for category in categories:
            path = 'train_audio\\'+category
            if not os.path.exists(path):
                os.makedirs(path) 
            if not os.path.exists(path+'\\audio'):
                os.makedirs(path+'\\audio')
            if not os.path.exists(path+'\\csv'):
                os.makedirs(path+'\\csv')

    def create_dir(self, dir):
         if not os.path.exists(dir):
            os.makedirs(dir)    

    def load_files(self):
        directory = QDir('cv_audio')
        file_list = directory.entryList()
        file_list = [file for file in file_list if file not in ['.','..']]
        for file_name in file_list:
            self.cv_files.append(file_name)
        self.cv_model.setStringList(self.cv_files)
        
        # Just call here for the train voice
        print(directory.entryList())
        self.load_train_files(self.bass_files, self.bass_model)
        self.load_train_files(self.tenor_files, self.tenor_model, dir='tenor')
        self.load_train_files(self.alto_files, self.alto_model, dir='alto')
        self.load_train_files(self.soprano_files, self.soprano_model, dir='soprano')

    def load_train_files(self, files, model,  dir='bass',):
        dir='train_audio\\'+dir+'\\audio'
        directory = QDir(dir)
        file_list = directory.entryList()
        file_list = [file for file in file_list if file not in ['.','..']]
        for file_name in file_list:
            files.append(file_name)
            print(file_name)
        model.setStringList(files)

    def category_listview(self):
        sender = self.sender()  # Get the sender object (the list view that emitted the signal)
        selected_item = sender.selectedIndexes()[0].data()
        # self.index_for_list_sec = 
        directories = QDir('train_audio')
        for directory in directories:
            if directory in selected_item:
                self.tv_selected_dir = directory
                if selected_item.startswith(directory):
                    self.index_for_list_sec = selected_item[len(directory):].split('.')[0]  # Remove the prefix string1 from string2
                    print(self.index_for_list_sec)
                    self.dir_current_csv = 'train_audio\\'+directory+'\\csv\\'+directory+self.index_for_list_sec
                print(directory)
        
        # self.alto_list.selectedIndexes()[0].data()
        self.path_for_seconds = 'train_audio\\'+self.tv_selected_dir+'\\seconds.json'
        self.tv_selected_item = 'train_audio\\'+self.tv_selected_dir+'\\audio\\'+selected_item
        if sender == self.alto_list:
            # Do something for the alto_list
            print("Alto list view clicked")
        elif sender == self.bass_list:
            # Do something for the bass_list
            print("Bass list view clicked")
        elif sender == self.tenor_list:
            # Do something for the tenor_list
            print("Tenor list view clicked")
        elif sender == self.soprano_list:
            # Do something for the soprano_list
            print("Soprano list view clicked")
        print(self.tv_selected_item)
        self.btn_practice.setEnabled(True)
        self.btn_practice.setVisible(True)

    def clear_list_clicked(self):
        self.cv_listview.selectionModel().clearSelection()
        for category in self.categories:
            category.selectionModel().clearSelection()
        
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
        file_dialog.setDefaultSuffix("wav")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setDirectory(self.import_audio_dir)

        if file_dialog.exec_():
            # Copy file to a specific folder
            destination_folder = "cv_audio"  # Change this to your desired destination folder
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            file_path = file_dialog.selectedFiles()[0]
            print(file_path)
            # print(f"Selected {button_type} file:", file_path)
            file_name = os.path.basename(file_path)
            print(file_name)
            
            # Copy file
            shutil.copy(file_path, os.curdir)
            gender = self.create_gender_dialog() # 0=Male 1=Female
            newfile_path = self.predict_audio(file_name, gender)
            # # destination_path = os.path.join(destination_folder, file_name)
            destination_path = os.path.join(destination_folder, newfile_path)

            if not os.path.exists(destination_path):
                shutil.copy(file_path, destination_path)
                # if button_type == "CV":
                self.cv_add_list(newfile_path)
            else:
                QMessageBox.critical(self, 'Error', f'The {file_name} file already exists')
            os.remove(file_name)

    def cv_add_list(self, path):
        self.cv_files.append(path)
        self.cv_model.setStringList(self.cv_files)

    def predict_audio(self, filename, gender):
        # 0=male 1=female
        category = self.voice_classifier.predict_audio(filename)
        print('This is the category: ', category)
        # Increase accuracy since dataset is few
        if gender==0 and (category=='alto' or category=='soprano'):
            category = 'tenor'
        elif gender==1 and (category=='bass' or category=='tenor'):
            category = 'alto'
        else:
            pass
        array_path =  filename.split('.')
        newfile_path = array_path[0]+'-'+category+'.'+array_path[1]
        return newfile_path

    def record_button_clicked(self):
        # Handle record button clicked event   
        self.ctgrz_optn_dialog.close()
        # self.loop(1)
        self.input_filename = InputFilenameDialog(self)  
        self.center_dialog(self.input_filename)

        result_ex = self.input_filename.exec_()
        if result_ex:
            self.btn_practice.setVisible(False)
            self.btn_practice.setEnabled(False)
            # Define Counter
            self.thread = QThread()
            self.counter = Counter(self.save_recorded)
            self.counter.moveToThread(self.thread)
            self.counter.finished.connect(self.thread.quit)
            self.counter.progress.connect(self.counting)
            self.counter.start_record.connect(self.done_counting) 
            self.counter.start_record.connect(self.record_cv)
            self.counter.finished.connect(self.done_counting) 
            self.counter.finished.connect(self.done_recording)
            # self.counter.deleteLater()
            self.start_task()
            print(self.input_filename.name)
        else:
            print(False)       
        # self.input_filename.show() 

    def create_gender_dialog(self):
        self.input_gender = InputGenderDialog(self)
        self.center_dialog(self.input_gender)
        self.btn_male = self.input_gender.findChild(QPushButton, 'btn_male')
        self.btn_female = self.input_gender.findChild(QPushButton, 'btn_female')
        self.btn_female.clicked.connect(self.input_gender.accept)
        self.btn_male.clicked.connect(self.input_gender.reject)
        return self.input_gender.exec_()

    def center_dialog(self, dialog):
        if isinstance(dialog, QDialog):
            x = self.width()/2
            y = self.height()/2
            w = dialog.width()
            h = dialog.height()
            dialog.setStyleSheet("background-color: white;")
            dialog.setGeometry(x, y, w, h)
        pass

    def start_task(self):
        self.thread.started.connect(self.counter.count_down)
        self.thread.start()

    def counting(self, value):
        # Just counting to prepare the user in recording
        self.display_record.setHtml(self.displayTextList[0]+'Recording in '+str(value)+'.'+self.displayTextList[1])
        
    def done_counting(self):
        # Indicate that the program is recording
        self.display_record.setHtml(self.displayTextList[0]+'Recording...'+self.displayTextList[1])

    def record_cv(self, isCV = True):
        if isCV:
            # Recording the voice
            self.cur_path = self.import_audio_dir+'\\'+self.input_filename.name
            # self.cur_path = self.input_filename.name
            self.btn_pause_start.setEnabled(False)
            self.btn_stop.setEnabled(False)
            self.record_thread = threading.Thread(target=self.voice_classifier.record_audio, args=(self.cur_path, 60))
            self.record_thread.setDaemon = True
            self.record_thread.start()
        else:
            duration = np.round(self.audio_analyzer.get_audio_duration(self.tv_selected_item)) - self.seconds + 1
            # duration = np.round(self.get_audio_duration(self.tv_selected_item)) - self.seconds + 1
            print('Duration: ',duration)
            self.thread2 = QThread()
            self.record_thread_tv = RecordThread(self.voice_classifier, self.cur_path, duration=duration)
            self.record_thread_tv.moveToThread(self.thread2)
            # self.record_thread_tv.deleteLater()
            print('Current_path: '+self.cur_path)
            self.record_thread_tv.finished.connect(lambda: self.get_score(self.cur_path))
            self.record_thread_tv.finished.connect(self.thread2.quit)
            self.thread2.started.connect(self.record_thread_tv.run)
            self.thread2.start()
            print('isCV is False')

    def done_recording(self, isPractice=False):
        if not isPractice:
            self.display_record.setHtml(self.displayTextList[0]+'Recording Saved'+self.displayTextList[1])  
        else:
            self.display_record.setHtml(self.displayTextList[0]+'Calculating the score...'+self.displayTextList[1])  
            pass
        print('Done Recording')
        self.btn_pause_start.setEnabled(True)
        self.btn_stop.setEnabled(True)
        # self.save_recorded()
       
    def save_recorded(self):
        # Categorize the voice and rename it
        print(self.cur_path)
        try:
            new_name = self.voice_classifier.predict_audio(self.cur_path) 
            os.rename(self.cur_path, new_name)
            self.cv_add_list(new_name)   
            self.update_cv_list(new_name)
        except Exception as e:
            print('No such file or directory Error')

        
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
            button.move(sidebar_center.x() - button_center.x(), button.y())  # Adjust vertical position

    def onclick_listview(self):
        self.isPauseDisplay = False
        self.btn_practice.setEnabled(False)
        self.btn_practice.setVisible(False)
        self.btn_pause_start.setIcon(QIcon("Raw_Image/Play_bttn.png"))

    def pause_start_action(self):
        # Toggle between Pause and Play icons
        if self.isPauseDisplay:
            print("Set to Play Button")
            self.change_pause_start_dis()
            try:
                self.play_audio.is_paused = True
                self.play_audio.pause()
            except:
                pass
        elif not self.isPauseDisplay:
            print("Set to Pause Button")
            try:
                self.play_audio.resume()
            except:
                pass
            try:
                cur_filename = self.cv_listview.selectedIndexes()[0].data()
                is_different_file = (self.prev_selected_file != cur_filename)
                print('The file is different: ',is_different_file)
                if not self.thread1.isRunning() or is_different_file:

                    # Terminate the thread1 if it is running
                    if self.thread1.isRunning():
                        self.thread1.terminate()

                    self.prev_selected_file = cur_filename
                    print(self.prev_selected_file)

                    # Define new thread and self.play_audio worker
                    self.thread1 = QThread()
                    audio_to_play = 'cv_audio\\'+self.prev_selected_file
                    self.play_audio = PlayAudio( audio_to_play)
                    self.play_audio.moveToThread(self.thread1)
                    self.play_audio.started.connect(lambda: self.display_label('Playing...'))
                    self.play_audio.finished.connect(self.change_pause_start_dis)
                    self.play_audio.finished.connect(lambda: self.display_label('Vocalizer'))
                    self.play_audio.finished.connect(self.thread1.quit)
                    self.start_audio()
                else:
                    pass
            except Exception as e:
                print(e)
            self.change_pause_start_dis()

    def display_label(self, string):
        self.display_record.setHtml(self.displayTextList[0]+string+self.displayTextList[1])

    def change_pause_start_dis(self):
        if self.isPauseDisplay:
            self.btn_pause_start.setIcon(QIcon("Raw_Image/Play_bttn.png"))
        else:
            self.btn_pause_start.setIcon(QIcon("Raw_Image/Pause_bttn.png"))
        self.isPauseDisplay = not self.isPauseDisplay
    
    
    def start_audio(self):
        self.thread1.started.connect(self.play_audio.play)
        self.thread1.start()

    def stop_btn_clicked(self):
        try:
            self.play_audio.stop()
            self.play_audio.disconnect()
            # self.play_audio.deleteLater()
            print('play_audio stopped')
        except Exception as e:
            print(e)

    def practice_clicked(self):
        print('Start Practice')
        path = self.tv_selected_item
         # Handle record button clicked event   
        self.btn_practice.setVisible(False)
        self.cur_path = 'temp\\0'
        index = int(self.index_for_list_sec)
        self.list_seconds = self.read_json(self.path_for_seconds)
        self.seconds = self.list_seconds[index]
        # Define Counter
        self.btn_pause_start.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.thread = QThread()
        self.counter = Counter(self.save_recorded, seconds=self.seconds)
        self.counter.moveToThread(self.thread)
        self.counter.finished.connect(self.thread.quit)
        self.counter.progress.connect(self.counting)
        self.counter.start_record.connect(self.done_counting) 
        self.counter.start_record.connect(lambda: self.record_cv(isCV=False)) 
        self.counter.play_background.connect(lambda: self.play_vocal_exercise(path=path))
        self.counter.finished.connect(self.done_counting) 
        self.counter.finished.connect(lambda: self.done_recording(isPractice=True))
        self.counter.deleteLater()
        self.start_task()

    def play_vocal_exercise(self, path):
        self.thread3 = QThread()
        self.play_vocal = PlayBackgroundThread(self.audio_analyzer, path)
        self.play_vocal.moveToThread(self.thread3)
        self.play_vocal.finished.connect(self.thread3.quit)
        # self.play_vocal.finished.connect(self.tv_stop_recording)
        self.play_vocal.deleteLater()
        self.play_vocal.started.connect(self.play_vocal.run)
        # print(self.cur_path)
        # self.play_vocal.finished.connect(lambda: self.get_score(self.cur_path))
        self.play_vocal.run()
        # self.audio_analyzer.play_audio_background(path)

    def get_score(self, cur_path):
        if self.thread4 is not None:
            if self.thread4.isRunning():
                self.thread4.terminate()
        # Create a thread instance
        self.thread4 = QThread()
        self.score_thread = ScoreThread(self.audio_analyzer, cur_path, self.dir_current_csv)
        # Connect the thread's finished signal to a slot
        self.score_thread.calculating.connect(self.display_label)
        self.score_thread.moveToThread(self.thread4)
        self.score_thread.finished.connect(self.thread4.quit)
        self.score_thread.finished.connect(self.display_label)

        self.score_thread.start()

    def tv_stop_recording(self):
        if self.record_thread_tv is not None:
            self.record_thread_tv.stop()
            print('Stopped')
        else: 
            print('record_thread_tv is None')
        # self.record_thread_tv = True

    def write_json(self, data, filepath):
        with open(filepath, 'w') as f:
            json.dump(data, f)

    def read_json(self, filepath):
        # Open the file and read the list from JSON
        with open(filepath, 'r') as f:
            recovered_data = json.load(f)
        return recovered_data
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
