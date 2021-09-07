# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import swarmmaster

from nose.tools import * 

import unittest

mh = swarmmaster.MessageHandler()
class TestMessageHandler(unittest.TestCase):
    """Basic test cases."""

    def test_mh_rl (self):
        assert mh.radiolink.config.CEPin == 25
        assert mh.radiolink.config.CSNPin == 0
    
    def test_mh_handle_message(self):
        test_msg= bytearray(0xffb11223.to_bytes(4,'big'))
        assert_raises(swarmmaster.UnknownMessageException, mh.handle_msg, test_msg)

    # def test_reg_rem_client(self):
    #     reg_msg = bytearray(0xff01e30104e7.to_bytes(6,'big'))
    #     deauth_msg = bytearray(0xff02e30104e7.to_bytes(6,'big'))
    #     mh.register_client(reg_msg)
    #     assert_true (mh.swarmmanager.is_client(0x0401))
    #     mh.register_client(reg_msg)
    #     assert_true (mh.swarmmanager.is_client(0x0401))
    #     mh.handle_msg(deauth_msg)
    #     assert_false (mh.swarmmanager.is_client(0x0401))
        
if __name__ == '__main__':
    unittest.main()