import time
import pyaudio
from proto.parallels import OUTPUT_QUEUE, INPUT_QUEUE, STOP_SOUND_IO, START_SOUND_IO, SHUTDOWN, EMPTY_QUEUE
# ---- Queues
# Shit works like this:
#
# -> -> ClientA.Record(CHUNK_SIZE) -> CHUNK -> INPUT_QUEUE_A.PUT(CHUNK) -> ClientA.Send(INPUT_QUEUE_A.get()) ->
# -------------------------------------- MEANWHILE ON CLIENT B ---------------------------------------        |
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
# And we want to know when to start capture, START_SOUND_IO event serves this


# ---- SoundIO settings
# We want this to be global, since we might want to change them on the fly
# TODO Thought: we might not actually change input stream, but post-process sound before sending
# it to the ClientB

CHUNK = 1024
RATE = 44100

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


def perform_play(queue, stream):
    try:
        block = queue.get(timeout=1)
    except EMPTY_QUEUE:
        block = None
    if (not block) or SHUTDOWN.is_set():
        return
    stream.write(block)


def perform_record(queue, stream):
    # start = time.time()
    block = stream.read(CHUNK)
    # print time.time() - start
    queue.put(block)


def sound_io_worker(io_type=None):
    """
    :param io_type: 1 - record, 0 - play
    :type io_type int:
    :return:
    """
    if io_type == 1:
        perform_io = perform_record
        queue = INPUT_QUEUE
        params = INPUT_PARAMS
        worker = "recorder"
    else:
        perform_io = perform_play
        queue = OUTPUT_QUEUE
        params = OUTPUT_PARAMS
        worker = "player"
    print '[IO WORKER {}] initiating, start_io: {}, waiting to be set'.format(worker, START_SOUND_IO.is_set())
    while not SHUTDOWN.is_set():
        START_SOUND_IO.wait(timeout=1)
        if not START_SOUND_IO.is_set():
            continue
        print '[IO WORKER {}] started, start_io: {}'.format(worker, START_SOUND_IO.is_set())
        stream = PA.open(**params)
        print '[IO WORKER {}] <stream> inited'.format(worker)
        while not (STOP_SOUND_IO.is_set() or SHUTDOWN.is_set()):
            # print 'acessing output_queue'
            perform_io(queue, stream)
        print 'STOP_SOUND_IO or SHUT DOWN triggered'
        stream.stop_stream()
        stream.close()
    print '[IO WORKER {}] shut down'.format(worker)