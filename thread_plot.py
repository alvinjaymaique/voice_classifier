# import pyaudio
# import numpy as np
# import librosa
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation
# import threading

# # Constants
# BUFFER_SIZE = 1024
# CHANNELS = 1
# FORMAT = pyaudio.paFloat32
# RATE = 44100
# notes = [' ','C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', ' ']
# mapping = {'C':1, 'C#':2, 'D':3, 'D#':4, 'E':5, 'F':6, 'F#':7, 'G':8, 'G#':9, 'A':10, 'A#':11, 'B':12}
# musical_note = 'C' 
# # Create PyAudio stream
# p = pyaudio.PyAudio()
# stream = p.open(format=FORMAT,
#                 channels=CHANNELS,
#                 rate=RATE,
#                 input=True,
#                 frames_per_buffer=BUFFER_SIZE)

# # def plot_realtime(m_note):
# #     plt.cla()
# #     Y = [mapping[m_note] for i in range(10)]
# #     X = [i for i in range(10)]
# #     plt.xlim(0, 10)
# #     plt.ylim(0, 10)
# #     plt.yticks(range(0, len(notes)), notes)
# #     plt.plot(X,Y)
# #     plt.show()
# #     plt.pause(0.01)

# def process_audio():
#     global musical_note
#     global stream
#     while True:
#         # Read audio data from the stream
#         data = stream.read(BUFFER_SIZE)
#         samples = np.frombuffer(data, dtype=np.float32)

#         # Process audio and detect pitch using Librosa
#         f0, voiced_flag, voiced_probs = librosa.pyin(samples, fmin=librosa.note_to_hz('C0'), fmax=librosa.note_to_hz('C7'))
#         # Extract the most prominent frequency
#         fundamental_frequency = np.median(f0[voiced_flag])
#         if not np.isnan(fundamental_frequency):
#             # Convert frequency to MIDI note number
#             midi_note = 69 + 12 * np.log2(fundamental_frequency / 440)

#             # Map MIDI note to musical note
#             note_index = int(round(midi_note) % 12)
#             if midi_note < 60:
#                 octave = int(round((midi_note - 12) / 12))
#             else:
#                 octave = int(round((midi_note - 12) / 12))
#             musical_note = notes[note_index] 

#             # Print the detected musical note
#             print("Detected note:", musical_note)
#             # plot_realtime(musical_note)

# # Start the real-time processing thread
# processing_thread = threading.Thread(target=process_audio)
# processing_thread.daemon = True
# processing_thread.start()

# # plt.ion()
# # # Plot in the main thread
# # plot_realtime(musical_note)

# try:
#     # Wait for Ctrl+C to stop
#     while True:
#         pass
# except KeyboardInterrupt:
#     print("Stopped listening.")

# # Close the PyAudio stream
# stream.stop_stream()
# stream.close()
# p.terminate()




# -----------------------------------------------------------------------------

import pyaudio
import numpy as np
import librosa
import matplotlib.pyplot as plt
import threading

# Constants
# BUFFER_SIZE = 1024
BUFFER_SIZE = 4096
CHANNELS = 1 
FORMAT = pyaudio.paFloat32
RATE = 44100
notes = [' ','C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', ' ']
mapping = {'C':1, 'C#':2, 'D':3, 'D#':4, 'E':5, 'F':6, 'F#':7, 'G':8, 'G#':9, 'A':10, 'A#':11, 'B':12}
musical_note = 'C' 
new_note_event = threading.Event()  # Event to signal when a new note is detected

# Create PyAudio stream
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=BUFFER_SIZE)

def plot_realtime(m_note):
    plt.cla()
    if m_note in mapping:
        Y = [mapping[m_note] for _ in range(10)]
    else:
        Y = [0 for _ in range(10)]  # If the note is not found, set Y to 0
    X = [i for i in range(10)]
    plt.xlim(0, 10)
    plt.ylim(0, 10)
    plt.yticks(range(0, len(notes)), notes)
    plt.plot(X, Y)
    plt.pause(0.001)  # Pause for a short time to allow plot to update

def process_audio():
    global musical_note
    global new_note_event
    global stream
    while True:
        # Read audio data from the stream
        data = stream.read(BUFFER_SIZE)
        samples = np.frombuffer(data, dtype=np.float32)

        # Process audio and detect pitch using Librosa
        f0, voiced_flag, voiced_probs = librosa.pyin(samples, fmin=librosa.note_to_hz('C0'), fmax=librosa.note_to_hz('C7'))
        # Extract the most prominent frequency
        fundamental_frequency = np.median(f0[voiced_flag])
        if not np.isnan(fundamental_frequency):
            # Convert frequency to MIDI note number
            midi_note = 69 + 12 * np.log2(fundamental_frequency / 440)

            # Map MIDI note to musical note
            note_index = int(round(midi_note) % 12)
            musical_note = notes[note_index+1] 

            # Print the detected musical note
            # print("Detected note:", musical_note)
            new_note_event.set()  # Signal that a new note is detected

# Start the real-time processing thread
processing_thread = threading.Thread(target=process_audio)
processing_thread.daemon = True
processing_thread.start()

plt.ion()  # Turn on interactive mode for Matplotlib
plt.figure()  # Create a new figure for the plot

try:
    while True:
        new_note_event.wait()  # Wait for a new note to be detected
        plot_realtime(musical_note)  # Update the plot with the new note
        new_note_event.clear()  # Clear the event
except KeyboardInterrupt:
    print("Stopped listening.")

# Close the PyAudio stream
stream.stop_stream()
stream.close()
p.terminate()
# -----------------------------------------------------------------------------

