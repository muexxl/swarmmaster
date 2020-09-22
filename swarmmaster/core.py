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
        
        self.mavpacker = Mavpacker(self.udpserver)
        self.messagehandler = MessageHandler(radiolink = self.radiolink, swarmmanager=self.swarmmanager)
        
        self.rxtx_counter_lock = threading.Lock()
        self.rx_counter = 0
        self.tx_counter = 0

    def run(self):
        logger.info('Starting up Swarmmaster')
        while 1:
            logger.debug('Swarmmaster\t| Checking Radio')
            msg = self.radiolink.check_radio()
            if msg:
                self.messagehandler.handle_msg(msg)
            client = self.swarmmanager.next_client()
            if client:
                self.talk_to_client(client)
                self.mavpacker.check_client(client)
            else:
                time.sleep(0.5)

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
