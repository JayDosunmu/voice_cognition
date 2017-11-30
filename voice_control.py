#! /usr/bin/python

from sys import byteorder
from array import array
from struct import pack

import pyaudio
import wave
import time
import io
import os

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

# Thanks to Cryo from stackoverflow:
# stackoverflow.com/questions/82199/detect-record-audio-in-python

THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 16000
SECONDS = 10
file_name = "speech.wav"


def is_silent(snd_data):
    """
        Threshold sound data by checking if the max value of the snippet is less than THRESHOLD
    """
    return max(snd_data) < THRESHOLD


def normalize(snd_data):
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r


def trim(snd_data):
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i) > THRESHOLD:
                snd_started = True
                r.append(i)
            
            elif snd_started:
                r.append(i)
        
        return r
    
    snd_data = _trim(snd_data)

    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data


def add_silence(snd_data, seconds):
    r = array('h', [0 for i in range(int(seconds*RATE))])
    r.extend(snd_data)
    r.extend([0 for i in range(int(seconds*RATE))])
    return r


def record():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=1,
        rate=RATE,
        input=True,
        input_device_index=2,
        output=True,
        frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    snd_started = False

    r = array('h')
    t_start = time.time()
    t_last = t_start
    while 1:
        snd_data = array('h', stream.read(CHUNK_SIZE, exception_on_overflow=False))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True

        t_end = time.time()
        if t_end - t_last > 1:
            print("tick")
            t_last = t_end
        if snd_started and num_silent > 30 or t_end - t_start > SECONDS:
            break

    sample_width = p.get_sample_size(FORMAT)

    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 0.5)
    return sample_width, r


def record_to_file(path):
    sample_width, data = record()
    data = pack('<' + ('h'*len(data)), *data)

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()


def speech_to_text(file_name):
    client = speech.SpeechClient()

    file_name = os.path.join(os.path.dirname(__file__),
        file_name)

    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code='en_US'
    )

    response = client.recognize(config, audio)

    for result in response.results:
        print(result)
        #print('Transcript: {}'.format(result.alternativees[0].transcript))

    return response.results.alternatives[0]


if __name__ == '__main__':
    while(1):
        print("please speak a word into the microphone")
        record_to_file(file_name)
        print("done - result written to speech.wav")

        print("transcribing speech")
        text = speech_to_text(file_name)
        print("Success - speech converted to text")

        print("downsampling audio file")
        print("Success - File downsampled")