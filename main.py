import sys
import threading

from console import console
from gui import tkgui

from _socket import error as socket_error
from networking.server import Caller
from sound.io import sound_io_worker

from proto.parallels import SHUTDOWN

# All this module should do is to define whether GUI version should be used or vannila-console



# noinspection PyPep8Naming
def initialize_threads_and_server():
    HOST, PORT = '', 8888
    caller_instance = None
    while True:
        try:
            caller_instance = Caller(HOST, PORT)
            break
        except socket_error:
            PORT += 1

    server_thread = threading.Thread(target=caller_instance.serve_forever, name='Server thread')
    playback_thread = threading.Thread(target=sound_io_worker,
                                       kwargs={'io_type': 0},
                                       name='Playback thread')
    record_thread = threading.Thread(target=sound_io_worker,
                                     kwargs={'io_type': 1},
                                     name='Record sound thread')

    server_thread.setDaemon(True)
    playback_thread.setDaemon(True)
    record_thread.setDaemon(True)

    server_thread.start()
    playback_thread.start()
    record_thread.start()
    return {
        "caller_instance": caller_instance,
        "server_thread": server_thread,
        "playback_thread": playback_thread,
        "record_thread": record_thread,
    }


def main():
    mode = '-console'  # default mode
    modes = ('-console', '-gui')
    try:
        mode = sys.argv[1]
    except IndexError:
        # Using default
        pass

    if mode not in modes:
        print 'Unknown mode {}, only those {} acceptable'.format(mode, modes)
        return
    components = initialize_threads_and_server()
    try:
        if mode == '-console':
            console.initialize(**components)
        elif mode == '-gui':
            tkgui.initialize(components['caller_instance'])
        else:
            print 'Unknown mode {}, only those {} acceptable'.format(mode, modes)
    except KeyboardInterrupt as ex:
        SHUTDOWN.set()
        raise ex
    components['caller_instance'].shutdown()
    print 'Should all stop now? '


if __name__ == '__main__':
    main()