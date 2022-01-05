import logging
from os import fchown
import socket
import threading
import time
import subprocess

logger = logging.getLogger(__name__)

#from pymavlink.dialects.v20 import ardupilotmega as mavlink2

class UDPServer(threading.Thread):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1),
        self.sock.setblocking(0)
        self.sock.bind(('',14570))

        #self.udp_broadcast = ('<broadcast>', 14550)
        self.udp_broadcasts = []

        shell_command = "ifconfig |grep broadcast|awk '{print $6}'"
        ip_list = subprocess.check_output(shell_command, shell=True, text=True).split('\n')
        for ip in ip_list:
            if ip=='':
                continue
            self.udp_broadcasts.append((ip,14550)) 
        self.rx_buf = bytearray()
        self.rx_lock = threading.Lock()
        self.data_available = False

        self.tx_buf = bytearray()
        self.tx_lock = threading.Lock()
        self.keep_running = False
        self.max_buf_size = 0xffff
        threading.Thread.__init__(self)

    def __del__(self):
        pass
    def run(self):
        self.keep_running = True
        logger.info('Running UDP Server')
        while self.keep_running:
            if self.tx_buf:
                self._send()
            self._receive()

            time.sleep(0.2)

        logger.info('UDP SERVER Run function ended')


    def stop(self):
        logger.info('Stopping UDP Server')
        self.keep_running = False
        self.join()
        logger.info('Stopped UDP Server')


    def _receive(self):

        data = None
        try:
            data, address = self.sock.recvfrom(4096)
            #logger.warning(f'UDPServer  |  Received {data }from {address}')
        except BlockingIOError:
            pass
            # logger.info('Excepted BlockingIOError')
        if data:
            self.rx_lock.acquire()
            self.rx_buf +=bytearray(data)
            self.data_available = True
            self.rx_lock.release()

    def _send(self):
        self.tx_lock.acquire()
        
        for broadcast in self.udp_broadcasts:
            try:
                self.sock.sendto(self.tx_buf[:self.max_buf_size], broadcast)
            except OSError:
                pass
        self.tx_buf = self.tx_buf[self.max_buf_size:]
        self.tx_lock.release()

    def publish_via_udp(self, data):
        self.tx_lock.acquire()
        self.tx_buf +=bytearray(data)
        self.tx_lock.release()


