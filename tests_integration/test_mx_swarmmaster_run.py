# python -m swarmmaster.tests_integration.test_mx_swarmmaster_run
from ..swarmmaster import *
import time
counter = 0
sm = Swarmmaster()
us = UDPServer()
mp = Mavpacker(us)
md = Mavdistributor(us, sm.swarmmanager)
us.start()
md.start()

try:

except KeyboardInterrupt:
    us.stop()
    md.stop()