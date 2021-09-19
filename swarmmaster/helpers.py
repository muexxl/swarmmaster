import crccheck
import threading 

class ClientException(Exception):
    pass

class UnknownMessageException(Exception):
    pass

class EmptyMessageException(Exception):
    def __init__(self, msg=""):
        self.msg =msg

class ScopedLock(object):
    def __init__(self, lock: threading.Lock):
        self.lock = lock
        self.lock.acquire()

    def __del__(self):
        self.lock.release()

def crc16(data : bytearray, offset , length):
    if data is None or offset < 0 or offset > len(data)- 1 and offset+length > len(data):
        return 0
    crc = 0xFFFF
    for i in range(0, length):
        crc ^= data[offset + i] << 8
        for j in range(0,8):
            if (crc & 0x8000) > 0:
                crc =(crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF

def crc_check(data, crc):
    _crc =crccheck.crc.Crc16CcittFalse.calc(data)
    return crc == _crc

def crc_calc(data):
    return crccheck.crc.Crc16CcittFalse.calc(data)