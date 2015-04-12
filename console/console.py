
def initialize(threads):
    """
    :param server_t: UDP Server thread instance
    :param playback_t: Playback thread instance
    :param record_t: Record mic thread instance
    """
    server_t, playback_t, record_t = threads
    print 'Console interface here'
    raw_input()