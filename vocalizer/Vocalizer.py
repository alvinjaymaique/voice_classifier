import sys, os, shutil, time, ctypes, threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QToolButton, QPushButton, QDialog, QMessageBox, QTextEdit, QListView, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QStringListModel, QFileInfo, QDir, QTimer, QItemSelectionModel, QItemSelection, QObject, pyqtSignal, QThread
from resources_rc import *
from Ctgrz_Optn import Ui_Dialog  # Import the QDialog UI form from Ctgrz_Optn.py
from VoiceCategorizer import VoiceClassifier
from RealTimeAudioAnalyzer import RealTimeAudioAnalyzer
from InputFilename import InputFilename_Dialog

# Make a destructor for killing a thread

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

class Counter(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    start_record = pyqtSignal()

    def __init__(self, function):
        super().__init__()
        self.function = function
        self.destroyed.connect(self.function) # When the instance of this class is destroyed it will call this function

    def count_down(self):
        for i in range(3, 0, -1):
            self.progress.emit(i) # Emit progress
            QThread.sleep(1)
        self.start_record.emit()
        QThread.sleep(6)
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

    # def play(self):
    #     from VoiceCategorizer import VoiceClassifier
    #     # For example:
    #     self.voice_classifier = VoiceClassifier()
    #     print(f"Play audio to {self.filename}")
    #     self.started.emit()
    #     self.voice_classifier.play_audio(self.filename)
    #     # Simulate recording for 5 seconds
    #     print("Play audio finished")
    #     self.finished.emit()

    def play(self):
        # self.voice_classifier = VoiceClassifier()
        print(f"Play audio from {self.filename}")
        # self.started.emit()
        # # Start playing audio in a separate thread
        # self.audio_thread = QThread()
        # self.audio_thread.started.connect(self._play_audio)
        # self.audio_thread.start()

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
            # if self.is_paused:
            #     print('wait')
            #     self.pause_event.wait()  # Wait until resume is called
            #     self.pause_event.clear()  # Clear the event flag
            # else:
            #     stream.write(data)
            #     data = wf.readframes(self.chunk_size)
            if self.is_paused:
                print('Paused. Waiting for resume...')
                self.pause_event.wait()  # Wait until resume is called
                self.pause_event.clear()  # Clear the event flag
                print('Resumed.')
            # print(self.is_paused)
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
        self.is_paused = True

    def resume(self):
        self.is_paused = False
        self.pause_event.set()  # Set the event flag to resume playback

    def stop(self):
        self.is_stop = True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("Vocalizer.ui", self)

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
        # self.thread1.start()  # Start the thread
        self.play_audio = PlayAudio('')

        self.Tenor_List_2.hide()
        self.Soprano_List_2.hide()
        self.Bass_List_2.hide()
        self.Alto_List_2.hide()

        # Connect button toggled signal to adjust button positions
        self.Tenor_Bttn.toggled.connect(self.adjust_button_positions)
        self.Soprano_Bttn.toggled.connect(self.adjust_button_positions)
        self.Bass_Bttn.toggled.connect(self.adjust_button_positions)
        self.Alto_Bttn.toggled.connect(self.adjust_button_positions)

        # Setup categorize button 
        self.cv_btn = self.findChild(QPushButton, 'CV_Button')
        self.cv_btn.clicked.connect(self.open_tv_button_dialog)
        # self.TV_Button.clicked.connect(self.open_tv_button_dialog)
        # self.CV_Button.clicked.connect(self.open_tv_button_dialog)    

        # Setup vertical layout
        self.v_layout = self.findChild(QVBoxLayout, 'verticalLayout')

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
        # Set its x and y coordinates
        # x = self.cv_btn.x() + self.cv_btn.width() + 100
        x = self.cv_btn.width() + self.cv_listview.width() - 50
        y = self.cv_btn.height() + self.cv_listview.height()
        h = self.ctgrz_optn_dialog.height()
        w = self.ctgrz_optn_dialog.width()
        self.ctgrz_optn_dialog.setGeometry(x, y, h, w)

        # # Input filename in Categorize Voice Record
        # self.input_filename = InputFilenameDialog(self)   
        # self.input_filename.close()

        # Voice Classifier
        self.voice_classifier = VoiceClassifier()
        self.voice_classifier.load_model('model.keras', 'labels.json')

        # Real Time Audio Analyzer
        self.audio_analyzer = RealTimeAudioAnalyzer()

        # # Define Worker
        # self.thread = QThread()
        # self.worker = Worker()
        # self.worker.moveToThread(self.thread)
        # self.worker.finished.connect(self.thread.quit)
        # self.worker.progress.connect(self.updateUI)
        # self.worker.finished.connect(self.taskFinished)
        
        # Check directories if it exists
        self.check_dir()
        

    def check_dir(self):
        # Create cv_audio directory if it does not exist
        if not os.path.exists('cv_audio'):
            os.makedirs('cv_audio')
        if not os.path.exists(self.import_audio_dir):
            os.makedirs(self.import_audio_dir)


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

            newfile_path = self.predict_audio(file_name)
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
        pass

    def predict_audio(self, filename):
        category = self.voice_classifier.predict_audio(filename)
        array_path =  filename.split('.')
        newfile_path = array_path[0]+'-'+category+'.'+array_path[1]
        return newfile_path

    def record_button_clicked(self):
        # Handle record button clicked event   
        self.ctgrz_optn_dialog.close()
        # self.loop(1)
        self.input_filename = InputFilenameDialog(self)  
        x = self.width()/2
        y = self.height()/2
        w = self.input_filename.width()
        h = self.input_filename.height()
        self.input_filename.setStyleSheet("background-color: white;")
        self.input_filename.setGeometry(x, y, w, h)
        # isEnter = self.input_filename.get_input()
        result_ex = self.input_filename.exec_()
        # del self.input_filename
        # print(result_ex)
        if result_ex:
            pass
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
            self.startTask()

            # Delete Counter object after a delay (e.g., 1 second)
            # QTimer.singleShot(7000, self.counter.deleteLater)
            print(self.input_filename.name)
        else:
            print(False)       
        # self.input_filename.show() 

    def startTask(self):
        self.thread.started.connect(self.counter.count_down)
        self.thread.start()

    def counting(self, value):
        # Just counting to prepare the user in recording
        self.display_record.setHtml(self.displayTextList[0]+'Recording in '+str(value)+'.'+self.displayTextList[1])
        
    def done_counting(self):
        # Indicate that the program is recording
        self.display_record.setHtml(self.displayTextList[0]+'Recording...'+self.displayTextList[1])

    def record_cv(self):
        # Recording the voice
        self.cur_path = self.import_audio_dir+'\\'+self.input_filename.name
        # self.cur_path = self.input_filename.name
        self.record_thread = threading.Thread(target=self.voice_classifier.record_audio, args=(self.cur_path,))
        self.record_thread.setDaemon = True
        self.record_thread.start()

    def done_recording(self):
        self.display_record.setHtml(self.displayTextList[0]+'Recording Saved'+self.displayTextList[1])  
        print('Done Recording')
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
            button.move(sidebar_center.x() - button_center.x(), button.y() + 1)  # Adjust vertical position

    def onclick_listview(self):
        self.isPauseDisplay = False
        self.Pause_Start_B.setIcon(QIcon("Raw_Image/Play_bttn.png"))

    def pause_start_action(self):
        # Toggle between Pause and Play icons
        
        # print(self.cv_listview.selectedIndexes()[0])
        # selected_item = self.cv_files[QItemSelectionModel.currentIndex(self.cv_model)]
        # if selected_item:
        #     print(selected_item)
        # else:
        #     print('No selected')
        if self.isPauseDisplay:
            print("Set to Play Button")
            self.Pause_Start_B.setIcon(QIcon("Raw_Image/Play_bttn.png"))
            try:
                print('Paused')
                self.play_audio.is_paused = True
                print(self.play_audio.is_paused)
                self.play_audio.pause()
            except:
                pass
        elif not self.isPauseDisplay:
            print("Set to Pause Button")
            try:
                print('Resumed')
                self.play_audio.resume()
                print(self.play_audio.is_paused)
            except:
                pass
            try:
                if not self.isAudioRunning or self.thread1.isRunning():
                    filename = self.cv_listview.selectedIndexes()[0].data()
                    # Define Counter
                    # self.thread1 = QThread()
                    audio_to_play = 'cv_audio\\'+filename
                    # self.play_audio = PlayAudio(audio_to_play)
                    self.play_audio.set_filename(audio_to_play)
                    # self.play_audio.play()
                    self.play_audio.moveToThread(self.thread1)
                    self.play_audio.finished.connect(self.thread1.quit)
                    # self.play_audio.started.connect(self.play_sel_audio)
                    # self.play_sel_audio.finished.conn
                    
                    self.start_audio()
                    # self.startTask()
                    
                    # self.voice_classifier.play_audio('cv_audio\\'+filename)
                else:
                    pass
                print(filename)
            except Exception as e:
                print(e)
            self.Pause_Start_B.setIcon(QIcon("Raw_Image/Pause_bttn.png"))
        self.isPauseDisplay = not self.isPauseDisplay
    
    def start_audio(self):
        self.thread1.started.connect(self.play_audio.play)
        self.thread1.start()

    def play_sel_audio(self, filepath):
        self.audio_analyzer.play_audio_background(filepath)

    def stop_btn_clicked(self):
        try:
            self.play_audio.stop()
        except:
            pass
        # print('HEyyy')
        # raise SystemExit()
        pass
        # self.audio_analyzer.stop_audio()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
