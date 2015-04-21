import SocketServer
import threading
import sched
import time
from proto.parallels import OUTPUT_QUEUE, INPUT_QUEUE, STOP_SOUND_IO, START_SOUND_IO, SHUTDOWN
from . import messages


class Server(SocketServer.UDPServer):
    def __init__(self, server_address, parent_caller):
        """
        :param parent_caller: instance of Caller that we are passing to be able
        """
        SocketServer.UDPServer.__init__(self, server_address=server_address, RequestHandlerClass=None)
        # We are handling requests right inside server
        print "Server running on {}:{}".format(self.server_address[0], self.server_address[1])
        self.last_net_action = None  # Last time that we actually got some data
        #self.socket.sendto = self.__wrappedsocksend
        self.parent_caller = parent_caller

    #def __wrappedsocksend(self, *args, **kwargs):
    #    self.last_net_action = time.time()
    #    self.socket.sendto(*args, **kwargs)

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
                print 'callmode accessed, getting queue'
                chunk = INPUT_QUEUE.get(timeout=2)
                if not chunk:
                    continue
                # self.last_net_action = time.time()
                print 'got queue, sending'
                if not self.parent_caller.interlocutor:
                    print 'no interlocutor, breaking'
                    break
                self.socket.sendto(chunk, self.parent_caller.interlocutor)
                print 'tried to send'
            #print 'SEND_CHUNKS CALLMODE BLOCK END'
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
        scheduler.enter(delay=1, priority=1, action=check_status_recursive, argument=(scheduler, self))
        self.scheduler_thread = threading.Thread(target=scheduler.run, name="Scheduler thread")
        self.scheduler_thread.setDaemon(True)
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
        self._send_text(data="MSG!{}".format(message), to=address)

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

    def parse_data(self, data, sock, address):
        command = data[:4]
        self.interlocutor = address
        if command == messages.MESSAGE_HEADER:
            print 'in command message!'
            self._alert_messangers(author=self.interlocutor or address, message=data[4:])
            return
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

    def _alert_messangers(self, author, message):
        print 'trying to allert messangers'
        print self.messangers
        for messanger in self.messangers:
            print 'alerting {}'.format(messanger)
            messanger.onMessageRecieved(author, message)

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


def check_status_recursive(scheduler, instance):
    if SHUTDOWN.is_set():
        return
    if instance.status == messages.ON_CALL or instance.status == messages.CONNECTING:
        if time.time() - instance.last_net_action > messages.MAX_WAIT_TIME:
            instance.hang_up()
    scheduler.enter(delay=1, priority=1, action=check_status_recursive, argument=(scheduler, instance))

