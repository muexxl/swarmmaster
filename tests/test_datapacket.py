# -*- coding: utf-8 -*-

import swarmmaster

import time
import unittest

from nose.tools import * 


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_datapacket(self):
        msg_id=b'\x48'
        msg_data=b'0123456789'
        msg= msg_id+msg_data
        
        dp= swarmmaster.DataPacket(msg)
    
        assert_equal(msg_data, dp.data)
        assert_equal(dp.type_id, 0x48)
        assert_equal(dp.type, 0x40)
        assert_equal(dp.id, 8)
        assert dp.len ==10


        
if __name__ == '__main__':
    unittest.main()
