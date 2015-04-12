import SocketServer
import threading

from sound.io import INPUT_QUEUE, OUTPUT_QUEUE, START_SOUND_IO, STOP_SOUND_IO
from . import messages
#
#
# class Caller(object):
#     def __init__(self, ip, port):
#         self.server = UDPServer((ip, port))
#         self.interlocutor = None
#         self.__enter_callmode = None
#
#     def send_wanna_talk(self, address=None):
#         pass
#
#     def recieve_wtal_answer(self):
#         pass
#
#     def send_call(self):
#         pass
#
#     def initiate_call(self):
#         self.send_wanna_talk()
#         self.recieve_wtal_answer()
#         self.send_call()
#         self.__enter_callmode()


class UDPServer(SocketServer.UDPServer):
    def __init__(self, server_address):
        SocketServer.UDPServer.__init__(self, server_address, None)  # We are handling requests right inside server
        print "Server running on {}:{}".format(self.server_address[0], self.server_address[1])
        self.interlocutor = None
        self.output_thread = threading.Thread(target=self.send_chunks, name="Chunk_sending_thread")
        self.__callmode = threading.Event()
        self.__trying_to_call = False
        self.__trying_to_answer = False

    def send_text(self, data="ping", to=None):
        try:
            if to:
                self.interlocutor = to
                self.socket.sendto(data, to)
            else:
                self.socket.sendto(data, self.interlocutor)
        except Exception as ex:
            print ex

    def send_chunks(self):
        print 'Output thread started, accessing self.__callmode'
        while self.__callmode.is_set():
            print 'callmode accessed, getting queue'
            chunk = INPUT_QUEUE.get()
            print 'got queue, sending'
            self.socket.sendto(chunk, self.interlocutor)

    def finish_request(self, request, client_address):
        """
        This should call a request handler, but we are implementing it right here (for now)
        """
        # TODO: watch at data protocol header
        data, socket = request  # request[0], request[1]
        print 'Got data!'
        command = data[:4]
        self.interlocutor = client_address
        # { initiating a call block
        if command == messages.WTAL:
            self.__trying_to_answer = True
            # TODO: leave user a choice to refuse
            self.bg_send_sure()
        if self.__trying_to_call:
            if command == messages.SURE:
                self.bg_send_call()
                self.enter_callmode()
            elif command == messages.NOTY:
                self.refresh_status()
        elif self.__trying_to_answer:
            if command == messages.CALL:
                self.enter_callmode()
        # }

        # ending call block {
        if command == messages.CHAO:
            self.refresh_status()
        # }

        if self.__callmode.is_set():  # If we're in callmode, put incoming data into queue
            OUTPUT_QUEUE.put(data)
        else:
            print "<{}>: {}".format(client_address[0], data)

    def initiate_call(self, address):
        self.interlocutor = address
        self.__trying_to_call = True
        self.bg_send_wtal()

    def bg_send_wtal(self):
        """
        Function that sends "wanna talk" message
        """
        print 'sending wtal'
        self.send_text(data=messages.WTAL, to=self.interlocutor)

    def bg_send_sure(self):
        self.send_text(data=messages.SURE, to=self.interlocutor)

    def bg_send_call(self):
        self.send_text(data=messages.CALL, to=self.interlocutor)

    def bg_send_chao(self):
        self.send_text(data=messages.CHAO, to=self.interlocutor)

    def leave_call(self):
        self.bg_send_chao()
        self.refresh_status()

    def refresh_status(self):
        self.__trying_to_answer = False
        self.__trying_to_call = False
        self.leave_callmode()
        self.interlocutor = None

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