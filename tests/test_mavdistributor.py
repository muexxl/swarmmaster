# -*- coding: utf-8 -*-

from .context import swarmmaster
from nose.tools import *
import time
import unittest


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_mavdistributor(self):
        us = swarmmaster.UDPServer()
        md = swarmmaster.Mavdistributor(us)
        assert_false(md.keep_running)
        md.start()
        time.sleep(0.3)
        assert_true(md.keep_running)
        md.stop()
        assert_false(md.keep_running)

if __name__ == '__main__':
    unittest.main()
