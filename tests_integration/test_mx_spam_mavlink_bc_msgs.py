#! /usr/bin/env python3

#   Invoke via:
#   python test_mx_spam_mavlink_msgs.py

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from swarmmaster import *

sm = SwarmMaster()
us =sm.udpserver
ul =sm.udplistener
md =sm.mavdistributor
to = sm.terminaloutput

CFG_EMIT_HEARTBEAT = 0

DUMMY_MAVLINK_MSG=b'\xfd\x1dDIES_KOENNTE_EINE_MAVLINK_V2_MSG_SEIN\r\n'
DUMMY_MAVLINK_MSG2=b'\xfd\xa6DIES_KOENNTE_EINE_GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANZ SCHOEN LANGE_MAVLINK_V2_MSG_SEIN\r\n'
DUMMY_MAVLINK_MSG3=b'\xfd\xaaDIES_KOENNTE_EINE_GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANZ SCHOEN LANGE_MAVLINK_V2_MSG_SEIN'
DUMMY_MAVLINK_MSG4=b'\xfd\xaaDIES_KOENNTE_EINE_GBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBNZ SCHOEN LBNGE_MBVLINK_V2_MSG_SEIN'


def run():
    #sm.swarmmanager.add_client(3)
    counter=0
    counter_bc=0
    while(1):
        logger.debug('Swarmmaster\t| Checking Radio')
        msg = sm.radiolink.check_radio()
        msg = None
        if msg:
            sm.messagehandler.handle_msg(msg)

        sm.swarmmanager.broadcast_client.add_data_to_tx_buffer(DUMMY_MAVLINK_MSG4+f"{counter_bc:04d}\r\n".encode('ascii'))
        counter_bc +=1
        sm.broadcast_data()

        client = sm.swarmmanager.next_client()
        if client:
            sm.talk_to_client(client)
            sm.mavpacker.check_client(client)
            while (len(client.tx_buffer)<100):
                client.add_data_to_tx_buffer(DUMMY_MAVLINK_MSG3+f"{counter:04d}\r\n".encode('ascii'))
                counter+=1
                

        else:
            time.sleep(0.0)

        time.sleep(1)
        if CFG_EMIT_HEARTBEAT: sm.send_heartbeat_if_due()

try:
    run()

except KeyboardInterrupt:
    us.stop()
    ul.stop()
    md.stop()
    to.stop()
