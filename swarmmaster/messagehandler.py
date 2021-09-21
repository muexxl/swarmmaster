import logging
import struct

from .swarmmanager import SwarmManager
from .radiolink import Radiolink
from .radioconfig import RadioConfig
from .commcodes import coco
from .helpers import *
from .dronedb import DroneDB
from .swarmclient import SwarmClient

from .configuration import *

import logging

logger = logging.getLogger(__name__)


class MessageHandler(object):
    def __init__(self,
                 radiolink=Radiolink(25, 0),
                 swarmmanager=SwarmManager(),
                 dronedb=DroneDB('default.db')):

        self.swarmmanager = swarmmanager
        self.radiolink = radiolink  #CE on GPIO 25, CSN on SPI 0.0 aka GPIO 8
        self.radioconfig = radiolink.config
        self.droneDB = dronedb

        self.sm = self.swarmmanager
        self.rl = self.radiolink
        self.db = self.droneDB

    def handle_msg(self, msg):

        if not len(msg):
            # raise EmptyMessageException(
            #     'Messagehandler\t| Received blank message. Unable to handle blank message'
            # )
            
            return

        message_id = msg[0]
        #logger.info(f'[MessageHandler] Received message : {msg[:10]}')
        if message_id == coco.REGISTRATION_REQUEST:
            self.handle_registration_request(msg)
        elif message_id & 0xf0 ==coco.DATA:
            self.swarmmanager.current_client.add_msg_to_packet_buffer(msg)
        elif message_id & 0xf0 == coco.CHKSUM:
            self.swarmmanager.current_client.add_msg_to_packet_buffer(msg)
        else:
            logger.error(f"[MessageHandler] Unknown Message received{msg.hex()}")
             
    def handle_config_msg(self, msg):
        config_code = msg[1]
        if config_code == coco.REGISTRATION_REQUEST:
            self.handle_registration_request(msg)
        elif config_code == coco.DEAUTH_REQUEST:
            self.deauth_client(msg)
        elif config_code == coco.PONG:
            logger.info(f"Messagehandler\t| Pong received")
        elif config_code == coco.PING:
            logger.info(f"Messagehandler\t| Ping received")
        else:
            raise UnknownMessageException(
                f"Messagehandler\t| Received Unknown Config Message :{msg.hex()}"
            )

    def handle_data_msg(self, msg):
        logging.debug(f'Messagehandler\t| Handling data msg {msg.hex()}')
        self.swarmmanager.current_client.add_data_to_rx_buffer(msg)
        if len(msg) < 32:
            self.swarmmanager.current_client.prio += 1  #increase prio if message is not "complete"

    def handle_registration_request(self, msg):
        if len(msg) == 19:
            (id0, id1, id2, devid, crc) = struct.unpack('<LLLLH', msg[1:])
        else:
            logger.error(
                f'Messagehandler\t| Registration Message with incorrect lenght received {msg.hex()}'
            )
            return

        if crc_check(msg[:17], crc):
            pass
        else:
            logger.error(
                f'Messagehandler\t| Registration Message with incorrect CRC received {msg.hex()}'
            )
            return

        sc = SwarmClient()
        sc.uid0 = id0
        sc.uid1 = id1
        sc.uid2 = id2
        sc.devid = devid
        sc.id = self.droneDB.get_client_id(sc)

        return self.sm.add_client(sc.id,sc)

    def deauth_client(self, msg):

        id = struct.unpack('<H', msg[3:5])[0]
        return self.swarmmanager.remove_client(id)

    def next_client(self):
        self.swarmmanager.next_client()
