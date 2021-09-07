# -*- coding: utf-8 -*-

import swarmmaster
import time
import unittest

from nose.tools import * 
sm = swarmmaster.SwarmManager()

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_mavdistributor(self):
        us = swarmmaster.UDPServer()
        md = swarmmaster.Mavdistributor(us, sm)
        assert_false(md.keep_running)
        md.start()
        time.sleep(0.3)
        assert_true(md.keep_running)
        md.stop()
        assert_false(md.keep_running)

if __name__ == '__main__':
    unittest.main()
