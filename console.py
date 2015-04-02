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
    prnt("Your 'eth0' address is: {}".format(wrap(BOLD, get_local_addr())))
    prnt('-' * 80)


def ipv4_check(addr):
    return re.match(IPV4_MATCH, addr)

def port_check(port):
    return 0 < int(port) < 65535

def commander(server_instance=None):
    call = False
    while True:
        data = raw_input()
        if data == "exit":
            break
        elif data[:5] == "sayto":
            try:
                addr, port, message = data[6:].split(" ", 2)
                if ipv4_check(addr) and port_check(port) and message is not "":
                    print 'should sleep'
                    server_instance.send_text(data=message, to=(addr, int(port)))
                    print 'have i slept? '
            except Exception as ex:
                print ex
        elif data[:6] == "callto":
            addr, port = data[6:].split(" ")
            if ipv4_check(addr) and port_check(port):
                pass