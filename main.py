import threading
import console
from _socket import error as socket_error
from networking.server import UDPServer
from client import player, recorder


def console_listner(HOST, PORT):
    server = UDPServer((HOST, PORT))
    srv_thread = threading.Thread(target=server.serve_forever, name='ServerThread')
    playback_thread = threading.Thread(target=player, name='PlaybackThread')
    recorder_thread = threading.Thread(target=recorder, name='RecordSoundThread')
    # srv_thread.setDaemon(True)
    srv_thread.start()
    playback_thread.start()
    recorder_thread.start()
    console.commander(server_instance=server)
    server.shutdown()


if __name__ == '__main__':
    console.greetings()
    HOST, PORT = 'localhost', 8888
    while True:
        try:
            console_listner(HOST, PORT)
            break
        except socket_error as ex:
            if ex.errno == 98:
                print "Port {} already in use, trying out next".format(PORT)
                PORT += 1