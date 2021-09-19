from .commcodes import coco
import threading
import logging
from .configuration import *
from .helpers import *
from .datapacket import DataPacket

logger = logging.getLogger(__name__)


class PacketBuffer(object):
    def __init__(self):
        self.available_packets={}
        self.last_packet=-1
        self.checksum=0
        self.stream_buffer=bytearray()
        self.packet_buffer=[]
        self.packet_buffer_lock=threading.Lock()
        self.stream_buffer_lock=threading.Lock()
        self.received_bytes_brutto=0
        self.received_bytes_netto=0
        self.received_packets=0
        self.double_packets=0
        self.lost_packets=0
        self.restored_packets=0

    def add_packet(self, packet:DataPacket):
        #adding packets. no checking or anything
        s=ScopedLock(self.packet_buffer_lock)
        self.packet_buffer.append(packet)
        self.received_packets+=1
        self.received_bytes_brutto+=32
        

    def add_message(self, message: bytes):
        packet=DataPacket(bytearray(message))
        self.add_packet(packet)

    def process_packet_buffer(self):
        s=ScopedLock(self.packet_buffer_lock)
        while(len(self.packet_buffer)):
            new_packet=self.packet_buffer.pop(0)#get first element -fifo style
            if new_packet.type == coco.DATA:
                self.add_to_availables(new_packet)
            elif new_packet.type ==coco.CHKSUM:
                self.handle_checksum_packet(new_packet)
            else:
                #baaaaaad error
                logger.error(f"[packet_buffer] Unkown Packet id received :{new_packet.id} {new_packet.data}" )


    def add_to_availables(self, new_packet: DataPacket):
        if self.is_packet_in_availables(new_packet):
            if self.are_packets_identical(new_packet,self.available_packets[new_packet.id]):
                self.double_packets+=1
                return 
            else:
                #bad we missed at least the checksum
                #reset message buffer AND delete all packets so far!!
                self.stream_buffer_lock.acquire()
                self.stream_buffer=bytearray()
                self.stream_buffer_lock.release()
                self.reset()
        
        self.available_packets[new_packet.id]=new_packet
        self.process_packet(new_packet)
    
    def process_packet(self, packet: DataPacket):
        if packet.is_processed:
            return
        if packet.id==self.last_packet+1:
            self.stream_buffer_lock.acquire()
            self.stream_buffer += packet.data
            self.stream_buffer_lock.release()
            self.last_packet = packet.id
            self.received_bytes_netto+=31
            packet.is_processed = True
            
    
    def process_all_available_packets(self):
        for i in range(len(self.available_packets)):
            self.process_packet(self.available_packets[i])

    def is_packet_in_availables(self, packet: DataPacket):
        return packet.id in self.available_packets.keys()

    def are_packets_identical(self, p1: DataPacket, p2: DataPacket):
        return p1.data==p2.data

    def reset(self):
        self.last_packet = -1
        self.available_packets={}
        self.checksum=0

    def handle_checksum_packet(self,checksum_packet:DataPacket):
        packets = checksum_packet.id
        available_packets = len(self.available_packets)
        if packets==available_packets:
            pass
            #perfect, all good :)
        elif packets == available_packets+1:
            #restore packet
            self.restore_packet(checksum_packet)
            self.process_all_available_packets()
            self.lost_packets +=1
        elif packets == 0:
            
            if available_packets==0:
                #perfect. this is an empty checksum all is perfect
                pass
            else:
                logger.error(f"[PacketBuffer] previous checksum packet was lost" )
                self.stream_buffer_lock.acquire()
                self.stream_buffer=bytearray()
                self.stream_buffer_lock.release()
                self.reset()
                self.lost_packets+=1
                
        elif available_packets==0:
            #double sending of checksum
            self.double_packets+=1
        else:
            lostPackets = packets-len(self.available_packets)
            if lostPackets<=0:
                lostPackets=len(self.available_packets)+1
            logger.error(f"[PacketBuffer] {lostPackets} out of {packets} are lost. restauration was not possible" )       
            self.lost_packets+=lostPackets
            self.stream_buffer_lock.acquire()
            self.stream_buffer=bytearray()
            self.stream_buffer_lock.release()

        self.reset()

    def restore_packet(self,checksum_packet:DataPacket):
        missing_id =-1
        checksum=int.from_bytes(checksum_packet.data,'little') 
        msg=bytearray()
        for i in range(checksum_packet.id):
            if i in self.available_packets.keys():
                checksum^=int.from_bytes(self.available_packets[i].data,'little')
            else:
                missing_id=i

        msg.append(coco.DATA | missing_id)
        msg+= checksum.to_bytes(31,'little')
        self.available_packets[missing_id]=DataPacket(msg)
        self.restored_packets +=1


                

