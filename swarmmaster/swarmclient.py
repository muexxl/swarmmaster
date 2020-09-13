
class SwarmClient:
    def __init__(self, id=0):
        self.id = id
        self.rx_buffer = bytearray()
        self.tx_buffer = bytearray()
        self.last_msg_id= 0xa0
        self.fail_counter = 0
        self.prio = 0 # Prio is 0 as base. Prio 0 means highest.  increase +1 for everytime the client is talked to. regular reductions ? maybe. 
