
import logging
import sys

from .radiolink import Radiolink
from .core import SwarmMaster
from .messagehandler import MessageHandler
from .radioconfig import RadioConfig
from .swarmclient import SwarmClient
from .swarmmanager import SwarmManager
from .dronedb import DroneDB
from .helpers import *

from .mavpacker import Mavpacker
from .mavdistributor import Mavdistributor
from .udpserver import UDPServer
from .commcodes import coco

from .datapacket import DataPacket
from .packetbuffer import PacketBuffer

def set_logger_level():
    for a in sys.argv:
        if a == "-d":
            set_logger_level_debug()
        elif a == "--debug":
            set_logger_level_debug()


def set_logger_level_debug():
    logger.level=logging.DEBUG

logging.basicConfig(format='[%(levelname)8s]\t%(asctime)s: %(message)s ', datefmt='%d.%m.%Y %H:%M:%S', filename='swarmmaster.log', filemode='a', level=logging.INFO)
logger = logging.getLogger(__name__)
set_logger_level()

