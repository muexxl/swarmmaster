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

        self.mavdistributor = Mavdistributor(self.udpserver, self.swarmmanager)
        self.mavdistributor.start()

        self.terminaloutput = TerminalOutput(self.swarmmanager)
        self.terminaloutput.start()

        self.udplistener = UDPListener()
        self.udplistener.start()

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
            logger.debug('Swarmmaster\t| Checking Radio')
            msg = self.radiolink.check_radio()
            if msg:
                self.messagehandler.handle_msg(msg)

            if self.udplistener.data_available:
                self.broadcast_rtcm_data_from_udp_listener()

            client = self.swarmmanager.next_client()
            if client:
                self.talk_to_client(client)
                self.mavpacker.check_client(client)
            else:
                time.sleep(0.5)

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

        for i in range(3):
            msg = client.get_packet()
            logger.debug(
                f'Swarmmaster\t| Sending to client # {client.id} of {len(self.swarmmanager.clients)} : {msg}'
            )
            success = self.radiolink.send(msg)
            if success:
                answer = self.radiolink.check_radio()
                self.messagehandler.handle_msg(answer)
                logger.debug(f'Swarmmaster\t| Received answer : {answer}')
            else:
                self.swarmmanager.report_fail()
                break

        self.radiolink.radio.startListening()

    def broadcast_rtcm_data_from_udp_listener(self):
        #logger.debug(f'Swarmmaster\t| Called function broadcast ...')
        self.udplistener.rx_lock.acquire()
        data = self.udplistener.rx_buf[:]
        self.udplistener.rx_buf = b''
        self.udplistener.data_available = False
        self.udplistener.rx_lock.release()

        self.terminaloutput.stats_bytes_broadcasted += len(data)
        counter = 0
        checksum = 0
        while data:
            prefix = (0xd0 + (counter % 15)).to_bytes(1, 'big')
            msg = prefix + data[:31]  #msg=RTCM_PREFIX + data[:31]
            self.radiolink.send_to_broadcast(msg)
            if (len(data) < 31):
                data += b'\x00' * (31 - len(data))
            checksum ^= int.from_bytes(data[:31], 'big')
            counter += 1
            logger.info(f'Swarmmaster\t| publishing via broadcast: {msg}')
            data = data[31:]

        prefix = b'\xdf'
        msg = prefix + checksum.to_bytes(31, 'big')
        self.radiolink.send_to_broadcast(msg)
        logger.info(f'Swarmmaster\t| publishing Checksum via broadcast: {msg}')

    def send_heartbeat_if_due(self):
        now = time.time()
        if (now - self.time_at_last_heartbeat
            ) > 2:  #Emit Heartbeat Every two seconds
            self.time_at_last_heartbeat = now
            heartbeat_msg = b'H'  # Heartbeat starts with 'H' = chr(0x48)
            heartbeat_msg += int(now).to_bytes(4, 'little')
            self.radiolink.send_to_broadcast(heartbeat_msg)
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
