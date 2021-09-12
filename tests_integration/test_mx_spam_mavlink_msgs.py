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

CFG_EMIT_HEARTBEAT = 1

def run():
    while(1):
        logger.debug('Swarmmaster\t| Checking Radio')
        msg = sm.radiolink.check_radio()
        if msg:
            sm.messagehandler.handle_msg(msg)

        if sm.udplistener.data_available:
            sm.broadcast_rtcm_data_from_udp_listener()

        client = sm.swarmmanager.next_client()
        if client:
            sm.talk_to_client(client)
            sm.mavpacker.check_client(client)
            #spamming request parameter msgs
            while (len(client.tx_buffer)<100):
                sm.mavpacker.request_client_id(client)

            time.sleep(1)
        else:
            time.sleep(0.5)

        if CFG_EMIT_HEARTBEAT: sm.send_heartbeat_if_due()

try:
    run()

except KeyboardInterrupt:
    us.stop()
    ul.stop()
    md.stop()
    to.stop()
