# -*- coding: utf-8 -*-

import swarmmaster

import time
import unittest

from nose.tools import * 


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_databuffer(self):
        pb = swarmmaster.PacketBuffer()
        msg =bytearray(32)
        for i in range(1,32):
            msg[i]=i

        for i in range(3):
            msg[0]=swarmmaster.coco.DATA | i
            pb.add_message(msg)
            assert len(pb.packet_buffer)==i+1

        msg[0]=swarmmaster.coco.CHKSUM | 3
        pb.add_message(msg)

        pb.process_packet_buffer()
        
        expected = bytes(msg[1:])*3
        assert pb.stream_buffer == expected

    def test_databuffer_restore(self):
        pb = swarmmaster.PacketBuffer()
        msg =bytearray(32)
        checksum=0
        counter=0

        for i in range(1,32):
            msg[i]=i

        for i in range(3):
            msg[0]=swarmmaster.coco.DATA | i
                
            for j in range(1,32):
                msg[j]=counter%255
                counter+=1
            checksum^=int.from_bytes(msg,'little')

            if i==1:
                continue #skip 2nd message

            pb.add_message(msg)
            
        assert len(pb.packet_buffer)==2

        msg=checksum.to_bytes(32,'little')
        msg=bytearray(msg)
        msg[0]=swarmmaster.coco.CHKSUM | 3

        pb.add_message(msg)
        pb.process_packet_buffer()

        expected = b''
        for i in range(3*31):
            expected+=i.to_bytes(1,'little')
            
        assert pb.stream_buffer == expected
        

        
if __name__ == '__main__':
    unittest.main()
