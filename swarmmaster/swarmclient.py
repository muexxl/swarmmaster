
from .commcodes import coco
import threading
import logging
logger= logging.getLogger(__name__)

class SwarmClient:
    max_rx_buf = 1024
    max_tx_buf = 1024
    def __init__(self, id=0):
        self.id = id
        self.rx_buffer = bytearray()
        self.tx_buffer = bytearray()
        self.last_msg_id= coco.HELLO
        self.fail_counter = 0
        self.prio = 0 # Prio is 0 as base. Prio 0 means highest.  increase +1 for everytime the client is talked to. regular reductions ? maybe. 
        self.rx_lock = threading.Lock()
        self.tx_lock = threading.Lock()

    def add_data_to_rx_buffer(self, msg):
        msg_id = msg[0]
        expected_id = (self.last_msg_id +1)% coco.MAX_MSG_ID      
        self.rx_lock.acquire()
        if self.last_msg_id == coco.HELLO:
            self.rx_buffer+=(msg[1:])
        elif msg_id == expected_id:
            self.rx_buffer+=(msg[1:])
        else:
            logging.warning(f'Message id 0x{msg_id:02x} does not Match expected Message id 0x{expected_id:02x}')
            logging.warning(f'Deleting rx buffer {self.rx_buffer}')
            self.rx_buffer.clear()
            self.rx_buffer+=(msg[1:])
        self.rx_lock.release()
        self.last_msg_id = msg_id
        
        if len(self.rx_buffer) > self.max_rx_buf:
            self.rx_buffer = self.rx_buffer[-self.max_rx_buf:]
            logger.warning(f'Client {self.id:04x} had to drop data due to RX Buffer overflow')

    def add_data_to_tx_buffer(self, data):
        self.tx_lock.acquire()
        self.tx_buffer+=(data[:])  
        if len(self.tx_buffer) > self.max_tx_buf:
            self.tx_buffer = self.tx_buffer[-self.max_tx_buf:]
            self.tx_lock.release()
            logger.warning(f'Client {self.id:04x} dropped data due to TX Buffer overflow')
            return False
        self.tx_lock.release()
        return True
