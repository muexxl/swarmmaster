# -*- coding: utf-8 -*-
from .swarmclient import *


import logging
logger = logging.getLogger(__name__)

class SwarmManager:  
    min_prio = 0
    max_prio = 10
    max_fails = 3
    def __init__(self):
        self.clients = dict()
        self.current_client= SwarmClient(0)
        
    def add_client(self,id):
        if not self.is_client(id):
            self.clients[id] = SwarmClient(id)
            logger.info(f'Added Client {id:04x},  Total Clients: {len(self.clients)}')
            return True
        else:
            logger.warning(f'Adding Client {id:04x} FAILED,  Total Clients: {len(self.clients)}')
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
            logger.info(f'Client # {id:04x} successfully removed')
            return True
        except KeyError as e:
            logger.warning(f'Failed to remove Client # {id:04x}. Client not registered')
            return False
        
    def next_client(self):
        try:
            self.current_client = sorted(self.clients.values(),key = lambda x:x.prio, reverse=False)[0]
            self.current_client.prio +=1
            logging.debug(f'Next is Client #{self.current_client.id:04x} with prio {self.current_client.prio}')
            self.check_client_priorities()
            return self.current_client
        except IndexError:
            self.current_client = None
            return None

    def get_client(self,id):
        try:
            self.current_client = self.clients[id] 
            self.current_client.prio +=1
            self.check_client_priorities()
            return self.current_client
        except KeyError:
            self.current_client = None
            return None

    def check_client_priorities(self):
        sorted_clients = sorted(self.clients.values(),key = lambda x:x.prio, reverse=False)
        if (sorted_clients[-1].prio > self.max_prio):
            self.reset_client_priorities()
        elif (sorted_clients[0].prio < self.min_prio):
            self.reset_client_priorities()

    def reset_client_priorities(self):
        for c in self.clients.values():
            c.prio = 0

    def report_fail(self):
        client =  self.current_client
        client.fail_counter +=1
        logger.warning(f'reported fail {client.fail_counter} for client {client.id}')
        if client.fail_counter > self.max_fails:
            self.remove_client(client.id)
        self.next_client()