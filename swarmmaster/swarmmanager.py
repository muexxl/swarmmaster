# -*- coding: utf-8 -*-
from .swarmclient import *

class SwarmManager:  
    min_prio = 0
    max_prio = 100
    def __init__(self):
        self.clients = dict()
        self.current_client= SwarmClient(0)
        
    def add_client(self,id):
        if not self.is_client(id):
            self.clients[id] = SwarmClient(id)
            return True
        else:
            return False

    def is_client(self,id):
        try:
            self.clients[id]
            return True
        except KeyError:
            return False
    
    def remove_client(self,id):
        try:
            self.clients.pop(id)
            return True
        except KeyError as e:
            return False
        
    def next_client(self):
        try:
            self.current_client = sorted(self.clients.values(),key = lambda x:x.prio, reverse=False)[0]
            return self.current_client
        except IndexError:
            return None
    
    def check_client_priorities(self):
        sorted_clients = sorted(self.clients.values(),key = lambda x:x.prio, reverse=False)
        if (sorted_clients[-1].prio > self.max_prio):
            self.reset_client_priorities()
        elif (sorted_clients[0] < self.min_prio):
            self.reset_client_priorities()

    def reset_client_priorities(self):
        for c in self.clients.values():
            c.prio = 0