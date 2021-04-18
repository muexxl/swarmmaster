#!/usr/bin/env python3
from .radiolink import Radiolink
from .messagehandler import MessageHandler
from .swarmmanager import SwarmManager
from .swarmclient import SwarmClient
from .commcodes import coco
from .helpers import *
from .udpserver import UDPServer
from .mavpacker import Mavpacker
from .mavdistributor import Mavdistributor
from .terminaloutput import TerminalOutput
from .udplistener import UDPListener

import threading
import time
import logging
logger = logging.getLogger(__name__)


class SwarmMaster():
    """docstring for Swarmmaster."""
    
    def __init__(self):
        self.swarmmanager = SwarmManager()
        self.radiolink = Radiolink(25,0)
        self.udpserver = UDPServer()
        self.udpserver.start()

        self.mavdistributor = Mavdistributor(self.udpserver, self.swarmmanager)    
        self.mavdistributor.start()
        
        self.terminaloutput = TerminalOutput(self.swarmmanager)
        self.terminaloutput.start()
        
        self.udplistener=UDPListener()
        self.udplistener.start()

        self.mavpacker = Mavpacker(self.udpserver)
        self.messagehandler = MessageHandler(radiolink = self.radiolink, swarmmanager=self.swarmmanager)
        
        self.rxtx_counter_lock = threading.Lock()
        self.rx_counter = 0
        self.tx_counter = 0
        self.time_at_last_heartbeat = 0

    def run(self):
        logger.info('Starting up Swarmmaster')
        while 1:
            logger.debug('Swarmmaster\t| Checking Radio')
            msg = self.radiolink.check_radio()
            if msg:
                self.messagehandler.handle_msg(msg)
            
            if self.udplistener.data_available:
                logger.debug('Swarmmaster\t| Data available on  UDP listener')
                #self.broadcast_data_from_udp_listener()

            client = self.swarmmanager.next_client()
            if client:
                self.talk_to_client(client)
                self.mavpacker.check_client(client)
            else:
                time.sleep(0.5)
            
            self.send_heartbeat_if_due()    

    def talk_to_client(self,client:SwarmClient):
        self.radiolink.open_pipes_to_id(client.id)
        msg=bytearray()
        msg.append(client.last_msg_id)
        msg+= client.read_data_from_tx_buffer(31)
        logger.debug(f'Swarmmaster\t| Sending to client # {client.id} of {len(self.swarmmanager.clients)} : {msg}')
        success = self.radiolink.send(msg)
        if success:

            answer = self.radiolink.check_radio()
            client.remove_data_from_tx_buffer(31)
            logger.debug(f'Swarmmaster\t| Received answer : {answer}')
            try:
                self.messagehandler.handle_msg(answer)
                client.fail_counter = 0
            except EmptyMessageException as e:
                logger.exception(e.msg)
        else:
            self.swarmmanager.report_fail()
        self.radiolink.radio.startListening()
    
    def broadcast_data_from_udp_listener():
        logger.debug(f'Swarmmaster\t| Called function broadcast ...')
        self.udplistener.rx_lock.acquire()
        data= self.udplistener.rx_buf[:]
        self.udplistener.rx_buf=b''
        self.udplistener.data_available = False
        self.udplistener.rx_lock.release()
        while data:
            self.radiolink.send_to_broadcast(data[:32])
            logger.debug(f'Swarmmaster\t| publishing via broadcast: {data[:32]}')
            data=data[32:]



    def send_heartbeat_if_due(self):
        now = time.time()
        if (now - self.time_at_last_heartbeat) > 2: #Emit Heartbeat Every two seconds
            self.time_at_last_heartbeat = now
            heartbeat_msg = b'HEARTBEAT'
            heartbeat_msg += int(time.time()).to_bytes(4, 'little')
            self.radiolink.send_to_broadcast(heartbeat_msg)
            logger.debug(f'Swarmmaster\t| Sending Heartbeat : {int(now)}')
            
    def ping_all_clients(self):
        for client in self.swarmmanager.clients.values():
            self.swarmmanager.current_client=client
            self.ping_current_client()

    def ping_current_client(self):
        current_client = self.swarmmanager.current_client
        id =current_client.id
        logger.info(f'Sending ping to Client # {id:04x}')
        msg= bytearray(6)
        msg[0]=coco.CONFIGMSG
        msg[1]=coco.PING
        
        self.radiolink.open_pipes_to_id(id)
        sending_successful = self.radiolink.send(msg)
        if sending_successful :
            logger.info(f"Ping successfully sent to Client # {id:04x}")
            answer = self.radiolink.check_radio()
            if answer:
                logger.info(f"Received Answer : {answer}")
                current_client.fail_counter = 0
            else:
                logger.info("Received blank answer")
        else: 
            logger.warning(f'Ping not answered by Client # {id:04x}')
            self.swarmmanager.report_fail()

        self.radiolink.radio.startListening()
