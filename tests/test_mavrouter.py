# -*- coding: utf-8 -*-

from .context import swarmmaster
from nose.tools import *
from pymavlink.dialects.v20 import ardupilotmega as mavlink2

import unittest

# 'assert_almost_equal'
# 'assert_almost_equals'
# 'assert_count_equal'
# 'assert_dict_contains_subset'
# 'assert_dict_equal'
# 'assert_equal'
# 'assert_equals'
# 'assert_false'
# 'assert_greater'
# 'assert_greater_equal'
# 'assert_in'
# 'assert_is'
# 'assert_is_instance'
# 'assert_is_none'
# 'assert_is_not'
# 'assert_is_not_none'
# 'assert_less'
# 'assert_less_equal'
# 'assert_list_equal'
# 'assert_logs'
# 'assert_multi_line_equal'
# 'assert_not_almost_equal'
# 'assert_not_almost_equals'
# 'assert_not_equal'
# 'assert_not_equals'
# 'assert_not_in'
# 'assert_not_is_instance'
# 'assert_not_regex'
# 'assert_not_regexp_matches'
# 'assert_raises'
# 'assert_raises_regex'
# 'assert_raises_regexp'
# 'assert_regex'
# 'assert_regexp_matches'
# 'assert_sequence_equal'
# 'assert_set_equal'
# 'assert_true'
# 'assert_tuple_equal'
# 'assert_warns'
# 'assert_warns_regex'
# 'eq_'
# 'istest'
# 'make_decorator'
# 'nontrivial'
# 'nontrivial_all'
# 'nottest'
# 'ok_'
# 'raises'
# 'set_trace'
# 'timed'
# 'trivial'
# 'trivial_all'
# 'with_setup']

client = swarmmaster.SwarmClient()
mav= mavlink2.MAVLink(open('mav.file', 'wb'))
class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""
    
    def test_mav_packer_change_client_id(self):
        
        mr = swarmmaster.Mavrouter()
        client.id = 4
        
        #Check initialization to FALSE
        assert client.mav_id_correct == False
        
        #check if value stays false in case of incorrect SYSID PARAM MESSAGE
        param_id = b'SYSID_THISMAV'
        param_value = 5.0 #wrong value!
        param_type = 4 #int116
        param_count = 1001
        param_index = 1
        valuemsg = mav.param_value_encode(param_id, param_value, param_type, param_count, param_index)
        
        client.rx_buffer = bytearray(valuemsg.pack(mav))
        mr.check_client(client)
        assert_false(client.mav_id_correct)
        
        #check if value successfully changes to TRUE in case of correct SYS ID PARAM MESSAGE
        param_value = 4.0 # correct value 
        valuemsg = mav.param_value_encode(param_id, param_value, param_type, param_count, param_index)
        client.rx_buffer = bytearray(valuemsg.pack(mav))
        mr.check_client(client)
        assert_true(client.mav_id_correct)
        del mr
   
if __name__ == '__main__':
    unittest.main()
