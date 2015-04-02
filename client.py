import Queue
import pyaudio
import threading


# ---- Queues
# Shit works like this:
#
# -> -> ClientA.Record(CHUNK_SIZE) -> CHUNK -> INPUT_QUEUE_A.PUT(CHUNK) -> ClientA.Send(INPUT_QUEUE_A.get()) ->
#       -------------------------------------- MEANWHILE ON CLIENT B ---------------------------------------  |
# < -<- ClientB.Play(CHUNK)  <-  OUTPUT_QUEUE_B.PUT(CHUNK)  <- CHUNK <- ClientB.RecV(CHUNK_SIZE)<- <- <- <- <-
#
# So we need two Queues on each server: output and input
# OUTPUT will get filled by Server and get emptied by SoundIO
# INPUT will get filled by SoundIO and emptied by Server
#
#                  Server                  Server
#           SoundIO  ^                        |   SoundIO
#           | |      | |                    | |      ^ |
#           | |      | |                    | |      | |
# InputQ:   | v      | |         OutputQ:   | v      | |
#           |   data   |                    |   data   |
#            ----------                      ----------
#
# Also we would like to have trigger that tells us to stop SoundIO, which is STOP_SOUND_IO Event

OUTPUT_QUEUE = Queue.Queue()
INPUT_QUEUE = Queue.Queue()
STOP_SOUND_IO = threading.Event()

# ---- SoundIO settings
# We want this to be global, since we might want to change them on the fly
# TODO Thought: we might not actually change input stream, but post-process sound before sending
# it to the ClientB
CHUNK = 1024
INPUT_PARAMS = {
    'frames_per_buffer': CHUNK,    # Check if this is best way
    'format': pyaudio.paInt16,    # Not sure about that either
    'rate': 10000,                # Lowering rate for the very begining
    'channels': 1,                # My mic has one channel, so...
    'input': True,
}
OUTPUT_PARAMS = {  # Pretty much same as input
    'frames_per_buffer': CHUNK,
    'format': pyaudio.paInt16,
    'rate': 10000,
    'channels': 1,
    'output': True,
}


class SoundIO(object):
    CURRENT_READ_CHUNK = None

    def __new__(cls, *args, **kwargs):
        """
        We want our class to be a singletone
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(SoundIO, cls).__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self):
        self.audio_streams = {
            'input': PyAudio.open(**stream_defaults['input']),
            'output': PyAudio.open(**stream_defaults['output'])
        }
        self.out_write = self.audio_streams['output'].write
        self.in_read = self.audio_streams['input'].read
        for stream in self.audio_streams.values():
            stream.start_stream()

    def play(self, chunk):
        self.out_write(chunk)

    def record(self, chunk_size):
        self.CURRENT_READ_CHUNK = self.in_read(chunk_size)

    def stop(self):
        for stream in self.audio_streams.values():
            stream.stop_stream()
            stream.close()

    def __del__(self):
        self.stop()


class OuterPlayer(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(OuterPlayer, self).__init__(*args, **kwargs)

    def run(self):
        p = pyaudio.PyAudio()  # TODO: should this be global?
        stream = p.open(**OUTPUT_PARAMS)
        while not STOP_SOUND_IO.is_set():
            block = OUTPUT_QUEUE.get()
            stream.write(block)
        stream.stop_stream()
        stream.close()

class InnerRecorder(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(InnerRecorder, self).__init__(*args, **kwargs)

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(**INPUT_PARAMS)
        while not STOP_SOUND_IO.is_set():
            block = stream.read(CHUNK)
            INPUT_QUEUE.put(block)
        stream.stop_stream()
        stream.close()