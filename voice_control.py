#! /usr/bin/python

import alsaaudio

card = 'sysdefault:CARD=Microphone'
inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, card)
