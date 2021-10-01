from .swarmclient import SwarmClient
from .swarmmanager import SwarmManager
from .udpserver import UDPServer
from .commcodes import coco

from . import onedrone as mavlink


import struct
import logging
import socket
import threading
import time

logger = logging.getLogger(__name__)

#from pymavlink.dialects.v20 import ardupilotmega as mavlink2

class Mavpacker(object):
    
    def __init__(self, udpserver : UDPServer):
        self.output = open('mavpacker.log','wb')
        self.mav = mavlink.MAVLink(self.output)
        self.mav.robust_parsing= True
        self.udp_server = udpserver
        self.client = None
    
    def __del__(self):        
        self.output.close()
        
    def check_client(self, client: SwarmClient):
        self.client = client
        packet_buffer=client.packet_buffer
        packet_buffer.process_packet_buffer()
        if (not len(packet_buffer.stream_buffer)):
            return
        packet_buffer.stream_buffer_lock.acquire()
        self.mav.buf = packet_buffer.stream_buffer
        self.mav.buf_index = 0
        self.parse_mav_buffer()
        
        #remove buffer elements that have been already parsed
        packet_buffer.stream_buffer = self.mav.buf[self.mav.buf_index:]
        packet_buffer.stream_buffer_lock.release()

    def parse_mav_buffer(self):
        continue_parsing = True
        old_buf_index = 0
        while continue_parsing:
            try:
                msg = self.mav.parse_char('')
                if msg:
                    self.handle_mav_msg(msg)
                elif msg ==None :
                    if self.mav.buf_index and (old_buf_index != self.mav.buf_index) : 
                        logger.info(f'MAVPACK | Dropping bad data because of No MAVLINK Message:{self.mav.buf[old_buf_index]}')

            except mavlink.MAVError:
                self.mav.buf_index =old_buf_index + 1
                logger.info(f'MAVPACK | Dropping bad data because of MAVError:{self.mav.buf[old_buf_index]}')

            #check if end condition is met
            if old_buf_index == self.mav.buf_index: 
                continue_parsing= False
            else:
                old_buf_index = self.mav.buf_index

    def handle_mav_msg(self, msg):
            client =  self.client
            
            if msg.get_msgId() == -1 : # Bad Data!
                logger.debug(f'MAVPACK | Dropping data because of BAD DATA Mavlink Message:{msg.get_msgbuf()}')
            else:
                if msg._header.srcSystem == client.id:
                    client.mav_id_correct = True
                    self.udp_server.publish_via_udp(msg.get_msgbuf())
                    try:
                        logger.info(f'MAVPACK | Sending as SrcSystem {msg._header.srcSystem} via upd: {msg.to_json()}')
                    except TypeError:
                        logger.debug(f'MAVPACK | Sending via udp RAW {msg.get_msgbuf()}')
                    
                else:
                    logger.warning(f'MAVPACKER|  Client #{client.id:04x} tried to send as #{msg._header.srcSystem:02x} MSG: {msg.to_json()}')
                    client.mav_id_correct = False
                    self.set_client_id(client)
        
    def set_client_id(self, client:SwarmClient):

        if time.time() - client.mav_id_request_sent > 2: 
            logger.debug(f'MAVPACKER| Setting Client ID for Client #{client.id:04x}')
            
            # send new SYSID 
            param_id= b"SYSID_THISMAV"
            param_value = client.id / 1.0
            param_type = mavlink.MAV_PARAM_TYPE_INT16
            msg = self.mav.param_set_encode(0, 0, param_id, param_value, param_type)
            client.tx_lock.acquire()
            client.tx_buffer = bytearray(msg.pack(self.mav))
            client.tx_lock.release()
            
            #request reboot
            msg = self.mav.command_long_encode(0, 0, mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN, 0, 1, 1, 0, 0, 0, 0, 0)
            
            client.tx_lock.acquire()
            client.tx_buffer += bytearray(msg.pack(self.mav))
            client.tx_lock.release()           
            
            client.mav_id_request_sent = time.time()
        else:
            logger.debug(f'MAVPACKER | Not sending MAV ID request again')
    
    def request_client_id(self, client:SwarmClient):
        param_id= b"SYSID_THISMAV"
        param_index = 1
        msg = self.mav.param_request_read_encode(0,0,param_id, param_index)
        client.tx_lock.acquire()
        client.tx_buffer += msg.pack(self.mav)
        client.tx_lock.release()
            
    def request_parameters(self, client:SwarmClient):
        logger.info('MAVPACK | Requesting parameters')
        msg = self.mav.MAVLink_param_request_list_message(0,0)
        client.tx_lock.acquire()
        client.tx_buffer += msg.pack(self.mav)
        client.tx_lock.release()
