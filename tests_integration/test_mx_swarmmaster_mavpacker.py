# python -m swarmmaster.tests_integration.test_mx_swarmmaster_mavpacker
from ..swarmmaster import *
import time
counter = 1
sm = Swarmmaster()
mp = Mavpacker()

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
        if time.time() - time1 > 2.0 :
            logging.info(f'requesting Client ID Change to {counter}')
            mp.request_client_id(client)
            mp.set_client_id(client, counter)
            counter+=1
            time1 = time.time()


    time.sleep(0.1)