import logging
import threading
import time
logger = logging.getLogger(__name__)

#from pymavlink.dialects.v20 import ardupilotmega as mavlink2

class TerminalOutput(threading.Thread):
    def __init__(self, swarmmanager):
        self.swarmmanager = swarmmanager
        self.sleep_time = 1

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
        print ('-'*50)
        print ('\tClient#\tRX      \tTX')
        self.swarmmanager.clients_lock.acquire()
        try:
            for c in self.swarmmanager.clients.values():
                rx, tx = c.get_stats()
                print (f'\t{c.id:04x} \t{rx/self.sleep_time} Bps \t{tx/self.sleep_time} Bps')
                total_rx += rx
                total_tx += tx
            print ('-'*50)

        except RuntimeError:
            pass #TODO Work with locks instead of risking unexpected change of dict!!

        
        self.swarmmanager.clients_lock.release()
        print (f'Total \t{len(self.swarmmanager.clients):02d} \t{total_rx/self.sleep_time} Bps \t{total_tx/self.sleep_time} Bps')

    def print_time(self):
        print(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()))

    def stop(self):
        logger.info('Stopping TerminalOutput Thread')
        self.keep_running = False
        self.join()