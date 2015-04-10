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
#     server = UDPServer((HOST, PORT))
#     srv_thread = threading.Thread(target=server.serve_forever, name='ServerThread', daemon=True)
#     playback_thread = threading.Thread(target=player, name='PlaybackThread')
#     recorder_thread = threading.Thread(target=recorder, name='RecordSoundThread')
#     # srv_thread.setDaemon(True)
#     srv_thread.start()
#     playback_thread.start()
#     recorder_thread.start()
#     console.commander(server_instance=server)
#     server.shutdown()


def main():
    mode = '-console'  # default mode
    modes = ('-console', '-gui')
    try:
        mode = sys.argv[1]
    except IndexError:
        # Using default
        pass
    if mode == '-console':
        console.initialize()
    elif mode == '-gui':
        gui.initialize()
    else:
        print 'Unknown mode {}, only those {} acceptable'.format(mode, modes)


if __name__ == '__main__':
    main()
#
# if __name__ == '__main__a':
#     console.greetings()
#     HOST, PORT = 'localhost', 8888
#     while True:
#         try:
#             console_listner(HOST, PORT)
#             break
#         except socket_error as ex:
#             if ex.errno == 98:
#                 print "Port {} already in use, trying out next".format(PORT)
#                 PORT += 1