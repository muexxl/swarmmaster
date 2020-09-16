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

sm = swarmmaster.SwarmManager()
class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""
    
    def test_sm_add_client_remove_exists (self):
        assert_false(sm.is_client(4))
        assert_true(sm.add_client(4))
        assert_false(sm.add_client(4))
        assert_true(sm.is_client(4))
        assert_true(sm.remove_client(4))
        assert_false(sm.remove_client(4))
        assert_false(sm.is_client(4))


    def test_sm_current_client (self):
        sm.add_client(5)
        sm.current_client = sm.clients[5]
        assert sm.current_client == sm.clients[5]
        assert_true(sm.add_client(63))
        
    def test_next_client(self):
        sm.add_client(44)
        client = sm.next_client()
        assert client == sm.clients[client.id]
        client.prio = 20
        sm.add_client(20)
        for c in sm.clients.values():
            c.prio =99
        sm.add_client(31)
        client = sm.next_client()
        assert client.id == 31
        client.prio = 101
        sm.check_client_priorities()
        client = sm.next_client()
        assert client.prio == 1
    def test_auto_resetting_prio(self):
        sm.clients.clear()
        sm.add_client(1)
        client = sm.next_client()
        assert client.id == 1
        sm.add_client(2)
        client = sm.next_client()
        assert client.id == 2
        

    def test_curr_client(self):
        assert_true(sm.add_client(2445))
        assert_false(sm.add_client(2445))
        client = sm.next_client()
        assert client == sm.current_client
        client.tx_buffer+=b'Hallo'
        client.prio +=1
        sm.add_client(2134)
        client == sm.next_client()
        assert sm.clients[2445].tx_buffer == bytearray(b'Hallo')
        



if __name__ == '__main__':
    unittest.main()