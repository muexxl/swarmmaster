# python -m radiolink.tests.test_mx_ping
# python -m radiolink.tests_integration.test_mx_ping
from  ..radiolink import *
import time

#open_reading_and_writing_pipe(config.get_address_from_id(0x0002))
rl = Radiolink(25,0)

while 1:
    suc = rl.send_to_id(2,bytearray(0xff04112233.to_bytes(5,'big')))
    print(f'Sending was {suc}')
    print("Received:")
    rl.check_radio_and_print_result()
    time.sleep(0.5)
