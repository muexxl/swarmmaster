from .swarmclient import SwarmClient
from .ardupilotmega import *
from .swarmmanager import SwarmManager
from .udpserver import UDPServer

import logging
import threading

logger = logging.getLogger(__name__)

#from pymavlink.dialects.v20 import ardupilotmega as mavlink2

class Mavdistributor(threading.Thread):
    
    def __init__(self, udpserver: UDPServer,swarmmanager: SwarmManager):
        self.output = open('mavdistributor.log','wb')
        self.mav = MAVLink(self.output)
        self.mav.robust_parsing= True
        self.udp_server = udpserver
        self.client = None
        self.swarmmanager = swarmmanager
        self.keep_running = False
        threading.Thread.__init__(self)
    
    def __del__(self):        
        self.output.close()

    def run(self):
        self.keep_running = True
        mav = self.mav
        us= self.udp_server
        logging.info('MAVDIST | Starting MAVDistributor')
        while self.keep_running:
            if self.udp_server.data_available:
                us.rx_lock.acquire()
                mav.buf += us.rx_buf[:]
                us.rx_buf.clear()
                us.data_available =False
                us.rx_lock.release()
                self.parse_mav_udp_buffer()
            else:
                time.sleep(0.1)
        logging.info('MAVDIST | MAVDistributor is ending')
        
    def stop(self):
        self.keep_running = False
        self.join()    

    def parse_mav_udp_buffer(self):
        continue_parsing = True
        old_buf_index = 0
        while continue_parsing:
            try:
                msg = self.mav.parse_char('')
                if msg:
                    self.handle_mav_udp_msg(msg)
                elif msg ==None :
                    if self.mav.buf_index and (old_buf_index != self.mav.buf_index) : 
                        logger.warning(f'MAVDISTRIBUTOR | Dropping bad data because of No MAVLINK Message:{self.mav.buf[old_buf_index]}')

            except MAVError:
                self.mav.buf_index =old_buf_index + 1
                logger.warning(f'MAVDISTRIBUTOR | Dropping bad data because of MAVError:{self.mav.buf[old_buf_index]}')

            #check if end condition is met
            if old_buf_index == self.mav.buf_index: 
                continue_parsing= False
            else:
                old_buf_index = self.mav.buf_index
        
    def handle_mav_udp_msg(self, msg):
        try:
            logging.debug(f'MAVDISTRIBUTOR | Handling incoming udp messsage {msg.to_json()}')
            msg_dict = msg.to_dict()
            target_system = msg_dict['target_system']
            if self.swarmmanager.is_client(target_system):
                client = self.swarmmanager.get_client(target_system)
                client.add_data_to_tx_buffer(msg.get_msgbuf())
            else :
                logger.warn(f'MAVDISTRIBUTOR | Received Message for Not Registered Client #{target_system:04x}. Message is beeing dropped')
                logger.warn(f'MAVDISTRIBUTOR | Message : {msg.to_json()}')
        except KeyError:
            logger.debug(f'MAVDISTRIBUTOR | Keyerror in handle_mav_udp_msg')  
            logger.debug(f'MAVDISTRIBUTOR | Message is {msg.to_json()}') 



            