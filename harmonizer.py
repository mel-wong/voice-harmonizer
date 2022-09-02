# Harmonizer script that takes in audio and outputs harmony
import sounddevice as sd
import wavio as wv
import numpy as np
from scipy.io.wavfile import read, write
from scipy.fft import rfft, rfftfreq
import math


# class for audio recording
class Audio:

    def __init__(self, sampling_freq=44100):
        self.sampling_freq = sampling_freq
        self.recording = np.array([])

    # record audio and save as wav
    def record(self, duration):
        self.recording = sd.rec(int(duration * self.sampling_freq), samplerate=self.sampling_freq, channels=1)
        sd.wait()
        wv.write('recording.wav', self.recording, self.sampling_freq, sampwidth=2)


# Identify different pitches in recording
def pitch_analysis(new_audio, note_delta):
    num_samples = new_audio.recording.size

    note_step = int(note_delta * new_audio.sampling_freq)
    i = 0
    num_notes = int(num_samples // note_step)

    # setting lowest (65 Hz) and highest freq (1000 Hz) for human voices to ignore noise
    lowest_freq_index = math.ceil(65 * note_delta)
    highest_freq_index = math.floor(1000 * note_delta)

    # array storing frequency of each note
    notes = np.zeros(num_notes)
    while i < num_notes:
        fft_amp = abs(rfft(new_audio.recording[i * note_step:note_step * (i + 1)]))
        fft_freq = rfftfreq(note_step, 1 / new_audio.sampling_freq)

        # handle time where no audio
        if not np.any(fft_amp):
            notes[i] = 0
        else:
            notes[i] = fft_freq[fft_amp[lowest_freq_index:highest_freq_index].argmax()]
        i += 1

    return notes


# generate wav file from array of note frequencies
def generateWav(notes, duration, note_delta):
    sample_rate = 44100
    t = np.linspace(0., duration, int(sample_rate * note_delta))
    amp = np.iinfo(np.int16).max
    wav_data = np.empty(duration * sample_rate)
    for i in range(len(notes)):
        wav_data[i * len(t):len(t) * (i + 1)] = amp * np.sin(2. * np.pi * notes[i] * t)

    write('harmony.wav', sample_rate, wav_data.astype(np.int16))


# Main code
if __name__ == '__main__':

    # frequency ratios for harmonic intervals
    harmony_ratio = {'octave': 2, 'fifth': 1.5, 'fourth': 1.33, 'major third': 1.25, 'minor third': 1.2}

    # just noticeable difference for humans is approx 1 Hz
    jnd = 1

    # Check if recording should start
    while True:

        mic_on = input("Begin recording? (Y/N): ")
        duration = 3  # seconds
        if mic_on.lower() == 'y' or mic_on.lower() == 'n':
            print('Recording...')
            new_audio = Audio()

            # Record for 10 seconds
            new_audio.record(duration)
            print('Recording has stopped!')
            break

        else:
            print('Invalid input! Please try again.')
            continue

    while True:
        try:
            interval = int(input(
                'Select desired harmony (1 = minor third, 2 = major third, 3 = perfect fourth, 4 = perfect fifth, 5 = octave: '))

        except:
            print('Invalid entry!')

        else:
            if interval < 1 or interval > 5:
                continue
            elif interval == 1:
                print('Minor Third chosen!')
                harmony_value = harmony_ratio['minor third']
            elif interval == 2:
                print('Major third chosen!')
                harmony_value = harmony_ratio['major third']
            elif interval == 3:
                print('Perfect Fourth chosen!')
                harmony_value = harmony_ratio['fourth']
            elif interval == 4:
                print('Perfect fifth chosen!')
                harmony_value = harmony_ratio['fifth']
            elif interval == 5:
                print('Octave chosen!')
                harmony_value = harmony_ratio['octave']
            break

    # Analyse notes of new audio file
    note_delta = 0.25
    notes = pitch_analysis(new_audio, note_delta)
    print(f'Frequency of notes: {notes}')

    # Calculate harmony
    harmony_freq = 1/harmony_value*notes
    harmony_freq = notes
    print(f'Harmony notes: {harmony_freq}')

    # Generate harmony wave file
    generateWav(harmony_freq, duration, note_delta)
