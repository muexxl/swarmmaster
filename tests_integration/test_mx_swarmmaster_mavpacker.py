# python -m swarmmaster.tests_integration.test_mx_swarmmaster_mavpacker
from ..swarmmaster import *
import time
import logging
logger = logging.getLogger(__name__)

counter = 1
sm = SwarmMaster()
mp = sm.mavpacker
us = sm.udpserver
md = sm.mavdistributor
to = sm.terminaloutput

try:
    request_pending = True
    time1 = time.time()
    while 1:
        msg = sm.radiolink.check_radio()
        if msg:
            sm.messagehandler.handle_msg(msg)
        client = sm.swarmmanager.next_client()
        if client:
            #sm.ping_current_client()

            sm.talk_to_client(client)
            mp.check_client(client)
            if time.time() - time1 > 20.0 :
                logger.info(f'requesting Client ID Change to {counter}')
                save_id = client.id

                client.id = counter
                
                mp.set_client_id(client)
                
                client.id = save_id
                counter+=1
                time1 = time.time()


        time.sleep(0.1)

except KeyboardInterrupt:
    us.stop()
    md.stop()
    to.stop()