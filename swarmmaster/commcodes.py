
class CommCodes():
    CONFIGMSG = 0xff
    REGISTRATION_REQUEST = 0x01
    DEAUTH_REQUEST = 0x02
    RESET_REQUEST = 0x03
    PING = 0x04
    PONG = 0x05
    STARTSEQUENCE = 0x07060504
    HELLO = 0xA0
    MAX_MSG_ID = 0x40


coco = CommCodes()