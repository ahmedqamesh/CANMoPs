import numpy as np
import sys
import struct
original = bytearray(b'\x00P\x80\xfe\x01(\x02\x00')
ioriginal = int.from_bytes(original, byteorder=sys.byteorder)
b1,b2,b3,b4,b5,b6,b7, b8 = ioriginal.to_bytes(8, 'little')
print(hex(b1)[2:],hex(b2)[2:],hex(b3)[2:],hex(b4)[2:],hex(b5)[2:],hex(b6)[2:],hex(b7)[2:], hex(b8)[2:])
print([f'{b1:02x} {b2:02x} {b3:02x} {b4:02x} {b5:02x} {b6:02x} {b7:02x} {b8:02x}'])
