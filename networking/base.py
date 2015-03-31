import socket


def get_local_addr(family=socket.AF_INET, remote="192.0.2.123"):
    """
    Gets preferable IP address for current machine, most of the
    times it will be 'eth0' address.
    :param family: domain, which protocol to use (IPv4 default)
    :param remote: address to connect, best practice: non-existsing
    :return: local ip address used to connect to 'remote'
    """
    try:
        s = socket.socket(family, socket.SOCK_DGRAM)
        try:
            s.connect((remote, 9))  # Trying to connect random IP, expected to be unsuccessfull
            return s.getsockname()[0]  # But we wanted just to know which address we've used
        finally:
            s.close()
    except socket.error:  # We are fucked, shit happens
        return None  # TODO: reraise exception