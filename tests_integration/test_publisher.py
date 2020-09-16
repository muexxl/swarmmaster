
# python -m swarmmaster.tests_integration.test_publisher

from ..swarmmaster import *
import time
counter = 0
pub = Publisher()
while 1:
    counter += 1
    message = f'Hello World {counter}!\n'
    logger.debug(f'Sending Message:') 
    logger.debug(message)

    pub.udp_send(message.encode())
    time.sleep(1)