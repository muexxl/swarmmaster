import logging
import threading
import time
logger = logging.getLogger(__name__)

#from pymavlink.dialects.v20 import ardupilotmega as mavlink2

class TerminalOutput(threading.Thread):
    def __init__(self, swarmmanager):
        self.swarmmanager = swarmmanager
        self.sleep_time = 1
        self.stats_lock = threading.Lock()
        self.stats_bytes_broadcasted= 0

        threading.Thread.__init__(self)

    def __del__(self):
        pass

    def run(self):
        self.keep_running = True
        logger.info('Running TerminalOutput Thread')
        while self.keep_running:
            print("\033c", end="")
            self.print_time()
            self.print_stats()
            time.sleep(self.sleep_time)
        
        logger.info('TerminalOutput Thread run function ended')

    def print_stats(self):
        total_rx = 0
        total_tx = 0
        print ('-'*80)
        print ('\tClient#\tTX\tRX - Bytes \t RX-Packets')
        print ('\t       \tbrutto\tbrutto\tnetto\ttotal\tlost\trestored')
        print ('\t       \t[Bps]\t[Bps]\t[Bps]\t[#]\t[#]\t[#]')
        self.swarmmanager.clients_lock.acquire()
        for c in self.swarmmanager.clients.values():
            bytes_sent, received_bytes_brutto,received_bytes_netto, received_packets,restored_packets ,lost_packets = c.get_stats()
            print (f'\t{c.id:04x} \t{bytes_sent/self.sleep_time} \t{received_bytes_brutto/self.sleep_time}\t{received_bytes_netto/self.sleep_time} \t{received_packets} \t {lost_packets}\t {restored_packets} \t ')
            total_rx += received_bytes_brutto
            total_tx += bytes_sent
        print ('-'*80)
  
        self.swarmmanager.clients_lock.release()
        print (f'Total \t{len(self.swarmmanager.clients):02d} \t{total_tx/self.sleep_time} \t{total_rx/self.sleep_time}')

        #Broadcasting stats
        bc = self.swarmmanager.broadcast_client
        bytes_sent, received_bytes_brutto,received_bytes_netto, received_packets,restored_packets ,lost_packets = bc.get_stats()
        print (f'\nBroadcast  \t{bytes_sent/self.sleep_time}  ') 
        
    

    def print_time(self):
        print(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()))

    def stop(self):
        logger.info('Stopping TerminalOutput Thread')
        self.keep_running = False
        self.join()