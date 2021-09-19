from .commcodes import coco
import threading
import logging
from .configuration import *
from .helpers import *

logger = logging.getLogger(__name__)

class DataPacket(object):
    def __init__(self, data_msg:bytearray):
        self.type_id=data_msg[0]
        self.type = data_msg[0] & 0xf0
        self.id=data_msg[0] & 0x0f
        self.data=data_msg[1:]
        self.len=len(self.data)
        self.is_processed=0
