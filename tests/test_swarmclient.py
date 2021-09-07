# -*- coding: utf-8 -*-

import swarmmaster

from nose.tools import * 
import unittest

sc = swarmmaster.SwarmClient(1)

class TestSwarmClient(unittest.TestCase):
    """Basic test cases."""

    def test_sc_id (self):
        assert sc.id == 1

    def test_sc_writebuffer (self):
        sc.tx_buffer.clear()
        sc.tx_buffer += b'Hello'
        assert sc.tx_buffer[:5] == bytearray(b'Hello')
        sc.tx_buffer.clear()
        assert sc.tx_buffer == bytearray(b'')

    def test_sc_readbuffer (self):
        sc.rx_buffer.clear()
        sc.rx_buffer += b'Hallo'
        assert sc.rx_buffer[:5] == bytearray(b'Hallo')
        sc.rx_buffer.clear()
        assert sc.rx_buffer == bytearray(b'')

    def test_sc_failcounter (self):
        assert sc.fail_counter == 0
        sc.fail_counter +=1
        assert sc.fail_counter == 1
    def test_sc_xx (self):
        sc.prio = 100
        assert sc.prio == 100
        sc.prio += 1
        assert sc.prio == 101

    def test_sc_add_data (self):
        sc.rx_buffer =bytearray(b'Hello')
        msg =bytearray(b'')
        msg.append(1)
        msg+=b'World'
        sc.add_data_to_rx_buffer(msg)
        assert sc.last_msg_id ==1
        assert sc.rx_buffer ==bytearray(b'HelloWorld')
        msg.clear()
        msg.append(2)
        msg +=b'!'
        sc.add_data_to_rx_buffer(msg)
        assert sc.last_msg_id ==2
        assert sc.rx_buffer== bytearray(b'HelloWorld!')
        msg.clear()
        msg.append(10)
        msg +=b'new start'
        sc.add_data_to_rx_buffer(msg)
        assert sc.last_msg_id == 10
        assert sc.rx_buffer == bytearray(b'new start')
    
    def test_sc_buffer_overflow(self):
        
        
        sc.max_rx_buf = 5
        sc.max_tx_buf = 6
        sc.tx_buffer.clear()
        sc.rx_buffer.clear()
        sc.add_data_to_rx_buffer(b'0123456789')
        assert sc.rx_buffer == bytearray(b'56789')

        sc.add_data_to_tx_buffer(b'0123456789')
        assert sc.tx_buffer == bytearray(b'456789')
        sc.max_rx_buf = 2**20 #2**20 means  1MB
        sc.max_tx_buf = 2**20
    
    def test_get_packet(self):
        sc.tx_buffer.clear()
        d1=b'0123456789abcdef0123456789abcde'
        d2=b'fedcba9876543210fedcba9876543'
        sc.add_data_to_tx_buffer(d1)
        sc.add_data_to_tx_buffer(d2)
        assert sc.get_tx_buffer_size() == 60
        p1 = sc.get_packet()
        assert len(p1) == 32
        assert p1[1:11] == b'0123456789'
        p2 = sc.get_packet()
        assert p2[1:32] == b'fedcba9876543210fedcba9876543\xf0\xf0'
        p3 = sc.get_packet()
        assert p3[0:1]==b'\xc2'
        p2_restore = int.from_bytes(p3,'little') ^ int.from_bytes(p1,'little')
        p2_restore = bytearray(p2_restore.to_bytes(32,'little'))
        p2_restore[0]=0xb1
        assert p2_restore == p2
        
        p4 = sc.get_packet()
        p4_expected =bytearray(32)
        p4_expected[0]=0xc0
        assert p4 == p4_expected

        pass

if __name__ == '__main__':
    unittest.main()