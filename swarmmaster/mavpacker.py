from .swarmclient import SwarmClient

import struct
import logging
import socket

logger = logging.getLogger(__name__)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class Mavpacker(object):

    
    def __init__(self):
        pass

    def check_client(self, client: SwarmClient):
        client.rx_lock.acquire()
        len = self.contains_message(client.rx_buffer)
        packet = None
        if len:
            packet = client.rx_buffer[:len]
            client.rx_buffer = client.rx_buffer[len:]
            logger.debug(
                f"Extracted {len} bytes from RX Buffer of Client #{client.id:04x} "
            )
        else:
            packet = None
        client.rx_lock.release()
        return packet

    def contains_message(self, buf: bytearray):
        if len(buf) > 16:
            return 16
        else:
            return 0


class Publisher(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = "192.168.0.46"
        self.port = 14550
        self.addr = (self.ip, self.port)

    def udp_send(self, data):
        self.sock.sendto(bytes(data), self.addr)
