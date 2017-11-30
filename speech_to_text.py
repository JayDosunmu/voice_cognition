import io
import os

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

client = speech.SpeechClient()

file_name = os.path.join(os.path.dirname(__file__),
    'speech.wav')

with io.open(file_name, 'rb') as audio_file:
    content = audio_file.read()
    audio = types.RecognitionAudio(content=content)

config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=44100,
    language_code='en_US'
)

response = client.recognize(config, audio)

for result in response.results:
    print(result)
    #print('Transcript: {}'.format(result.alternativees[0].transcript))
