import SocketServer
import threading
import sched
import time
from proto.parallels import OUTPUT_QUEUE, INPUT_QUEUE, STOP_SOUND_IO, START_SOUND_IO, SHUTDOWN
import struct
from . import messages


class VoiceData(object):
    def __init__(self, packet):
        if packet[0] != messages.VOICECH_HEADER:
            raise ValueError
        self.pid = PacketID.unpack(packet[1:3])
        self.voicebuff = packet[3:]


class PacketID(object):
    MAX_SIZE = 2 ** 16 - 1

    def __init__(self):
        self.x = 0

    def __add__(self, other):
        if self.x + other <= self.MAX_SIZE:
            self.x += other
            return self
        self.x = 0
        return self

    @property
    def value(self):
        val = struct.pack("H", self.x)
        return val

    def pack(self):
        return struct.pack("H", self.x)

    @classmethod
    def unpack(cls, packed_value):
        try:
            return struct.unpack("H", packed_value)
        except struct.error:
            return 0

    def __str__(self):
        return self.x


class Server(SocketServer.UDPServer):
    def __init__(self, server_address, parent_caller):
        """
        :param parent_caller: instance of Caller that we are passing to be able
        """
        SocketServer.UDPServer.__init__(self, server_address=server_address, RequestHandlerClass=None)
        # We are handling requests right inside server
        print "Server running on {}:{}".format(self.server_address[0], self.server_address[1])
        self.last_net_action = None  # Last time that we actually got some data
        self.parent_caller = parent_caller
        self.current_pid = PacketID()

    def send_message(self, data, to=None):
        self._send_text(data="{}{}".format(messages.MESSAGE_HEADER, data), to=to)

    def send_command(self, command, to=None):
        self._send_text(data="{}{}".format(messages.COMMAND_HEADER, command), to=to)

    def _send_text(self, data="ping", to=None):
        self.last_net_action = time.time()
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
        while not SHUTDOWN.is_set():
            self.parent_caller.callmode.wait(timeout=0.2)
            while self.parent_caller.callmode.is_set() and (not SHUTDOWN.is_set()):
                # print 'callmode accessed, getting queue'
                chunk = INPUT_QUEUE.get(timeout=2)
                if not chunk:
                    continue
                # print 'got queue, sending'
                if not self.parent_caller.interlocutor:
                    print 'no interlocutor, breaking'
                    break
                self.socket.sendto("{}{}{}".format(messages.VOICECH_HEADER, self.current_pid.pack(), chunk),
                                   self.parent_caller.interlocutor)
                self.current_pid += 1
        print 'SEND_CHUNKS EXIT'

    def finish_request(self, request, client_address):
        """
        This should call a request handler, but we are implementing it right here (for now)
        """
        data, sock = request  # request[0], request[1]
        self.last_net_action = time.time()
        # TODO: watch at data protocol header
        self.parent_caller.parse_data(data=data, sock=sock, address=client_address)


class Caller(Server, object):
    def __init__(self, ip, port):
        Server.__init__(self, server_address=(ip, port), parent_caller=self)
        self.interlocutor = None
        self.callmode = threading.Event()
        self.messangers = []
        self.__trying_to_call = False
        self.__trying_to_answer = False
        self.__init_scheduler()
        self.__init_chunks_output()

    def __init_chunks_output(self):
        self.output_thread = threading.Thread(target=self._send_chunks, name="Chunk sending thread")
        self.output_thread.start()  # Won't actually start since callmode is not set

    def __init_scheduler(self):
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(delay=1, priority=1, action=check_status_repeatedly, argument=(scheduler, self))
        self.scheduler_thread = threading.Thread(target=scheduler.run, name="Scheduler thread")
        self.scheduler_thread.start()

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
        if not self.interlocutor:
            return
        self._leave_call()

    def send(self, message, address=None):
        address = address or self.interlocutor
        self.send_message(data=message, to=address)

    def shutdown(self):
        print 'trying to shut down'
        Server.shutdown(self)
        print 'now it should be stopped... i guess..'

    @property
    def status(self):
        if self.callmode.is_set():
            return messages.ON_CALL
        if self.__trying_to_call or self.__trying_to_answer:
            return messages.CONNECTING
        return messages.NOT_CONNECTED

    @property
    def port(self):
        return self.server_address[1]

    def parse_message(self, author, message):
        """
        onMessageRecievedParams:
        :param author: Address of author, tuple (ip, port)
        :param message: Content
        """
        self._alert_messangers(author=author, message=message)

    def parse_audio(self, author, packet):
        if self.callmode.is_set():  # if we're in callmode, put incoming data into queue
            OUTPUT_QUEUE.put(packet)

    def parse_control(self, command):
        if command == messages.WTAL:
            self.__trying_to_answer = True
            # TODO: leave user a choice to refuse
            answer = None
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
        if command == messages.OFLO:
            self.__relax_chunks()

    def parse_data(self, data, sock, address):
        command = data[0]
        if command == messages.COMMAND_HEADER:
            self.interlocutor = address
            self.parse_control(data[1:])
        elif command == messages.MESSAGE_HEADER:
            self.parse_message(self.interlocutor or address, message=data[1:])
        elif command == messages.VOICECH_HEADER:
            packet = VoiceData(data)
            self.parse_audio(author=self.interlocutor, packet=packet)

    def overflow(self):
        self._send_overflow()

    def __initiate_call(self, address):
        self.interlocutor = address
        self.__trying_to_call = True
        print 'Caller variabels set'
        self._send_wtal()

    def _alert_messangers(self, author, message):
        for messanger in self.messangers:
            messanger.onMessageRecieved(author, message)

    def _send_wtal(self):
        print 'sending wtal'
        self.send_command(messages.WTAL, to=self.interlocutor)
        # self._send_text(data=messages.WTAL, to=self.interlocutor)

    def _send_sure(self):
        print 'sending sure'
        self.send_command(messages.SURE, to=self.interlocutor)
        # self._send_text(data=messages.SURE, to=self.interlocutor)

    def _send_call(self):
        print 'sending call'
        self.send_command(messages.CALL, to=self.interlocutor)
        # self._send_text(data=messages.CALL, to=self.interlocutor)

    def _send_chao(self):
        print 'sending chao'
        self.send_command(messages.CHAO, to=self.interlocutor)
        # self._send_text(data=messages.CHAO, to=self.interlocutor)

    def _send_overflow(self):
        self.send_command(messages.OFLO, to=self.interlocutor)

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

    def __relax_chunks(self):
        raise NotImplementedError

def check_status_repeatedly(scheduler, instance):
    if SHUTDOWN.is_set():
        return
    if instance.status == messages.ON_CALL or instance.status == messages.CONNECTING:
        if time.time() - instance.last_net_action > messages.MAX_WAIT_TIME:
            instance.hang_up()
    scheduler.enter(delay=1, priority=1, action=check_status_repeatedly, argument=(scheduler, instance))

