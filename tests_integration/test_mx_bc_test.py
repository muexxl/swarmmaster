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

def run():
    #sm.swarmmanager.add_client(3)

    while(1):
        sm.broadcast_check()
        time.sleep(0)
        
try:
    run()

except KeyboardInterrupt:
    us.stop()
    ul.stop()
    md.stop()
    to.stop()
