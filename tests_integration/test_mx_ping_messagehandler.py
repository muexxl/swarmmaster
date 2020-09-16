
# python -m swarmmaster.tests_integration.test_mx_ping_messagehandler
from ..swarmmaster import *
import time

print("Import successful")

mh = MessageHandler()
while 1:
    mh.ping_client(2)
    time.sleep(1)