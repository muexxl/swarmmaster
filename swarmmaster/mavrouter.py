from .swarmclient import SwarmClient
from .ardupilotmega import *
from .swarmmanager import SwarmManager

import struct
import logging
import socket
import threading
logger = logging.getLogger(__name__)

#from pymavlink.dialects.v20 import ardupilotmega as mavlink2

class Mavrouter(object):
    
    def __init__(self):
        self.output = open('mavlink.log','wb')
        self.output2 = open('mavlink2.log','wb')
        self.mav = MAVLink(self.output)
        self.mav_gcs = MAVLink(self.output2)
        self.mav.robust_parsing= True
        self.udp_server = UDPServer()
        self.udp_server.run()
        self.client = None
        self.swarmanager = SwarmManager()
    
    def __del__(self):
        
        self.udp_server.keep_running = False
        self.udp_server.rx_lock.release()
        self.udp_server.tx_lock.release()
        print("DEL MAVROUTER")
        self.udp_server.t1.join()
        print("T1 STOPPED")
        
        self.output.close()
        self.output2.close()
        
    def check_client(self, client: SwarmClient):
        self.client = client
        self.mav.buf_index = 0
        self.mav.buf.clear()
        client.rx_lock.acquire()
        logger.debug(f'Client Buffer BEFORE extracting messages: \n {client.rx_buffer}')
        self.mav.buf = client.rx_buffer
        self.parse_mav_buffer()
        #remove buffer elements that have been already parsed
        client.rx_buffer = self.mav.buf[self.mav.buf_index:]
        logger.debug(f'Client Buffer AFTER extracting messages: \n {client.rx_buffer}')
        client.rx_lock.release()

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
                        logger.info(f'Dropping bad data because of No MAVLINK Message:{self.mav.buf[old_buf_index]}')

            except MAVError:
                self.mav.buf_index =old_buf_index + 1
                logger.info(f'Dropping bad data because of MAVError:{self.mav.buf[old_buf_index]}')

            #check if end condition is met
            if old_buf_index == self.mav.buf_index: 
                continue_parsing= False
            else:
                old_buf_index = self.mav.buf_index

    def handle_mav_msg(self, msg):
            client =  self.client
            
            if msg.get_msgId() == -1 : # Bad Data!
                logger.info(f'Dropping data because of BAD DATA Mavlink Message:{msg.get_msgbuf()}')
            else:
                if client.mav_id_correct:
                    self.udp_server.publish_via_udp(msg.get_msgbuf())
                    try:
                        logger.info(f'Sending via upd: {msg.to_json()}')
                    except TypeError:
                        logger.debug(f'Sending via udp RAW {msg.get_msgbuf()}')
                
                else:
                    if msg.get_msgId() == MAVLINK_MSG_ID_PARAM_VALUE:
                        msg_dict = msg.to_dict()
                        logger.debug(f'Message is {msg.to_json()}')
                        if msg_dict['param_id'] == "SYSID_THISMAV":
                            
                            if msg_dict['param_value'] == client.id :
                                client.mav_id_correct = True
                                logger.debug(f'Cliend.mav_id_correct is {client.mav_id_correct}')


                if not client.mav_id_correct:
                    self.set_client_id(client)
        
    def set_client_id(self, client:SwarmClient):
        self.client = client
        param_id= b"SYSID_THISMAV"
        param_value = client.id / 1.0
        param_type = MAV_PARAM_TYPE_INT16
        msg = self.mav.param_set_encode(0, 0, param_id, param_value, param_type)
        client.tx_lock.acquire()
        client.tx_buffer += msg.pack(self.mav)
        client.tx_lock.release()
    
    def request_client_id(self, client:SwarmClient):
        param_id= b"SYSID_THISMAV"
        param_index = 1
        msg = self.mav.param_request_read_encode(0,0,param_id, param_index)
        client.tx_lock.acquire()
        client.tx_buffer += msg.pack(self.mav)
        client.tx_lock.release()
            
    def request_parameters(self, client:SwarmClient):
        logger.info('Requesting parameters')
        msg = MAVLink_param_request_list_message(0,0)
        client.tx_lock.acquire()
        client.tx_buffer += msg.pack(self.mav)
        client.tx_lock.release()

    def handle_incoming_udp(self):
        if self.udp_server.data_available:
            self.udpserver.rx_lock.acquire()
            self.mav_udp.buf =self.udp_server.rx_buf[:]  
            self.parse_mav_udp_buffer()          
            self.udp_server.rx_lock.release()

    def parse_mav_udp_buffer(self):
        continue_parsing = True
        old_buf_index = 0
        while continue_parsing:
            try:
                msg = self.mav_udp.parse_char('')
                if msg:
                    self.handle_mav_udp_msg(msg)
                elif msg ==None :
                    if self.mav_udp.buf_index and (old_buf_index != self.mav_udp.buf_index) : 
                        logger.info(f'Dropping bad data because of No MAVLINK Message:{self.mav_udp.buf[old_buf_index]}')

            except MAVError:
                self.mav_udp.buf_index =old_buf_index + 1
                logger.info(f'Dropping bad data because of MAVError:{self.mav.buf[old_buf_index]}')

            #check if end condition is met
            if old_buf_index == self.mav.buf_index: 
                continue_parsing= False
            else:
                old_buf_index = self.mav_udp.buf_index
    
    def handle_mav_udp_msg(self, msg):
        try:
            logging.debug(f'Handling incoming udp messsage {msg.to_json()}')
            msg_dict = msg.to_dict()
            client_id = msg_dict['target_system']
            if self.swarmanager.is_client(target_system):
                client = self.swarmanager.get_client(target_system)
                client.add_data_to_tx_buffer(msg.get_msgbuf())

        except KeyError:
            logger.debug('Keyerror in handle_mav_udp_msg')  
        except :
            logger.debug('Another Error in handle mav udp msg')


    #     len = self.contains_message(client.rx_buffer)
    #     packet = None
    #     if len:
    #         packet = client.rx_buffer[:len]
    #         client.rx_buffer = client.rx_buffer[len:]
    #         logger.debug(
    #             f"Extracted {len} bytes from RX Buffer of Client #{client.id:04x} "
    #         )
    #     else:
    #         packet = None
    #     client.rx_lock.release()
    #     return packet

        
    ## IDEA
    # 1. mavobject erzeugen
    # 2. mavobject nutzen um Nachrichten zu extrahieren
    # 3. ggfs. mavobject auch zum veroeffentlichen per UDP nutzen. hmmm.
    # self.mav = MAVlink(file) 
    # self.mav.buf = client.buf[:] COPY CLIENT BUF
    # self.mav.parsebuffer

