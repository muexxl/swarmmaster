from .swarmmanager import SwarmManager
from .radiolink import Radiolink
from .radioconfig import RadioConfig
import commcodes as coco

class MessageHandler():

    def __init__(self):
        
        self.swarmmanager = SwarmManager()
        self.radiolink = Radiolink(25,0) #CE on GPIO 25, CSN on SPI 0.0 aka GPIO 8  
        self.radioconfig =RadioConfig()
        
        self.sm = self.swarmmanager
        self.rl = self.radiolink

    def talk_to_client(self):

        client = self.swarmmanager.current_client()
        self.radiolink.send_to_id(client.id,)
    
    def handle_msg(self,msg):
        message_id = msg[0]
        if message_id == coco.CONFIGMSG:
            self.handle_config_msg(msg)

    def handle_config_msg(self,msg):
        config_code = msg[1]
        if config_code == coco.REGISTRATION_REQUEST:
            self.register_client(msg)
    
    def register_client(self, msg):
        id = struct.unpack('<H',msg[3:5])[0]
        self.swarmmanager.add_client(id)
        