from proto.parallels import OUTPUT_QUEUE, EMPTY_QUEUE
from bisect import bisect

BUFFER = list()


def buffer_parse(caller_instance, data):
    global BUFFER
    bisect(BUFFER, data, key=data.PID)
    if len(BUFFER) == 6:
        map(OUTPUT_QUEUE.put, BUFFER)
        BUFFER = []
        return
    elif len(BUFFER) > 6:
        map(OUTPUT_QUEUE.put, BUFFER[:6])
        caller_instance.overflow()

