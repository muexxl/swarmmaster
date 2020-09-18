# python -m swarmmaster.tests_integration.test_mx_swarmmaster_run
from ..swarmmaster import *
import time
counter = 0
sm = Swarmmaster()
mp = Mavpacker()
while 1:
    msg = sm.radiolink.check_radio()
    if msg:
        sm.messagehandler.handle_msg(msg)
    
    client = sm.swarmmanager.next_client()
    if client:
        sm.talk_to_client(client)
        mp.check_client(client)
