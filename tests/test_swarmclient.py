# -*- coding: utf-8 -*-

from .context import swarmmaster

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

if __name__ == '__main__':
    unittest.main()