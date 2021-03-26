# -*- coding: utf-8 -*-
from .swarmclient import *
import threading

import logging
logger = logging.getLogger(__name__)

class SwarmManager:  
    min_prio = 0
    max_prio = 10
    max_fails = 5


    def __init__(self):
        self.clients = dict()
        self.current_client= None
        self.clients_lock = threading.Lock()
        
    def add_client(self,id):
        returnvalue = False
        if not self.is_client(id):
            self.clients_lock.acquire()
            self.clients[id] = SwarmClient(id)
            self.clients_lock.release()
            logger.info(f'Swarmmanager\t| Added Client {id:04x},  Total Clients: {len(self.clients)}')
            returnvalue =True
        else:
            logger.warning(f'Swarmmanager\t| {id:04x} FAILED,  Total Clients: {len(self.clients)}')
            returnvalue =False
        
        return returnvalue

    def is_client(self,id):
        try:
            self.clients[id]
            return True
        except KeyError:
            return False
    
    def remove_client(self,id):
        self.clients_lock.acquire()
        returnvalue = False
        try:
            self.clients.pop(id)
            logger.info(f'Swarmmanager\t| Client # {id:04x} successfully removed')
            returnvalue =  True
        except KeyError as e:
            logger.warning(f'Swarmmanager\t| Failed to remove Client # {id:04x}. Client not registered')
            returnvalue =  False
        self.clients_lock.release()
        return returnvalue


    def remove_all_clients(self):
       self.current_client = None
       client_list =  list(self.clients.keys())
       for id in client_list:
           self.remove_client(id)
        



    def next_client(self):

        try:
            self.current_client = sorted(self.clients.values(),key = lambda x:x.prio, reverse=False)[0]
            self.current_client.prio +=1
            logging.debug(f'Swarmmanager\t| Next Client #{self.current_client.id:04x} at priority {self.current_client.prio}')
            self.check_client_priorities()
            return self.current_client
        except IndexError:
            self.current_client = None
            return None

    def get_client(self,id):
        try:
            return self.clients[id]
        except KeyError:
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
        logger.warning(f'Swarmmanager\t| reported fail {client.fail_counter} for client #{client.id:04x}')
        if client.fail_counter > self.max_fails:
            self.remove_client(client.id)
        self.next_client()