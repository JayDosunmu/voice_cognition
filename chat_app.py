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

from controller import Controller

file_name = 'speech.wav'


if __name__ == '__main__':
    try:
        welcome = (
            "\nWelcome to the chat app voice control client\n"
            "to use the client, you can speak naturally\n\n"
            "say any of the following commands to control the client\n\n"
            "    \"enroll new profile\": start process to recognize a new speaker\n"
            "    \"start conversation\": begin a new conversation\n"
            "    \"sign into conversation <speaker name>\": add an individual to a conversation by saying name\n"
            "    \"close conversation\": to end the current conversation\n"
            "    \"stop application\": stop the chat app voice client\n"
            "    \"clear profiles\": remove the currently enrolled profiles from account\n"
        )
        print(welcome)

        controller = Controller(file_name)
        controller.clear_profiles()

        while  controller.is_running():
            controller.run()
    except KeyboardInterrupt:
        print('\nprocess interrupted...')
    finally:
        print('Interaction complete...')
        

