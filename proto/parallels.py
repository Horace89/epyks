import Queue
import threading

OUTPUT_QUEUE = Queue.Queue()  # For outco
INPUT_QUEUE = Queue.Queue()  # For incoming chunks

STOP_SOUND_IO = threading.Event()
START_SOUND_IO = threading.Event()

SHUTDOWN = threading.Event()

EMPTY_QUEUE = Queue.Empty