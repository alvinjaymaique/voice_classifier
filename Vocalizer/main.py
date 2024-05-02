import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from RealTimeAudioAnalyzer import RealTimeAudioAnalyzer
from PyQt5.uic import loadUi
from PyQt5.QtCore import QObject, pyqtSignal

# Always have this class for RealTimeAudioAnalyzer
class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, audio_analyzer, audio_file):
        super().__init__()
        self.audio_analyzer = audio_analyzer
        self.audio_file = audio_file

    def run(self):
        self.audio_analyzer.start_analysis(self.audio_file, 12)
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('MacDsgn_Vocalizer.ui', self)

        # Find the child widgets
        self.frame2 = self.findChild(QFrame, 'frame_2')
        self.plot_layout = self.findChild(QVBoxLayout, 'plot_layout')

        # Create the RealTimeAudioAnalyzer instance
        self.audio_analyzer = RealTimeAudioAnalyzer()
        # self.audio_analyzer.start_record()
        self.start_training(self.audio_analyzer)
        # Get the figure from the RealTimeAudioAnalyzer
        self.figure = self.audio_analyzer.get_figure()

        # Create the Matplotlib plot canvas
        self.canvas = FigureCanvas(self.figure)

        # Add the canvas to the layout
        self.plot_layout.addWidget(self.canvas)
        

        

    def start_training(self, obj):
        # Start audio analysis in a separate thread
        # self.worker = Worker(self.audio_analyzer, "multiplenotes.mp3")
        self.worker = Worker(obj, "BASS.wav")
        self.worker.finished.connect(self.worker_finished)
        self.thread = threading.Thread(target=self.worker.run)
        self.thread.start()

    def worker_finished(self):
        print("Audio analysis finished")

    def closeEvent(self, event):
        # Stop the audio analyzer when the window is closed
        self.audio_analyzer.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())