# Calling mechanism works pretty much like TCP 3-way handshake
#
# Positive conversation example:          Negative:
#
#    clientA               clientB        clientA               clientB
#       ||       WTAL        ||             ||       WTAL        ||
#       || ------------>>>>  ||             || ------------>>>>  ||
#       ||                   ||             ||                   ||
#       ||       SURE        ||             ||       NOTY        ||
#       || <<<<------------  ||             || <<<<------------  ||
#       ||                   ||
#       ||       CALL        ||
#       || ------------>>>>  ||             WTAL (wanna talk?)   => Offer to make a call
#       ||                   ||             SURE (sure)          => Positive response to call offer
#       ||       DATA        ||             CALL (call)          => Signal that we are starting data transmission
#       || <<<<<<<-->>>>>>>  ||             NOTY (no, thank you) => Negative response to call offer
#       ||                   ||             CHAO (goodbye)       => Ending a call
#
#
# Ending a call works pretty simple:
#       ||       CHAO        ||
#       || ------------>>>>  ||
#       ||                   ||
#

WTAL = "WTAL"
SURE = "SURE"
NOTY = "NOTY"
CALL = "CALL"
CHAO = "CHAO"

ON_CALL = "On call"
CONNECTING = "Connecting"
NOT_CONNECTED = "Not connected"

MESSAGE_HEADER = "MSG!"

MAX_WAIT_TIME = 5