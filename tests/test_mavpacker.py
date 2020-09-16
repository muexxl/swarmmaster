# -*- coding: utf-8 -*-

from .context import swarmmaster
from nose.tools import *

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

mp = swarmmaster.Mavpacker()
client = swarmmaster.SwarmClient()
class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""
    
    def test_mavpacker(self):
        
        packet = mp.check_client(client)
        assert packet == None

        data= bytearray(b'x0123456789abcdef0123456789abcdef')
        client.add_data_to_rx_buffer(data)
        packet = mp.check_client(client)
        assert packet[:16] == bytearray(b'0123456789abcdef')

if __name__ == '__main__':
    unittest.main()