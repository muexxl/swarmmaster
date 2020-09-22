from swarmmaster import *

sm = SwarmMaster()
us =sm.udpserver
md =sm.mavdistributor

try:
    sm.run()
except KeyboardInterrupt:
    us.stop()
    md.stop()