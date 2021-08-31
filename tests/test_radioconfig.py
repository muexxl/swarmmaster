# -*- coding: utf-8 -*-

from .context import swarmmaster

import unittest

rl = swarmmaster.Radiolink()
config = rl.config


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""
    def test_get_address(self):
        config.CEPin = 22
        config.CSNPin = 0
        assert config.channel == 0x64
        assert config.CEPin == 22
        assert config.get_address_from_id(0xeeff) == b'\x2d\xff\xee'
        assert config.get_id_from_address(b'\x2d\xff\xee') == 0xeeff

    def test_broadcast_address(self):
        assert config.broadcastAddress == b'\x1d\x1d\x1d'
        assert config.get_broadcast_address() == b'\x1d\x1d\x1d'

    def test_master_address(self):
        assert config.get_master_address() == b'\x1e\x1d\x1d'


if __name__ == '__main__':
    unittest.main()