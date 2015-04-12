import sys
import threading

from console import console
from gui import gui

from _socket import error as socket_error
from networking.server import UDPServer
from sound.io import player, recorder

# All this module should do is to define whether GUI version
# should be used or vannila-console

HOST, PORT = 'localhost', 8888
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
    server = None
    while True:
        try:
            server = UDPServer((HOST, PORT))
            break
        except socket_error:
            PORT += 1
    server_t = threading.Thread(target=server.serve_forever, name='ServerThread')
    playback_t = threading.Thread(target=player, name='PlaybackThread')
    recorder_t = threading.Thread(target=recorder, name='RecordSoundThread')
    server_t.setDaemon(True)
    playback_t.setDaemon(True)
    recorder_t.setDaemon(True)
    return {
        "server_instance": server,
        "server_thread": server_t,
        "playback_thread": playback_t,
        "record_thread": recorder_t,
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