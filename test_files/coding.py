import numpy as np
import sys
import struct
import signal
original = bytearray(b'\x00P\x80\xfe\x01(\x02\x00')
ioriginal = int.from_bytes(original, byteorder=sys.byteorder)
b1, b2, b3, b4, b5, b6, b7, b8 = ioriginal.to_bytes(8, 'little')
print(hex(b1)[2:], hex(b2)[2:], hex(b3)[2:], hex(b4)[2:], hex(b5)[2:], hex(b6)[2:], hex(b7)[2:], hex(b8)[2:])
print([f'{b1:02x} {b2:02x} {b3:02x} {b4:02x} {b5:02x} {b6:02x} {b7:02x} {b8:02x}'])
print(["#ededed", "#f7e5b2","#fcc48d","#e64e4b","#984071","#58307b","#432776","#3b265e","#4f2e6b","#943ca6","#df529e","#f49cae","#f7d2bb","#f4ce9f",
       "#ecaf83","#dd8a5b","#904a5d","#5d375a","#402b55","#332d58","#3b337a","#365a9b","#2c4172","#2f3f60","#3f5d92","#4e7a80","#60b37e","#b3daa3",
       "#cfe8b7","#d2d2ba","#bab59e","#8b7c99","#6a5c9d"",#4c428d","#3a3487","#31222c"])

import threading 
import time 
  
def run(): 
    while True: 
        print('thread running') 
        global stop_threads 
        if stop_threads: 
            break
  
stop_threads = False
t1 = threading.Thread(target = run) 
t1.start() 
time.sleep(1) 
stop_threads = True
t1.join() 
print('thread killed') 