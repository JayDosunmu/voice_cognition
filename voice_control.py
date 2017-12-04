#! /usr/bin/python
#import http.client, urllib2.request, urllib2.parse, urllib2.error, base64, json

from sys import byteorder
from array import array
from struct import pack

import audioop
import pyaudio
import wave
import threading
import time
import io
import os

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

# Thanks to Cryo from stackoverflow:
# stackoverflow.com/questions/82199/detect-record-audio-in-python

#os.path.join(os."speaker_recognition","speech16k.wav")

THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100
SECONDS = 10
file_name = "speech.wav"
out_file = os.path.join(os.path.dirname(__file__), "speaker_recognition/speech16k.wav")

text = None
speaker = None

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


def downsample(src, dst, inrate=44100, outrate=16000, inchannels=1, outchannels=1):
    if not os.path.exists(src):
        print('Source not found!')
        return False

    try:
        s_read = wave.open(src, 'r')
        s_write = wave.open(dst, 'w')
    except:
        print('Failed to open files!')
        return False

    n_frames = s_read.getnframes()
    data = s_read.readframes(n_frames)

    try:
        converted = audioop.ratecv(data, 2, inchannels, inrate, outrate, None)
        # if outchannels == 1:
            # converted = audioop.tomono(converted[0], 2, 1, 0)
    except:
        print('Failed to downsample wav')
        return False

    try:
        s_write.setparams((outchannels, 2, outrate, 0, 'NONE', 'Uncompressed'))
        s_write.writeframes(converted[0])
    except:
        print('Failed to write wav')
        return False

    try:
        s_read.close()
        s_write.close()
    except:
        print('Failed to close wav files')
        return False

    return True


def _record_wav():
    print("please speak a word into the microphone")
    record_to_file(file_name)
    print("done - result written to speech.wav")
    return True

class SpeechToTextThread(threading.Thread):
    def run(self):    
        def _speech_to_text():
            print("transcribing speech")
            text = speech_to_text("nommel_sample.wav")
            print("Success - speech converted to text")
            return True


class SpeakerRecognition(threading.Thread):
    def _speaker_recognize():
        print("downsampling audio file")
        downsample(file_name, out_file)
        print("Success - File downsampled")
        return True

        print("recognizing speaker")
        #speaker = 
        print("speaker recognized")

    

if __name__ == '__main__':
    while(1):
        _record_wav()

        speech_to_text = SpeechToTextThread()
        speaker_recognition = SpeakerRecognition()

        speech_to_text.start()
        speaker_recognition.start()

        speaker_recognition.join()
        speech_to_text.join()

        if text and speaker:
            print("Speaker: %s, Message: %s" % (speaker, text))
        elif not speaker and text:
            print("Speaker: Unknown, Message: %s" % text)
        elif not text and speaker:
            print("Speaker: %s, Message: Unknown" % speaker)
        else:
            print("Unable to parse input")

        

