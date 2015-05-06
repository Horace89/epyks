from networking.base import get_local_addr
import re

"""
This class handles users text input-output
"""

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

IPV4_MATCH = """^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"""


def wrap(style, text):
    return ''.join([style, text, style])


def prnt(msg=None):
    # In case of GUI
    msg = msg or ""
    print msg


def greetings():
    prnt('-' * 80)
    prnt('Greetings!\n')
    prnt("This is a voice chat application which allows you to communicate between local")
    prnt("machines by using your voice")
    prnt()
    prnt("To get list of commands type {}".format(wrap(BOLD, "help")))
    prnt()
    prnt("callto 192.168.0.102 888")
    prnt("Your 'eth0' address is: {}".format(wrap(BOLD, get_local_addr())))
    prnt('-' * 80)


def ipv4_check(addr):
    return re.match(IPV4_MATCH, addr)


def port_check(port):
    return 0 < int(port) < 65535


def commander(caller_instance=None):
    call = False
    while True:
        data = raw_input()
        command = data.split(' ')
        if data == "exit":
            break
        elif command[0] == "sayto":
            try:
                addr, port, message = command[1:]
                if ipv4_check(addr) and port_check(port) and message is not '':
                    caller_instance._send_text(data=message, to=(addr, int(port)))
            except Exception as ex:
                print ex
        elif command[0] == "callto":
            addr, port = command[1:3]
            if ipv4_check(addr) and port_check(port):
                prnt('Trying to initiate a call')
                caller_instance.call(address=(addr, int(port)))
        elif command[0] == "endcall":
            caller_instance.hang_up()


def initialize(caller_instance, server_thread, playback_thread, record_thread):
    """
    """
    greetings()
    commander(caller_instance)