from _socket import error as socket_error
import threading
from networking.server import UDPServer
import console
from Queue import Queue

def console_listner(HOST, PORT):
    server = UDPServer((HOST, PORT))
    t1 = threading.Thread(target=server.serve_forever, name='Echo')
    t1.setDaemon(True)
    t1.start()

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