class UDPServer(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.ip = '<broadcast>'
        self.port = 14550
        self.addr = (self.ip, self.port)
        
        self.rx_buf = bytearray()
        self.rx_lock = threading.Lock()
        self.data_available = False

        self.tx_buf = bytearray()
        self.tx_lock = threading.Lock()
        self.keep_running = True
        self.max_buf_size = 0xffff

    def run(self):
        self.t1 = threading.Thread(target=self._run)
        self.t1.start()

    def _run(self):
        logger.info('Starting UDP Server')
        while self.keep_running:
            if self.tx_buf:
                self._send()
            self._receive()
        logger.info('Stopping UDP Server')

    def _receive(self):

        print('UDP checking receive')
        data = self.sock.recvfrom(self.max_buf_size)   
        if data:
            self.rx_lock.acquire()
            self.rx_buf +=bytearray(data)
            self.rx_lock.release()
            self.data_available = True
        
    def _send(self):
        self.tx_lock.acquire()
        self.sock.sendto(self.tx_buf[:self.max_buf_size], self.addr)
        self.tx_buf = self.tx_buf[self.max_buf_size:]
        self.tx_lock.release()

    def publish_via_udp(self, data):
        self.tx_lock.acquire()
        self.tx_buf +=bytearray(data)
        self.tx_lock.release()

            
