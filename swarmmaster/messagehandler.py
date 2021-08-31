import logging
import struct
import sqlite3

from .swarmmanager import SwarmManager
from .radiolink import Radiolink
from .radioconfig import RadioConfig
from .commcodes import coco
from .helpers import *

from .configuration import *



import logging
logger = logging.getLogger(__name__)

class MessageHandler(object):

    def __init__(self, radiolink=Radiolink(25,0),swarmmanager = SwarmManager() ):
        
        self.swarmmanager = swarmmanager
        self.radiolink =radiolink #CE on GPIO 25, CSN on SPI 0.0 aka GPIO 8  
        self.radioconfig = radiolink.config
        
        self.sm = self.swarmmanager
        self.rl = self.radiolink

    def handle_msg(self,msg):
        if not len(msg):
            raise EmptyMessageException('Messagehandler\t| Received blank message. Unable to handle blank message')

        message_id = msg[0]
        if message_id == coco.REGISTRATION_REQUEST:
            self.register_client(msg)
        elif message_id < coco.MAX_MSG_ID:
            self.handle_data_msg(msg)
        else:
            raise UnknownMessageException(f"Messagehandler\t| Received Unknown:{msg.hex()}")

    def handle_config_msg(self,msg):
        config_code = msg[1]
        if config_code == coco.REGISTRATION_REQUEST:
            self.register_client(msg)
        elif config_code == coco.DEAUTH_REQUEST:
            self.deauth_client(msg)
        elif config_code == coco.PONG:
            logger.info(f"Messagehandler\t| Pong received")
        elif config_code == coco.PING:
            logger.info(f"Messagehandler\t| Ping received")
        else:
            raise UnknownMessageException(f"Messagehandler\t| Received Unknown Config Message :{msg.hex()}")
    
    def handle_data_msg(self, msg):
        logging.debug(f'Messagehandler\t| Handling data msg {msg.hex()}')
        self.swarmmanager.current_client.add_data_to_rx_buffer(msg)
        if len(msg) < 32 :
            self.swarmmanager.current_client.prio +=1 #increase prio if message is not "complete"


    def register_client(self, msg):
        if len(msg) == 19:
            (id0,id1,id2,devid,crc) = struct.unpack('<LLLLH',msg[1:])
            id0=0
        else :
            logger.error(f'Messagehandler\t| Registration Message with incorrect lenght received {msg.hex()}')
        
        return self.swarmmanager.add_client(id)
         
    def deauth_client(self, msg):
        
        id = struct.unpack('<H',msg[3:5])[0]
        return self.swarmmanager.remove_client(id)    

    def next_client(self):
        self.swarmmanager.next_client()
