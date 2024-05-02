import numpy as np
import tensorflow as tf
import os
import librosa
import json
from tensorflow.keras import layers, models # type: ignore
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model # type: ignore

import pyaudio
import wave
import threading

class VoiceClassifier:
    # @tf.function(reduce_retracing=True)
    def __init__(self, data_dir='dataset', test_size=0.2, desired_shape=(128, 128), sr=22050, hop_length=512, n_mels=128):
        self.data_dir = data_dir
        self.test_size = test_size
        self.desired_shape = desired_shape
        self.sr = sr
        self.hop_length = hop_length
        self.n_mels = n_mels
        self.labels = {}
        self.model = None

    def create_model(self, input_shape, num_classes):
        model = models.Sequential([
            layers.Reshape((input_shape[0], input_shape[1], 1), input_shape=input_shape),  # Add a channel dimension
            layers.Conv2D(32, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(64, activation='relu'),
            layers.Dense(num_classes, activation='softmax')
        ])
        return model

    def preprocess_data(self):
        X = []
        y = []
        for i, label in enumerate(os.listdir(self.data_dir)):
            label_dir = os.path.join(self.data_dir, label)
            self.labels[i] = label
            for file in os.listdir(label_dir):
                file_path = os.path.join(label_dir, file)
                y_, sr = librosa.load(file_path, sr=self.sr)
                n_fft = min(2048, len(y_))
                hop_length = n_fft // 4
                spectrogram = librosa.feature.melspectrogram(y=y_, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=self.n_mels)
                spectrogram = librosa.power_to_db(spectrogram, ref=np.max)
                pad_width = self.desired_shape[1] - spectrogram.shape[1]
                if pad_width > 0:
                    spectrogram = np.pad(spectrogram, ((0, 0), (0, pad_width)), mode='constant')
                else:
                    spectrogram = spectrogram[:, :self.desired_shape[1]]
                X.append(spectrogram)
                y.append(i)
            
        X = np.array(X)
        y = np.array(y)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.test_size, random_state=42)
        input_shape = X_train.shape[1:]
        num_classes = len(self.labels)
        y_train = tf.keras.utils.to_categorical(y_train, num_classes)
        y_test = tf.keras.utils.to_categorical(y_test, num_classes)
        return X_train, X_test, y_train, y_test, input_shape, num_classes

    def train_model(self, epochs=4, batch_size=32):
        X_train, X_test, y_train, y_test, input_shape, num_classes = self.preprocess_data()
        self.model = self.create_model(input_shape, num_classes)
        self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, y_test))
        test_loss, test_acc = self.model.evaluate(X_test, y_test)
        print('Test accuracy:', test_acc)

    def preprocess_audio(self, audio_file):
        y_, sr = librosa.load(audio_file)
        spectrogram = librosa.feature.melspectrogram(y=y_, sr=sr)
        spectrogram = librosa.power_to_db(spectrogram, ref=np.max)
        current_shape = spectrogram.shape
        if current_shape[1] > self.desired_shape[1]:
            spectrogram = spectrogram[:, :self.desired_shape[1]]
        elif current_shape[1] < self.desired_shape[1]:
            pad_width = self.desired_shape[1] - current_shape[1]
            spectrogram = np.pad(spectrogram, ((0, 0), (0, pad_width)), mode='constant')
        if current_shape[0] != self.desired_shape[0]:
            spectrogram = librosa.util.fix_length(spectrogram, self.desired_shape[0], axis=0)
        spectrogram = np.expand_dims(spectrogram, axis=-1)
        return spectrogram

    def predict_audio(self, audio_file):
        if not self.model:
            print("Error: Model not trained. Please train the model first.")
            return
        preprocessed_audio = self.preprocess_audio(audio_file)
        predictions = self.model.predict(np.expand_dims(preprocessed_audio, axis=0))
        predicted_class_index = np.argmax(predictions)
        # Check if predicted class index exists in self.labels
        predicted_class = self.labels[predicted_class_index]
        # print("Predicted class:", predicted_class)
        return predicted_class

    def save_model(self, model_path, labels_path):
        self.model.save(model_path)
        with open(labels_path, 'w') as f:
            json.dump(self.labels, f)

    def load_model(self, model_path, labels_path):
        self.model = load_model(model_path)
        with open(labels_path, 'r') as f:
            labels_dict = json.load(f)
            self.labels = list(labels_dict.values())

    def record(self, output_filename, record_seconds=60, sample_rate=44100, channels=1, audio_format=pyaudio.paInt16):
        self.output_filename = output_filename
        self.record_seconds = record_seconds
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_format = audio_format
        self.frames = []
        self.recording = False
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.audio_format,
                                       channels=self.channels,
                                       rate=self.sample_rate,
                                       input=True,
                                       frames_per_buffer=1024)
        
    def start_recording(self):
        self.recording = True
        self.frames = []
        print("Recording...")
        threading.Thread(target=self._record).start()

    def _record(self):
        for _ in range(0, int(self.sample_rate / 1024 * self.record_seconds)):
            if not self.recording:
                break
            data = self.stream.read(1024)
            self.frames.append(data)
        self.stop_recording()

    def stop_recording(self):
        if self.recording:
            self.recording = False
            print("Finished recording.")
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            self.save_to_file()

    def save_to_file(self):
        wf = wave.open(self.output_filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()


# # Usage example
# if __name__ == "__main__":
#     voice_classifier = VoiceClassifier(data_dir='dataset')
#     # voice_classifier.train_model()
#     voice_classifier.load_model('model.keras', 'labels.json')
#     audio_file = 'tenor_pavarotti.wav'
#     voice_classifier.predict_audio(audio_file)
