import SocketServer
import socket
import threading

from sound.io import INPUT_QUEUE, OUTPUT_QUEUE, START_SOUND_IO, STOP_SOUND_IO
from . import messages


class Server(SocketServer.UDPServer):
    def __init__(self, server_address, parent_caller, RequestHandlerClass=None):
        """
        :param caller: instance of Caller that we are passing to be able
        """
        SocketServer.UDPServer.__init__(self, server_address=server_address, RequestHandlerClass=None)
        # We are handling requests right inside server
        print "Server running on {}:{}".format(self.server_address[0], self.server_address[1])
        self.parent_caller = parent_caller

    def _send_text(self, data="ping", to=None):
        try:
            if to:
                self.parent_caller.interlocutor = to
                self.socket.sendto(data, to)
            else:
                self.socket.sendto(data, self.parent_caller.interlocutor)
        except Exception as ex:
            print ex

    def _send_chunks(self):
        print 'Output thread started, accessing self.__callmode'
        while not self.parent_caller.callmode.is_set():
            print 'WAITING FOR CALLMODE'
            self.parent_caller.callmode.wait()
            while self.parent_caller.callmode.is_set():
                #print 'callmode accessed, getting queue'
                chunk = INPUT_QUEUE.get()
                #print 'got queue, sending'
                if not self.parent_caller.interlocutor:
                    print 'no interlocutor, breaking'
                    break
                self.socket.sendto(chunk, self.parent_caller.interlocutor)
                #print 'tried to send'
            print 'CALLMODE EXIT'
        print "send_chunks thread exit"

    def finish_request(self, request, client_address):
        """
        This should call a request handler, but we are implementing it right here (for now)
        """
        data, sock = request  # request[0], request[1]
        #print 'Got data!'
        # TODO: watch at data protocol header
        self.parent_caller.parse_data(data=data, sock=sock, address=client_address)




class Caller(Server, object):
    def __init__(self, ip, port):
        Server.__init__(self, server_address=(ip, port), parent_caller=self, RequestHandlerClass=None)
        self.interlocutor = None
        self.callmode = threading.Event()
        self.__trying_to_call = False
        self.__trying_to_answer = False
        self.output_thread = threading.Thread(target=self._send_chunks, name="Chunk sending thread")
        self.output_thread.start() # Won't work since callmode is not set

    def call(self, address):
        """
        Trying to call address
        :param address: where are we tryping to connect
        :type address tuple:
        """
        # check address
        print 'entered callfuncion'
        self.__initiate_call(address=address)

    def hang_up(self):
        """
        Stops the call
        """
        self._leave_call()

    def send(self, message, address=None):
        address = address or self.interlocutor
        self._send_text(data=message, to=address)

    @property
    def status(self):
        if self.callmode.is_set():
            return "On call"
        if self.__trying_to_call or self.__trying_to_answer:
            return "Connecting"
        return "Not connected"

    @property
    def port(self):
        return self.server_address[1]

    @port.setter
    def port(self, value):
        raise NotImplementedError

    def parse_data(self, data, sock, address):
        command = data[:4]
        self.interlocutor = address
        # if we are initiating a call
        if command == messages.WTAL:
            self.__trying_to_answer = True
            # TODO: leave user a choice to refuse
            self._send_sure()
        if self.__trying_to_call:
            if command == messages.SURE:
                self._send_call()
                self.__enter_callmode()
            elif command == messages.NOTY:
                self.__refresh_status()
        elif self.__trying_to_answer:
            if command == messages.CALL:
                self.__enter_callmode()

        #  if we are ending call
        if command == messages.CHAO:
            self.__refresh_status()

        if self.callmode.is_set():  # if we're in callmode, put incoming data into queue
            OUTPUT_QUEUE.put(data)
        else:
            print "<{ip} {port}>: {message}".format(ip=address[0], port=address[1], message=data)

    def __initiate_call(self, address):
        self.interlocutor = address
        self.__trying_to_call = True
        print 'Caller variabels set'
        self._send_wtal()

    def _send_wtal(self):
        print 'sending wtal'
        self._send_text(data=messages.WTAL, to=self.interlocutor)

    def _send_sure(self):
        print 'sending sure'
        self._send_text(data=messages.SURE, to=self.interlocutor)

    def _send_call(self):
        print 'sending call'
        self._send_text(data=messages.CALL, to=self.interlocutor)

    def _send_chao(self):
        print 'sending chao'
        self._send_text(data=messages.CHAO, to=self.interlocutor)

    def _leave_call(self):
        print "trying to end call"
        self._send_chao()
        self.__refresh_status()
        print "call ended"

    def __refresh_status(self):
        print "trying to refresh status"
        self.__trying_to_answer = False
        self.__trying_to_call = False
        self.__leave_callmode()
        self.interlocutor = None
        print "status refreshed"

    def __enter_callmode(self):
        STOP_SOUND_IO.clear()
        self.callmode.set()
        START_SOUND_IO.set()
        print 'Callmode vars are set'

    def __leave_callmode(self):
        print 'Leaving callmode'
        self.callmode.clear()
        START_SOUND_IO.clear()
        STOP_SOUND_IO.set()

