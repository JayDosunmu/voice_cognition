from sys import byteorder
from array import array
from struct import pack

import audioop
import pyaudio
import wave
import time
import io
import os

# Thanks to Cryo from stackoverflow:
# stackoverflow.com/questions/82199/detect-record-audio-in-python

THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 16000
SECONDS = 10
SILENCE_DURATION = 60


class Recorder:
    def record_to_file(self, file_name, minimum_time=0):
        sample_width, data = self._record(minimum_time)
        data = pack('<' + ('h'*len(data)), *data)

        wf = wave.open(file_name, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(RATE)
        wf.writeframes(data)
        wf.close()


    def downsample(self, src, dst, inrate=44100, outrate=16000, inchannels=1, outchannels=1):
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


    def bytes_from_file(self, filename, chunksize=8192):
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(chunksize)
                if chunk:
                    yield chunk
                else:
                    break


    def _record(self, minimum_time=0):
        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=1,
            rate=RATE,
            input=True,
            # input_device_index=2,
            # output=True,
            frames_per_buffer=CHUNK_SIZE)

        num_silent = 0
        snd_started = False

        r = array('h')
        t_start = time.time()
        t_last = t_start

        print('\nrecording...\n')
        while 1:
            snd_data = array('h', stream.read(CHUNK_SIZE, exception_on_overflow=False))
            if byteorder == 'big':
                snd_data.byteswap()
            r.extend(snd_data)

            silent = self._is_silent(snd_data)

            if silent and snd_started:
                num_silent += 1
            elif not silent and not snd_started:
                snd_started = True

            t_end = time.time()
            if t_end - t_last > 1:
                t_last = t_end
            
            # print(snd_started)
            # print(num_silent, SILENCE_DURATION)
            # print(t_end, t_start, SECONDS)
            if snd_started and num_silent > SILENCE_DURATION or t_end - t_start > SECONDS:
                if t_end - t_start > minimum_time:
                    break

        sample_width = p.get_sample_size(FORMAT)

        stream.stop_stream()
        stream.close()
        p.terminate()

        r = self._normalize(r)
        r = self._trim(r)
        r = self._add_silence(r, 0.5)
        return sample_width, r


    def _is_silent(self, snd_data):
        """
            Threshold sound data by checking if the max value of the snippet is less than THRESHOLD
        """
        return max(snd_data) < THRESHOLD


    def _normalize(self, snd_data):
        MAXIMUM = 16384
        times = float(MAXIMUM)/max(abs(i) for i in snd_data)

        r = array('h')
        for i in snd_data:
            r.append(int(i*times))
        return r


    def _trim(self, snd_data):
        def _trim_helper(snd_data):
            snd_started = False
            r = array('h')

            for i in snd_data:
                if not snd_started and abs(i) > THRESHOLD:
                    snd_started = True
                    r.append(i)
                
                elif snd_started:
                    r.append(i)
            
            return r
        
        snd_data = _trim_helper(snd_data)

        snd_data.reverse()
        snd_data = _trim_helper(snd_data)
        snd_data.reverse()
        return snd_data


    def _add_silence(self, snd_data, seconds):
        r = array('h', [0 for i in range(int(seconds*RATE))])
        r.extend(snd_data)
        r.extend([0 for i in range(int(seconds*RATE))])
        return r

