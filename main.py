import sys
import threading

from console import console
from gui import gui

from _socket import error as socket_error
from networking.server import UDPServer
from sound.io import player, recorder

# All this module should do is to define whether GUI version
# should be used or vannila-console

HOST, PORT = '', 8888
#
# def console_listner(HOST, PORT):
# server = UDPServer((HOST, PORT))
#     srv_thread = threading.Thread(target=server.serve_forever, name='ServerThread', daemon=True)
#     playback_thread = threading.Thread(target=player, name='PlaybackThread')
#     recorder_thread = threading.Thread(target=recorder, name='RecordSoundThread')
#     # srv_thread.setDaemon(True)
#     srv_thread.start()
#     playback_thread.start()
#     recorder_thread.start()
#     console.commander(server_instance=server)
#     server.shutdown()


def initialize_threads_and_server():
    global PORT
    server_instance = None
    while True:
        try:
            server_instance = UDPServer((HOST, PORT))
            break
        except socket_error:
            PORT += 1

    server_thread = threading.Thread(target=server_instance.serve_forever, name='ServerThread')
    playback_thread = threading.Thread(target=player, name='PlaybackThread')
    record_thread = threading.Thread(target=recorder, name='RecordSoundThread')

    server_thread.setDaemon(True)
    playback_thread.setDaemon(True)
    record_thread.setDaemon(True)

    server_thread.start()
    playback_thread.start()
    record_thread.start()
    return {
        "server_instance": server_instance,
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