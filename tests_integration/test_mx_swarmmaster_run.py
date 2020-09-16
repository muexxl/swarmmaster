# python -m swarmmaster.tests_integration.test_mx_swarmmaster_run
from ..swarmmaster import *
import time
counter = 0
sm = Swarmmaster()
while 1:
    msg = sm.radiolink.check_radio()
    if msg:
        sm.messagehandler.handle_msg(msg)
    client = sm.swarmmanager.next_client()
    if client:
        #sm.ping_current_client()
        msg = f"Hello #{client.id:04x} msg number {counter}".encode()
        counter += 1
        client.add_data_to_tx_buffer(msg)
        sm.talk_to_client(client)

    time.sleep(0.1)