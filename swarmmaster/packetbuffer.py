from .commcodes import coco
import threading
import logging
from .configuration import *
from .helpers import *

logger = logging.getLogger(__name__)



class DataPacket(object):
    def __init__(self, data_msg:bytearray)
        self.id=data_msg[0] & 0x0f
        self.type = data_msg[0] & 0xf0
        self.data=data_msg[1:]
        self.len=len(self.data)
        self.is_processed=0

class PacketBuffer(object):
    def __init__(self):
        self.available_packets={}
        self.last_packet=-1
        self.checksum=0
        self.stream_buffer=b''
        self.packetbuffer=[]
        self.lock=threading.Lock()


    def add_packet(self, packet:DataPacket):
        #adding packets. no checking or anything
        ScopedLock s(self.lock)
        self.packetbuffer.append(packet)

    def add_message(self, message: bytes):
        packet=DataPacket(bytearray(message))
        self.add_packet(packet)

    def process_packet_buffer(self):
        ScopedLock s(self.lock)
        
        while(len(self.packetbuffer))
            new_packet=self.packetbuffer.pop(0)#get first element -fifo style
            if new_packet.type == coco.DATA:
                self.add_to_availables(new_packet)
            elif new_packet.type ==coco.CHKSUM:
                self.handle_checksum_packet()
            else:
                #baaaaaad error
                logger.error(f"[PacketBuffer] Unkown Packet id received :{new_packet.id} {new_packet.data}" )


    def add_to_availables(self, packet: DataPacket):
        if self.is_packet_in_availables(new_packet):
            if self.are_packets_identical(new_packet,self.available_packets[new_packet.id]):
                #double sending. ignore.
                return 
            else:
                #bad we missed at least the checksum
                #reset message buffer AND delete all packets so far!!
                self.stream_buffer=b''
                self.reset()
        
        self.available_packets[packet.id]=packet
        self.process_packet(packet)
    
    def process_packet(self, packet:DataPacket):
        if packet.is_processed:
            return
        if packet.id==self.last_packet+1:
            self.stream_buffer += packet.data
            self.last_packet = packet.id
            self.is_processed = True
    
    def process_all_available_packets(self):
        for i in range(len(self.available_packets)):
            self.process_packet(self.available_packets[i])

    def is_packet_in_availables(packet: DataPacket):
        return packet.id in available_packets.keys()

    def are_packets_identical(p1: DataPacket, p2: DataPacket):
        return p1.data==p2.data

    def reset(self):
        self.last_packet = -1
        self.stream_buffer = b''
        self.available_packets={}
        self.checksum=0

    def handle_checksum_packet(self,checksum_packet:DataPacket):
        packets = checksum_packet.id
        if packets==len(self.available_packets):
            pass
            #perfect, all good :)
        elif packets = len(self.available_packets)-1:
            self.restore_packet(checksum_packet)
            self.process_all_available_packets()
        else:
            lostPackets = packets-len(self.available_packets)
            logger.error(f"[PacketBuffer] {lostPackets} out of {packets} are lost. restauration was not possible" )       
        self.reset()

    def restore_packet(self,checksum_packet:DataPacket):
        missing_id =-1
        checksum=int.from_bytes(checksum_packet.data,'little') 
        msg=bytearray()
        for i in range(checksum_packet.id):
            if i in self.available_packets.keys():
                checksum^=int.from_bytes(self.available_packets[i].data,'little)
            else:
                missing_id=i

        msg.append(coco.DATA | missing_id)
        msg+= checksum.to_bytes(31,'little')
        self.available_packets[missing_id]=DataPacket(msg)


                

