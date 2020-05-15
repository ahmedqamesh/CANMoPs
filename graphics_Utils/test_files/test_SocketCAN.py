#pip install python-can
from __future__ import print_function
import time
import can
bustype = ['socketcan',"pcan","ixxat","vector"]
channel = 'vcan0'

can.rc['interface'] = 'socketcan'
can.rc['channel'] = 'ch0'
can.rc['bitrate'] = 125000
from can.interface import Bus
bus = Bus()


def producer(id, N = None):
    """:param id: Spam the bus with messages including the data id."""
    bus = can.interface.Bus(bustype=bustype[0], channel=channel, bitrate=125000)
    for i in range(N):
        msg = can.Message(arbitration_id=0xc0ffee, data=[id, i, 34, 1, 0, 0, 0, 0], is_extended_id=False)
        try:
            bus.send(msg)
            print("Message sent on {}".format(bus.channel_info))
        except can.CanError:
            print("Message NOT sent")
        
        message = bus.recv(1.0)
        listener(message)
        if message is None:
            print('Timeout occurred, no message.')
        else:
            print(message)   
    time.sleep(1)


if __name__ == '__main__':
    pass    
    #producer(1, N = 5)


    