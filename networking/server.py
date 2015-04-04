import SocketServer
import threading

from sound.client import INPUT_QUEUE, OUTPUT_QUEUE, START_SOUND_IO, STOP_SOUND_IO


class UDPServer(SocketServer.UDPServer):
    def __init__(self, server_address):
        SocketServer.UDPServer.__init__(self, server_address, None)  # We are handling requests right inside server
        print "Server running on {}:{}".format(self.server_address[0], self.server_address[1])
        self.client_addr = None
        self.output_thread = threading.Thread(target=self.send_chunks, name="Chunk_sending_thread")
        self.__callmode = threading.Event()

    def send_text(self, data="fuck off", to=None):
        try:
            if to:
                self.client_addr = to
                self.socket.sendto(data, to)
            else:
                self.socket.sendto(data, self.client_addr)
        except Exception as ex:
            print ex

    def send_chunks(self):
        print 'Output thread started, accessing self.__callmode'
        while self.__callmode.is_set():
            print 'callmode accessed, getting queue'
            chunk = INPUT_QUEUE.get()
            print 'got queue, sending'
            self.socket.sendto(chunk, self.client_addr)

    def finish_request(self, request, client_address):
        """
        This should call a request handler, but we are implementing it right here (for now)
        """
        data, socket = request  # request[0], request[1]
        print 'Got data!'
        # TODO: watch at data protocol header
        if data[:5] == "callm":
            print 'Trying to enter callmode'
            self.enter_callmode()
            return
        elif data[:5] == "leave":
            self.leave_callmode()
            return
        if self.__callmode.is_set():  # If we're in callmode, put incoming data into queue
            OUTPUT_QUEUE.put(data)
        else:
            print "<{}>: {}".format(client_address[0], data)

    def enter_callmode(self):
        # TODO: locks
        self.__callmode.set()
        START_SOUND_IO.set()
        print 'Callmode vars are set, trying to start output_thread'
        self.output_thread.start()

    def leave_callmode(self):
        # TODO: locks
        print 'Leaving callmode'
        self.__callmode.clear()
        STOP_SOUND_IO.set()