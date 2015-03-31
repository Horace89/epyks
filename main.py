from _socket import error as socket_error
import threading
from networking.base import get_local_addr
import SocketServer


class Console():
    """
    This class handles user input-output
    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def bold(text):
        return ''.join([Console.BOLD, text, Console.ENDC])

    @staticmethod
    def greetings():
        print '-' * 80
        print 'Greetings!\n'
        print "This is a voice chat application which allows you to communicate between local"
        print "machines by using your voice"
        print ""
        print "To get list of commands type " + Console.bold("help")
        print ""
        print "Your 'eth0' address is: " + Console.bold(get_local_addr())
        print '-' * 80

class SpeakingUDPServer(SocketServer.UDPServer):
    def __init__(self, server_address):
        SocketServer.UDPServer.__init__(self, server_address, None)  # We are handling requests right in server
        print "Server running on {}:{}".format(self.server_address[0], self.server_address[1])
        self.client_addr = None

    def speak(self, data="fuck off", to=None):
        try:
            if to:
                self.socket.sendto(data, to)
            else:
                self.socket.sendto(data, self.client_addr)
        except Exception as ex:
            print ex

    def finish_request(self, request, client_address):
        """

        :param request:
        :param client_address:
        :return:
        """
        self.data = request[0]
        self.socket = request[1]
        print "socket: {}".format(self.socket)
        print "{} wrote: {}".format(client_address[0], self.data)

def console_commander(server_instance=None):
    while True:
        data = raw_input()
        if data == "exit":
            break
        elif data[:5] == "sayto":
            addr, port, message = data[5:].split(" ", 2)
            server_instance.speak(data=message, to=(addr, int(port)))

def console_listner(HOST, PORT):
    server = SpeakingUDPServer((HOST, PORT))
    t1 = threading.Thread(target=server.serve_forever, name='Echo')
    t1.setDaemon(True)
    t1.start()

    console_commander(server)

    server.shutdown()


if __name__ == '__main__':
    Console.greetings()
    HOST, PORT = 'localhost', 8888
    while True:
        try:
            console_listner(HOST, PORT)
            break
        except socket_error as ex:
            if ex.errno == 98:
                print "Port {} already in use, trying out next".format(PORT)
                PORT += 1