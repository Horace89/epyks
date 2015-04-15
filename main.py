import sys
import threading

from console import console
from gui import gui

from _socket import error as socket_error
from networking.server import Caller
from sound.io import player, recorder

# All this module should do is to define whether GUI version
# should be used or vannila-console

HOST, PORT = '', 8888


def initialize_threads_and_server():
    global PORT
    caller_instance = None
    while True:
        try:
            caller_instance = Caller(HOST, PORT)
        except socket_error:
            PORT += 1
        break

    server_thread = threading.Thread(target=caller_instance.serve_forever, name='Server thread')
    playback_thread = threading.Thread(target=player, name='Playback thread')
    record_thread = threading.Thread(target=recorder, name='Record sound thread')

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
    if mode == '-console':
        console.initialize(**components)
    elif mode == '-gui':
        gui.initialize(**components)
    else:
        print 'Unknown mode {}, only those {} acceptable'.format(mode, modes)


if __name__ == '__main__':
    main()