import pyaudio
import numpy as np
import librosa
import matplotlib.pyplot as plt
import threading
import time
import pydub
from pydub.playback import play

# class RealTimeAudioAnalyzer:
#     def __init__(self, buffer_size=4096, channels=1, format=pyaudio.paFloat32, rate=44100):
#         self.buffer_size = buffer_size
#         self.channels = channels
#         self.format = format
#         self.rate = rate
#         self.notes = [' ','C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', ' ']
#         self.mapping = {'C':1, 'C#':2, 'D':3, 'D#':4, 'E':5, 'F':6, 'F#':7, 'G':8, 'G#':9, 'A':10, 'A#':11, 'B':12}
#         self.musical_note = 'C'
#         self.new_note_event = threading.Event()  # Event to signal when a new note is detected

#         # Create PyAudio stream
#         self.p = pyaudio.PyAudio()
#         self.stream = self.p.open(format=self.format,
#                                   channels=self.channels,
#                                   rate=self.rate,
#                                   input=True,
#                                   frames_per_buffer=self.buffer_size)

#         # Create a figure for the plot
#         self.fig = plt.figure()
#         self.ax = self.fig.add_subplot(111)
#         self.ax.set_xlim(0, 10)
#         self.ax.set_ylim(0, len(self.notes))
#         self.ax.set_yticks(range(0, len(self.notes)))
#         self.ax.set_yticklabels(self.notes)
#         self.line, = self.ax.plot([], [], marker='o')

#     def get_figure(self):
#         return self.fig

#     def update_plot(self, m_note):
#         if m_note in self.mapping:
#             y = [self.mapping[m_note] for _ in range(10)]
#         else:
#             y = [0 for _ in range(10)]  # If the note is not found, set Y to 0
#         x = np.arange(len(y))
#         self.line.set_data(x, y)
#         self.line.set_marker(None)
#         self.fig.canvas.draw()

#     def process_audio(self):
#         while True:
#             # Read audio data from the stream
#             data = self.stream.read(self.buffer_size)
#             samples = np.frombuffer(data, dtype=np.float32)

#             # Process audio and detect pitch using Librosa
#             f0, voiced_flag, voiced_probs = librosa.pyin(samples, fmin=librosa.note_to_hz('C0'), fmax=librosa.note_to_hz('C7'))
#             # Extract the most prominent frequency
#             fundamental_frequency = np.median(f0[voiced_flag])
#             if not np.isnan(fundamental_frequency):
#                 # Convert frequency to MIDI note number
#                 midi_note = 69 + 12 * np.log2(fundamental_frequency / 440)

#                 # Map MIDI note to musical note
#                 note_index = int(round(midi_note) % 12)
#                 self.musical_note = self.notes[note_index+1] 

#                 # Print the detected musical note
#                 print("Detected note:", self.musical_note)
#                 self.new_note_event.set()  # Signal that a new note is detected

#     def play_audio_background(self, audio_file):
#         def play_audio_task():
#             time.sleep(5)
#             audio = pydub.AudioSegment.from_file(audio_file)
#             play(audio)

#         audio_thread = threading.Thread(target=play_audio_task)
#         audio_thread.daemon = True  # Set the thread as a daemon so it will be terminated when the main program exits
#         audio_thread.start()

#     def start_analysis(self, audio_file):
#         # Start the real-time processing thread
#         processing_thread = threading.Thread(target=self.process_audio)
#         processing_thread.daemon = True
#         processing_thread.start()

#         # Play the audio in the background
#         self.play_audio_background(audio_file)

#         try:
#             while True:
#                 self.new_note_event.wait()  # Wait for a new note to be detected
#                 self.update_plot(self.musical_note)  # Update the plot with the new note
#                 self.new_note_event.clear()  # Clear the event
#         except KeyboardInterrupt:
#             print("Stopped listening.")

#     def close(self):
#         # Close the PyAudio stream
#         self.stream.stop_stream()
#         self.stream.close()
#         self.p.terminate()

########################################################################

class RealTimeAudioAnalyzer:
    def __init__(self, buffer_size=4096, channels=1, format=pyaudio.paFloat32, rate=44100):
        self.lock = threading.Lock()
        self.buffer_size = buffer_size
        self.channels = channels
        self.format = format
        self.rate = rate
        self.notes = [' ','C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', ' ']
        self.mapping = {'C':1, 'C#':2, 'D':3, 'D#':4, 'E':5, 'F':6, 'F#':7, 'G':8, 'G#':9, 'A':10, 'A#':11, 'B':12}
        self.musical_note = 'C'
        self.new_note_event = threading.Event()  # Event to signal when a new note is detected

        # Create PyAudio stream
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.buffer_size)

        # Create a figure for the plot
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, len(self.notes))
        self.ax.set_yticks(range(0, len(self.notes)))
        self.ax.set_yticklabels(self.notes)
        self.line, = self.ax.plot([], [], marker='o')

    def get_figure(self):
        return self.fig

    def update_plot(self, m_note):
        if m_note in self.mapping:
            y = [self.mapping[m_note] for _ in range(10)]
        else:
            y = [0 for _ in range(10)]  # If the note is not found, set Y to 0
        x = np.arange(len(y))
        self.line.set_data(x, y)
        self.line.set_marker(None)
        self.fig.canvas.draw()

    def process_audio(self):
        try:
            while True:
                with self.lock:
                    data = self.stream.read(self.buffer_size)
                samples = np.frombuffer(data, dtype=np.float32)
                # # Read audio data from the stream
                # data = self.stream.read(self.buffer_size)
                # samples = np.frombuffer(data, dtype=np.float32)

                # Process audio and detect pitch using Librosa
                f0, voiced_flag, voiced_probs = librosa.pyin(samples, fmin=librosa.note_to_hz('C0'), fmax=librosa.note_to_hz('C7'))
                # Extract the most prominent frequency
                fundamental_frequency = np.median(f0[voiced_flag])
                if not np.isnan(fundamental_frequency):
                    # Convert frequency to MIDI note number
                    midi_note = 69 + 12 * np.log2(fundamental_frequency / 440)

                    # Map MIDI note to musical note
                    note_index = int(round(midi_note) % 12)
                    self.musical_note = self.notes[note_index+1] 

                    # Print the detected musical note
                    print("Detected note:", self.musical_note)
                    self.new_note_event.set()  # Signal that a new note is detected
        except Exception as e:
            print("An error occurred:", e)

    def play_audio_background(self, audio_file):
        def play_audio_task():
            time.sleep(5)
            audio = pydub.AudioSegment.from_file(audio_file)
            play(audio)

        audio_thread = threading.Thread(target=play_audio_task)
        audio_thread.daemon = True  # Set the thread as a daemon so it will be terminated when the main program exits
        audio_thread.start()

    def start_analysis(self, audio_file):
        # Start the real-time processing thread
        processing_thread = threading.Thread(target=self.process_audio)
        processing_thread.daemon = True
        processing_thread.start()

        # Play the audio in the background
        self.play_audio_background(audio_file)

        try:
            while True:
                self.new_note_event.wait()  # Wait for a new note to be detected
                self.update_plot(self.musical_note)  # Update the plot with the new note
                self.new_note_event.clear()  # Clear the event
        except KeyboardInterrupt:
            print("Stopped listening.")
        finally:
            self.close()

    def close(self):
        # Close the PyAudio stream
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()