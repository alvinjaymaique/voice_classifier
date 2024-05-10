# # Always have this class for RealTimeAudioAnalyzer
# class Worker(QObject):
#     finished = pyqtSignal()

#     def __init__(self, audio_analyzer, audio_file):
#         super().__init__()
#         self.audio_analyzer = audio_analyzer
#         self.audio_file = audio_file

#     def run(self):
#         self.audio_analyzer.start_analysis(self.audio_file)
#         self.finished.emit()

###################################################################################################          

import pyaudio
import numpy as np
import librosa
import matplotlib.pyplot as plt
import threading
import time
import pydub
import csv
import wave
from pydub.playback import play
import pydub.playback

class RealTimeAudioAnalyzer:
    def __init__(self, buffer_size=4096, channels=1, format=pyaudio.paInt16 , rate=44100):
        self.lock = threading.Lock()
        self.buffer_size = buffer_size
        self.channels = channels
        self.format = format
        self.rate = rate
        self.notes = [' ', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', ' ']
        self.mapping = {'C':1, 'C#':2, 'D':3, 'D#':4, 'E':5, 'F':6, 'F#':7, 'G':8, 'G#':9, 'A':10, 'A#':11, 'B':12}
        self.musical_note = 'C'
        self.new_note_event = threading.Event()  # Event to signal when a new note is detected
        self.stream = None
        self.stop_processing = threading.Event()  # Event to signal processing thread to stop
        self.processing_thread = None
        self.audio_thread = None

        self.voice_file = ''
        self.frames = [] # used for recording an audio 
        self.duration = 0 # duration of recording an audio
        self.user_note = []
        self.isRecord = False # Indicate to record the note to be used for scoring
        self.audio_player = None

         # Create PyAudio stream
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.buffer_size)     
        # self.create_fig()

        

    def create_fig(self):
        # Create a figure for the plot
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, len(self.notes))
        self.ax.set_yticks(range(0, len(self.notes)))
        self.ax.set_yticklabels(self.notes)
        self.line, = self.ax.plot([], [], marker='o')
    
    def start_record(self):
        print("* Recording...")
        # frames = []  # List to store audio frames
        # Record audio for 5 seconds (adjust as needed)
        for _ in range(0, int(self.rate / self.buffer_size * self.duration)):
            data = self.stream.read(self.buffer_size)
            self.frames.append(data)
        print("* Done recording!")
        self.save_audio()

    def stop_and_save_recorded_audio(self):
        if self.stream is not None and self.stream.is_active():
            # Stop recording
            self.stream.stop_stream()
            self.stream.close()
            self.save_audio()
        if self.audio_thread is not None and self.audio_thread.is_alive():
            self.stop_processing.set()
            self.audio_thread.join()

    def save_audio(self):
        wf = wave.open(self.voice_file+'.wav', 'wb')
        wf.setnchannels(self.channels)  # Mono
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)  # Sample rate
        wf.writeframes(b''.join(self.frames))
        wf.close()
        print(f"Recording saved as {self.voice_file}.wav")


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
            while not self.stop_processing.is_set():
                data = self.stream.read(self.buffer_size)
                samples = np.frombuffer(data, dtype=np.int16)

                # Process audio and detect pitch using Librosa
                f0, voiced_flag, _ = librosa.pyin(samples, fmin=librosa.note_to_hz('C0'), fmax=librosa.note_to_hz('C7'))
                # Extract the most prominent frequency
                fundamental_frequency = np.median(f0[voiced_flag])
                if not np.isnan(fundamental_frequency) and fundamental_frequency != 0:  # Check if frequency is valid
                    # Convert frequency to MIDI note number
                    midi_note = 69 + 12 * np.log2(fundamental_frequency / 440)

                    # Map MIDI note to musical note
                    note_index = int(round(midi_note)) % 12
                    self.musical_note = self.notes[note_index+1] 

                    # Print the detected musical note
                    print("Detected note:", self.musical_note)
                    self.new_note_event.set()  # Signal that a new note is detected
                    self.new_note_event.clear()  # Clear the event
        except Exception as e:
            print("An error occurred:", e)
        finally:
            self.close()

    def append_note(self, note, isRecord):
        if isRecord:
            self.user_note.append(note)

    def play_audio_background(self, audio_file):
        def play_audio_task():
            # time.sleep(5)
            audio = pydub.AudioSegment.from_file(audio_file)
            self.audio_player = pydub.playback.play(audio)
            print(self.audio_player)
            # play(audio)
            # chunk_duration = 2000  # 1 second
            # for start_time in range(0, len(audio), chunk_duration):
            #     if self.stop_processing.is_set():  # Check if the stop flag is set
            #         break  # Exit the loop if the flag is set
            #     # Extract the current chunk
            #     chunk = audio[start_time:start_time + chunk_duration]
            #     # Play the chunk
            #     play(chunk)
               
        self.audio_thread = threading.Thread(target=play_audio_task)
        self.audio_thread.daemon = True  # Set the thread as a daemon so it will be terminated when the main program exits
        self.audio_thread.start()
        # split_file = audio_file.split('.')
        # self.start_record(split_file[0]+'1'+split_file[1])

    def stop_audio(self):
        # Check if there is a player object and stop it
        # print(self.audio_player)
        if not self.audio_player:
            self.audio_player.stop()
        else:
            print("Audio playback hasn't started yet.")
        # Optionally, if you want to stop the audio playback thread as well
        # Set the stop_processing flag if it's used in your threaded task
        self.stop_processing.set()

    def start_analysis(self, audio_file, target, sleep, duration):
        # Play the audio in the background
        self.play_audio_background(audio_file)
        time.sleep(sleep)
        # Start the real-time processing thread
        # split_audiofile = audio_file.split('.')
        self.duration = duration
        self.voice_file = audio_file.split('.')[0] + '1'
        # self.start_record()
        self.processing_thread = threading.Thread(target=target) 
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def close(self):
        # Close the PyAudio instance
        if self.p is not None:
            self.p.terminate()


    def saveto_csv(self, filename):
        # Load the audio file
        audio_file = filename
        y, sr = librosa.load(audio_file)
        # Extract fundamental frequency
        f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

        # Initialize an empty array to store musical notes
        musical_notes = []

        # Iterate through each frame
        for i in range(len(f0)):
            # Check if the frame is voiced
            if voiced_flag[i]:
                # Get the fundamental frequency for the voiced frame
                fundamental_frequency = f0[i]
                
                # Convert frequency to MIDI note number
                midi_note = 69 + 12 * np.log2(fundamental_frequency / 440)
                musical_notes.append(librosa.midi_to_note(midi_note,octave=False))


        name = audio_file.split('.')[0]
        csv_file = name+'.csv'

        # Open the CSV file in write mode
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write the header
            writer.writerow([name])
            
            # Write each musical note to the CSV file
            for note in musical_notes:
                writer.writerow([note])

    def read_csv(self, csv_file):
        # Initialize an empty list to store musical notes
        read_musical_notes = []
        # Open the CSV file in read mode with UTF-8 encoding
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            # Skip the header row
            next(reader)
            
            # Read each row and extract musical notes
            for row in reader:
                read_musical_notes.append(row[0])
        # Display the read musical notes
        print(read_musical_notes)

    def score(recorded, reference):
        dictMap = {}
        score = 0
        for index, (note_ref, note_rec) in enumerate(zip(reference, recorded)):
            if(note_ref == note_rec):
                dictMap[index] = 1
            else:
                dictMap[index] = 0
        for value in dictMap.values():
            if(value == 1):
                score += 1
        score = (score/len(dictMap.keys))
        return score
    
    