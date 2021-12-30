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
from .dronedb import DroneDB
from .configuration import *

import threading
import time
import logging
import struct

logger = logging.getLogger(__name__)


class SwarmMaster():
    """docstring for Swarmmaster."""
    def __init__(self):
        self.swarmmanager = SwarmManager()
        self.radiolink = Radiolink(25, 0)
        self.droneDB = DroneDB(DRONE_DB_PATH)

        self.udpserver = UDPServer()
        self.udpserver.start()

        self.terminaloutput = TerminalOutput(self.swarmmanager)
        self.terminaloutput.start()

        self.udplistener = UDPListener()
        self.udplistener.start()

        self.mavdistributor = Mavdistributor(self.udpserver, self.udplistener, self.swarmmanager)
        self.mavdistributor.start()

        self.mavpacker = Mavpacker(self.udpserver)
        self.messagehandler = MessageHandler(radiolink=self.radiolink,
                                             swarmmanager=self.swarmmanager,
                                             dronedb=self.droneDB)

        self.rxtx_counter_lock = threading.Lock()
        self.rx_counter = 0
        self.tx_counter = 0
        self.time_at_last_heartbeat = 0

    def run(self):
        logger.info('Starting up Swarmmaster')
        while 1:
            #logger.debug('Swarmmaster\t| Checking Radio')
            msg = self.radiolink.check_radio()
            self.broadcast_data()

            if msg:
                self.messagehandler.handle_msg(msg)

            client = self.swarmmanager.next_client()
            if client:
                self.talk_to_client(client)
                self.mavpacker.check_client(client)
            else:
                time.sleep(0.01)
            

            if CFG_EMIT_HEARTBEAT: self.send_heartbeat_if_due()

    def send_registration_request_ack(self, client: SwarmClient):
        self.radiolink.open_pipes_to_id(MAX_CLIENT_ID)
        msg = bytearray()
        msg += coco.REGISTRATION_REQUEST_ACK.to_bytes(2, 'little')
        msg += client.id.to_bytes(2, 'little')
        msg += client.uid0.to_bytes(4, 'little')
        msg += client.uid1.to_bytes(4, 'little')
        msg += client.uid2.to_bytes(4, 'little')
        crc = crc_calc(msg)
        msg += crc.to_bytes(2, 'little')
        logger.debug(
            f'Swarmmaster\t| Sending Reg Req Ack to client # {client.id} of {len(self.swarmmanager.clients)} : {msg}'
        )

        success = self.radiolink.send(msg)

        client.registration_request_ack_sent = True

        self.radiolink.radio.startListening()

    def talk_to_client(self, client: SwarmClient):

        if (not client.registration_request_ack_sent):
            self.send_registration_request_ack(client)
            return

        self.radiolink.open_pipes_to_id(client.id)


        for i in range(MAX_PACKET_BEFORE_CHECKSUM +1):  #send complete data packets!!
            msg = client.get_packet()
            if msg[0] == 0xc0:
                msg = msg[:1]
            else:
                logger.debug(
                    f'Swarmmaster\t| Sending to client # {client.id} of {len(self.swarmmanager.clients)} : {msg[:10]}'
                )
            #time.sleep(0.01)
            success = self.radiolink.send(msg)
            if success:
                answer = self.radiolink.check_radio()
                self.messagehandler.handle_msg(answer)
            else:
                self.swarmmanager.report_fail()
                break

        self.radiolink.radio.startListening()

    def broadcast_data(self):
        bc = self.swarmmanager.broadcast_client
        packet = bc.get_bc_packet()
        packets = [] #initialize empty list

        while (packet[0] & 0xf0) != coco.BROADCAST_CHKSUM:  #add packets to list until checksum package is reached
            packets.append(packet)
            packet = bc.get_bc_packet()

        checksum_packet = packet #last packet is the checksum
        
        if not len(packets):
            return

        self.radiolink.start_broadcast()

        for i in range(CFG_BROADCAST_REPETITIONS):
            for p in packets:
                self.radiolink.send_to_broadcast(p)

        for i in range(CFG_BROADCAST_REPETITIONS + 2):
            self.radiolink.send_to_broadcast(checksum_packet)

        self.radiolink.stop_broadcast()

    def broadcast_check(self):
        self.radiolink.start_broadcast()
        msg = bytearray(32)
        msg[0] = coco.BROADCAST_CHECK
        for i in range(0x100):
            msg[4] = i  #id ist im 2. 32 bit integer. logisch. oder?
            self.radiolink.send_to_broadcast(msg)
            self.swarmmanager.broadcast_client.bytes_sent += 32
        self.radiolink.stop_broadcast()

    def send_heartbeat_if_due(self):
        now = time.time()
        if (now - self.time_at_last_heartbeat) > 2:  #Emit Heartbeat Every two seconds
            self.time_at_last_heartbeat = now
            heartbeat_msg = b'H'  # Heartbeat starts with 'H' = chr(0x48)
            heartbeat_msg += int(now).to_bytes(4, 'little')
            self.radiolink.start_broadcast()
            self.radiolink.send_to_broadcast(heartbeat_msg)
            self.radiolink.stop_broadcast()
            logger.debug(f'Swarmmaster\t| Sending Heartbeat : {int(now)}')

    def ping_all_clients(self):
        for client in self.swarmmanager.clients.values():
            self.swarmmanager.current_client = client
            self.ping_current_client()

    def ping_current_client(self):
        current_client = self.swarmmanager.current_client
        id = current_client.id
        logger.info(f'Sending ping to Client # {id:04x}')
        msg = bytearray(6)
        msg[0] = coco.CONFIGMSG
        msg[1] = coco.PING

        self.radiolink.open_pipes_to_id(id)
        sending_successful = self.radiolink.send(msg)
        if sending_successful:
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
