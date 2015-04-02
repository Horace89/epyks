import SocketServer
import time

class UDPServer(SocketServer.UDPServer):
    def __init__(self, server_address):
        SocketServer.UDPServer.__init__(self, server_address, None)  # We are handling requests right inside server
        print "Server running on {}:{}".format(self.server_address[0], self.server_address[1])
        self.client_addr = None

    def send_text(self, data="fuck off", to=None):
        time.sleep(2)
        try:
            if to:
                self.socket.sendto(data, to)
            else:
                self.socket.sendto(data, self.client_addr)
        except Exception as ex:
            print ex

    def finish_request(self, request, client_address):
        """
        This should call a request handler, but we are implementing it right here (for now)
        :param request:
        :param client_address:
        :return:
        """
        data, socket = request  # request[0], request[1]
        print "socket: {}".format(socket)
        print "{} wrote: {}".format(client_address[0], data)