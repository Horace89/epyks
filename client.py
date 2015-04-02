import pyaudio

PyAudio = pyaudio.PyAudio()

stream_defaults = {
    'output': {
        'frames_per_buffer': 1024,
        'format': pyaudio.paInt16,
        'rate': 44100,
        'channels': 1,
        'output': True
    },
    'input': {
        'frames_per_buffer': 1024,
        'format': pyaudio.paInt16,
        'rate': 44100,
        'channels': 1,
        'input': True
    },
}

class SoundIO(object):
    output_stream = PyAudio.open(**stream_defaults['output'])
    input_stream = PyAudio.open(**stream_defaults['input'])