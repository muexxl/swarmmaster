import logging
import socket
import threading
import time
logger = logging.getLogger(__name__)
#from pymavlink.dialects.v20 import ardupilotmega as mavlink2

class UDPListener(threading.Thread):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1),
        # own_hostname = socket.gethostname()
        # own_ip = socket.gethostbyname(own_hostname)
        # own_ip = ''
        self.sock.setblocking(0)
        
        self.sock.bind(('',5544))
        
        self.rx_buf = bytearray()
        self.rx_lock = threading.Lock()
        self.data_available = False

        self.max_buf_size = 0xffff
        threading.Thread.__init__(self)

    def __del__(self):
        pass

    def run(self):
        self.keep_running = True
        logger.info('UDP Listener | Running UDP Listener')
        while self.keep_running:
            self._receive() 
            time.sleep(0.5)
        
        logger.info('UDP Listener |  Run function ended')


    def stop(self):
        logger.info('UDP Listener | Stopping UDP Listener')
        self.keep_running = False
        self.join()
        logger.info('UDP Listener | Stopped UDP Listener')
        

    def _receive(self):
        data = None
        try:
            data, address = self.sock.recvfrom(4096)
        except BlockingIOError:
            pass
            # logger.info('Excepted BlockingIOError')
        if data:
            logger.debug(f'UDP Listener  |  Received {data }from {address}')
            self.rx_lock.acquire()
            self.rx_buf +=bytearray(data)
            self.data_available = True
            self.rx_lock.release()
        
