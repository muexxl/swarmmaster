#! /usr/bin/env python

HEADER = b'\xb5\x62'

outfile="assistancedata.hex"

def get_msg(marker, len):

    msg = HEADER
    msg += marker * 2
    msg += len.to_bytes(2, 'little')
    msg += marker * len
    msg += marker * 2
    return msg

content = {
    '\x03': 3,
    '\x04':4,
    }

repetitions=0x10
data=b''

for i in range(repetitions):
    b=i.to_bytes(1,'little')
    msg= get_msg(b,0x50)
    data += msg

with open(outfile,'wb')as f:
    f.write(data)

