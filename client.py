import Queue
import pyaudio
import threading


# ---- Queues
# Shit works like this:
#
# -> -> ClientA.Record(CHUNK_SIZE) -> CHUNK -> INPUT_QUEUE_A.PUT(CHUNK) -> ClientA.Send(INPUT_QUEUE_A.get()) ->
# -------------------------------------- MEANWHILE ON CLIENT B ---------------------------------------  |
# < -<- ClientB.Play(CHUNK)  <-  OUTPUT_QUEUE_B.PUT(CHUNK)  <- CHUNK <- ClientB.RecV(CHUNK_SIZE)<- <- <- <- <-
#
# So we need two Queues on each server: output and input
# OUTPUT will get filled by Server and get emptied by SoundIO
# INPUT will get filled by SoundIO and emptied by Server
#
# Server                  Server
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
START_SOUND_IO = threading.Event()

# ---- SoundIO settings
# We want this to be global, since we might want to change them on the fly
# TODO Thought: we might not actually change input stream, but post-process sound before sending
# it to the ClientB

CHUNK = 1024
RATE = 22000

INPUT_PARAMS = {
    'frames_per_buffer': CHUNK,  # Check if this is best way
    'format': pyaudio.paInt16,  # Not sure about that either
    'rate': RATE,  # Lowering rate for the very begining
    'channels': 1,  # My mic has one channel, so...
    'input': True,
}
OUTPUT_PARAMS = {  # Pretty much same as input
    'frames_per_buffer': CHUNK,
    'format': pyaudio.paInt16,
    'rate': RATE,
    'channels': 1,
    'output': True,
}

PA = pyaudio.PyAudio()


def player():
    print '[Player] initiating, start_io: {}, waiting to be set'.format(START_SOUND_IO.is_set())

    START_SOUND_IO.wait()

    print '[Player] started, start_io: {}'.format(START_SOUND_IO.is_set())
    stream = PA.open(**OUTPUT_PARAMS)
    print '[Player] <stream> inited'
    while not STOP_SOUND_IO.is_set():
        block = OUTPUT_QUEUE.get()
        stream.write(block)
    print 'STOP_SOUND_IO triggered'
    stream.stop_stream()
    stream.close()


def recorder():
    print '[Recorder] initiating, start_io: {}, waiting to be set'.format(START_SOUND_IO.is_set())

    START_SOUND_IO.wait()

    print '[Recorder] started, start_io: {}'.format(START_SOUND_IO.is_set())
    stream = PA.open(**INPUT_PARAMS)
    print '[Recorder] <stream> inited'
    while not STOP_SOUND_IO.is_set():
        block = stream.read(CHUNK)
        INPUT_QUEUE.put(block)
    print 'STOP_SOUND_IO triggered'
    stream.stop_stream()
    stream.close()
