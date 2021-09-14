from  RF24 import *
from .radioconfig import *
from datetime import datetime

import time

class Radiolink():

    def __init__(self, ce_pin= 25, csn_pin=0):
        self.config = RadioConfig()
        self.config.CEPin = ce_pin
        self.config.CSNPin = csn_pin

        self.radio = RF24(self.config.CEPin, self.config.CSNPin)
        self.radio.begin()

        self.radio.setAddressWidth(3)
        self.radio.setAutoAck(1)
        self.radio.enableDynamicPayloads()
        self.radio.enableAckPayload()
        #radio.enableDynamicAck()
        self.radio.setChannel(self.config.channel)
        self.radio.setDataRate(RF24_2MBPS)
        self.radio.setPALevel(RF24_PA_MAX)
        self.radio.setRetries(4,5) #delay x 250us , retries
        self.radio.startListening()
        self.set_adresses()

    def set_adresses(self):

        self.radio.openReadingPipe(0, self.config.get_master_address())
        self.radio.openReadingPipe(1, self.config.get_master_address())
        self.radio.openWritingPipe(self.config.get_master_address())
        self.radio.startListening()

    def open_reading_and_writing_pipe(self, address: bytes):
        self.radio.openReadingPipe(0,address)
        self.radio.openWritingPipe(address)

    def open_pipes_to_id(self, id: int):
        address= self.config.get_address_from_id(id)
        
        self.open_reading_and_writing_pipe(address)
        self.radio.stopListening()

    def send(self, data: bytearray):
        return self.radio.write(data)
        

    def send_to_address(self, address: bytes, data:bytearray):
        self.open_reading_and_writing_pipe(address)
        return self.send(data)

    def send_to_master(self, data:bytearray):
        self.open_reading_and_writing_pipe(self.config.get_master_address())
        self.radio.stopListening()
        self.send(data)
        self.radio.startListening()

    def send_to_broadcast(self, data:bytearray):
        self.open_reading_and_writing_pipe(self.config.get_broadcast_address())
        self.radio.stopListening()
      
        self.radio.write(data,1) # use multicast to signal noAck. not really faster :// approx 30 ms
        
        self.radio.startListening()

    def check_radio(self):
        len = 0
        if self.radio.available():
            len = self.radio.getDynamicPayloadSize()
            return self.radio.read(len)
        else:
            return bytearray(0) # empty bytearray

    def check_radio_and_print_result(self):
        receive_buffer = self.check_radio()
        if receive_buffer:

            s=datetime.strftime(datetime.now(),"%H:%m:%S.%f")[:-3] + "  | "
            for b in receive_buffer:
                s +=f" {b:02x}"
            print (s)
