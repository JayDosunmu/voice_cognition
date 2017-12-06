import os
import audioop
import wave

file_name = "nommel_sample.wav"#"speech.wav"
out_file = os.path.join(os.path.dirname(__file__), "speaker_recognition/speech16k.wav")
#os.path.join(os."speaker_recognition","speech16k.wav")



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


if __name__ == "__main__":
    print("Downsampling audio file")
    downsample(file_name, out_file, inchannels=1)
    print("Success -  downsample completed")