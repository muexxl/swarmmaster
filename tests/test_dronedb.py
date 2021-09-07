# -*- coding: utf-8 -*-

import swarmmaster
from pymavlink.dialects.v20 import ardupilotmega as mavlink2
import time
import unittest

from nose.tools import * 
db=swarmmaster.DroneDB('test.db')
sc1 =swarmmaster.SwarmClient(0)
sc2 =swarmmaster.SwarmClient(0)

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_drone_db(self):
        sc1.uid0=10
        sc2.uid1=11
        
        id = db.get_client_id(sc1)
        assert id==1

        id = db.get_client_id(sc2)
        assert id==2

        #client 1 is already familiar and the id should come from the database
        id = db.get_client_id(sc1)
        assert id==1

        db.remove_table()

        
if __name__ == '__main__':
    unittest.main()
