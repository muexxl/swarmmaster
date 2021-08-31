import sqlite3
import os
from .swarmclient import SwarmClient


class DroneDB(object):
    """docstring for DroneDB."""
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.init_db()

    def init_db(self):
        self.con = sqlite3.connect(self.dbfile)
        self.cur = self.con.cursor()
        try: 
            self.cur.execute("CREATE TABLE IF NOT EXISTS drones (client_id INTEGER PRIMARY KEY, uid0 INTEGER, uid1 INTEGER, uid2 INTEGER, devid INTEGER)")
        except sqlite3.OperationalError:
            pass
        self.cur.fetchall()

    def get_client_id(self, client):
        self.cur.execute(f"SELECT client_id FROM drones WHERE uid0={client.uid0} AND uid1={client.uid1} AND uid2={client.uid2}")
        result = self.cur.fetchall()

        if (result):
            client.id = result[0][0]
        else:
            new_id = self.find_first_free_client_id()
            client.id = new_id
            self._insert_client_into_db(client)
        
        return client.id

    def _insert_client_into_db(self, client):
        sql_cmd = f"INSERT INTO drones (client_id, uid0, uid1, uid2, devid) VALUES (?,?,?,?,?)"
        values = (client.id, client.uid0, client.uid1, client.uid2, client.devid)
        self.cur.execute(sql_cmd,values)
        self.con.commit()

    def find_first_free_client_id(self):
        self.cur.execute(f"SELECT client_id FROM drones")
        result=self.cur.fetchall()
        used_client_ids=[]
        for row in result:
            used_client_ids.append(row[0])

        is_found = False
        test_id=1
        while (not is_found):
            if (test_id in used_client_ids):
                test_id +=1
            else:
                is_found=True

        return test_id
    
    def remove_table(self):
        self.cur.execute("DROP TABLE IF EXISTS drones")

        

