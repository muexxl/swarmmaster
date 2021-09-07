# -*- coding: utf-8 -*-

import struct


class RadioConfig(object):
    def __init__(self):
        self.CEPin = 22
        self.CSNPin = 0
        
        self.broadcastAddress = 0x1d1d1d.to_bytes(3,'little')
        self.masterAddress = 0x1d1d1e.to_bytes(3,'little')
        
        self.id =0
        self.addressPrefix = 0x2d
        self.channel = 0x64 #CH100 decimal
    
    def get_address_from_id(self, id):
        address = bytearray(3)
        #!! reverse byte order!!
        address[0:2]=struct.pack('<H',id)
        address[2]=self.addressPrefix
        return (bytes(address))

    def get_id_from_address(self, address: bytes):
        id_bytes = address[1:3]
        id = struct.unpack('<H',id_bytes)[0]
        return id

    def get_own_address(self):
        return get_address_from_id(self.id)
    
    def get_master_address(self):
        return self.masterAddress
    
    def get_broadcast_address(self):
        return self.broadcastAddress
