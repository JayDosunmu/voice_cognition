import http.client, urllib.request, urllib.parse, urllib.error, base64
import io
import json
import os
import pyaudio
import threading
import urllib
import wave

from time import sleep

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from recorder import Recorder
from user import User


THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100
SECONDS = 10
file_name = 'speech.wav'
out_file = os.path.join(os.path.dirname(__file__), 'speech16k.wav')


class ChatClient:
    def __init__(self, url='http://chatappproject.herokuapp.com'):
        self.url = url
        self.endpoints = {
            'messages':'',
            'conversations':'',
            'users':''
        }
    
    def send_message(self, message):
        pass

    
    def add_conversation(self, conversation):
        pass

    
    def add_user(self, user):
        pass


class GoogleClient:
    def __init__(self, rate=RATE):
        self.rate = rate

    def speech_to_text(self, file_name):
        client = speech.SpeechClient()

        file_name = os.path.join(os.path.dirname(__file__),
            file_name)

        with io.open(file_name, 'rb') as audio_file:
            content = audio_file.read()
            audio = types.RecognitionAudio(content=content)

        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            #sample_rate_hertz=self.rate,
            language_code='en_US'
        )

        response = client.recognize(config, audio)

        # for result in response.results:
        #     print(result)
            #print('Transcript: {}'.format(result.alternativees[0].transcript))
        if len(response.results) > 0 and len(response.results[0].alternatives) > 0:
            print(response.results[0].alternatives[0].transcript)
            return response.results[0].alternatives[0].transcript
        else:
            return ''
    

    def get_thread(msg, *args, **kwargs):
        return SpeechToTextThread(msg, *args, **kwargs)


class SpeechToTextThread(threading.Thread):
    def __init__(self, msg, *args, **kwargs):
        super(SpeechToTextThread, self).__init__(*args, **kwargs)
        
        self.client = GoogleClient()
        self.msg = msg

    def _speech_to_text(self):
        print("\ntranscribing speech")
        self.msg.set_text(self.client.speech_to_text("speech.wav"))
        print("Success - speech converted to text\n")
        return True

    def run(self):  
        self._speech_to_text()
