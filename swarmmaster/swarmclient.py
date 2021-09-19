from .commcodes import coco
import threading
import logging
from .configuration import *
from .helpers import *
from .packetbuffer import PacketBuffer

logger = logging.getLogger(__name__)

class SwarmClient:
    max_rx_buf = 2**20
    max_tx_buf = 2**20

    def __init__(self, id=0):

        self.id = id

        self.uid0 = 0
        self.uid1 = 0
        self.uid2 = 0
        self.devid = 0
        self.registration_request_ack_sent = False

        self.packet_buffer= PacketBuffer()
        self.rx_buffer = self.packet_buffer.stream_buffer
        self.rx_lock = self.packet_buffer.stream_buffer_lock

        self.tx_buffer = bytearray()
        self.tx_lock = threading.Lock()

        self.last_msg_id = coco.HELLO
        self.fail_counter = 0
        self.prio = 0  # Prio is 0 as base. Prio 0 means highest.  increase +1 for everytime the client is talked to. regular reductions ? maybe.
        self.mav_id_correct = False
        self.mav_id_request_sent = 0

        
        
        
        self.bytes_received = 0
        self.bytes_sent = 0

        self.packet_id = 0
        self.chksum = 0
        self.chksum_due = 0

    def get_stats(self):
        self.rx_lock.acquire()
        received_bytes_brutto = self.packet_buffer.received_bytes_brutto
        self.packet_buffer.received_bytes_brutto =0
        received_bytes_netto = self.packet_buffer.received_bytes_netto
        self.packet_buffer.received_bytes_netto = 0
        received_packets= self.packet_buffer.received_packets
        lost_packets = self.packet_buffer.lost_packets
        restored_packets = self.packet_buffer.restored_packets
        double_packets = self.packet_buffer.double_packets
        self.rx_lock.release()

        self.tx_lock.acquire()
        bytes_sent = self.bytes_sent
        self.bytes_sent = 0
        self.tx_lock.release()
        return bytes_sent, received_bytes_brutto,received_bytes_netto, received_packets,double_packets, restored_packets ,lost_packets

    def get_tx_buffer_size(self):
        return len(self.tx_buffer)

    def add_msg_to_packet_buffer(self, msg):
        self.packet_buffer.add_message(msg)


    def add_data_to_tx_buffer(self, data):
        self.tx_lock.acquire()
        self.tx_buffer += (data[:])
        if len(self.tx_buffer) > self.max_tx_buf:
            self.tx_buffer = self.tx_buffer[-self.max_tx_buf:]
            self.tx_lock.release()
            logger.warning(
                f'Swarmclient\t| Client {self.id:04x} dropped data due to TX Buffer overflow'
            )
            return False
        self.tx_lock.release()
        return True

    def read_data_from_tx_buffer(self, length):
        self.tx_lock.acquire()
        data = self.tx_buffer[:length]
        self.tx_lock.release()
        return data

    def remove_data_from_tx_buffer(self, length):
        self.tx_lock.acquire()
        length = min(length, len(self.tx_buffer))
        self.tx_buffer = self.tx_buffer[length:]
        self.bytes_sent += length
        self.tx_lock.release()

    def get_data_from_tx_buffer(self, length):
        self.tx_lock.acquire()
        length = min(length, len(self.tx_buffer))
        data = self.tx_buffer[:length]
        self.tx_buffer = self.tx_buffer[length:]
        self.bytes_sent += length
        self.tx_lock.release()
        return data

    def get_packet(self):

        if (self.packet_id == MAX_PACKET_BEFORE_CHECKSUM):
            self.chksum_due = 1

        if (len(self.tx_buffer) == 0):
            self.chksum_due = 1

        if self.chksum_due:  #checksum packet
            id_byte = coco.CHKSUM + self.packet_id
            msg = bytearray()
            msg += self.chksum.to_bytes(32, 'little')
            msg[0] = id_byte
            self.packet_id = 0
            self.chksum_due = 0
            self.chksum = 0
            msg = bytes(msg)

        else:  #normal data packet
            msg = b''
            id_byte = coco.DATA + self.packet_id
            msg += id_byte.to_bytes(1, 'little')
            msg += self.get_data_from_tx_buffer(31)
            if (len(msg) < 32):
                self.chksum_due = 1
                while (len(msg) < 32):
                    msg += b'\xf0'
            self.chksum ^= int.from_bytes(msg, 'little')
            self.packet_id += 1

        return msg

    def get_bc_packet(self):

        if (self.packet_id == MAX_PACKET_BEFORE_BC_CHECKSUM):
            self.chksum_due = 1

        if (len(self.tx_buffer) == 0):
            self.chksum_due = 1

        if self.chksum_due:  #checksum packet
            id_byte = coco.BROADCAST_CHKSUM + self.packet_id
            msg = bytearray()
            msg += self.chksum.to_bytes(32, 'little')
            msg[0] = id_byte
            self.packet_id = 0
            self.chksum_due = 0
            self.chksum = 0
            msg = bytes(msg)

        else:  #normal data packet
            msg = b''
            id_byte = coco.BROADCAST_DATA + self.packet_id
            msg += id_byte.to_bytes(1, 'little')
            #msg += b'\x00'
            msg += self.get_data_from_tx_buffer(31)

            if (len(msg) < 32): #auffuellen mit f0 falls .. ja falls .. ja falls das Paket sonst nicht vollstaendig ist
                self.chksum_due = 1
                while (len(msg) < 32):
                    msg += b'\xf0'
            #checksum to check packet integrity. Doch nicht erforderlich
            # msg=bytearray(msg)# convert to bytearray
            # for i in range(2,32):
            #     msg[1] ^= msg[i]

            self.chksum ^= int.from_bytes(msg, 'little')
            self.packet_id += 1

        return msg

    