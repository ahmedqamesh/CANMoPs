#pip install python-can
from __future__ import print_function
import time
import can
bustype = ['socketcan',"pcan","ixxat","vector"]
channel = 'can0'
from analysis import controlServer
can.rc['interface'] = 'socketcan'
can.rc['channel'] = 'can0'
can.rc['bitrate'] = 125000
from can.interface import Bus
#bus = Bus()
def test():
    # Define parameters
    NodeIds = server.get_nodeIds()
    interface =server.get_interface()
    SDO_RX = 0x600
    index = 0x1000
    Byte0= cmd = 0x40 #Defines a read (reads data only from the node) dictionary object in CANOPN standard
    Byte1, Byte2 = index.to_bytes(2, 'little')
    Byte3 = subindex = 0 
    #write CAN message [read dictionary request from master to node]
    server.writeCanMessage(SDO_RX + NodeIds[0], [Byte0,Byte1,Byte2,Byte3,0,0,0,0], flag=0, timeout=30)
    
    #Response from the node to master
    cobid, data, dlc, flag, t = server.readCanMessages()
    print(f'ID: {cobid:03X}; Data: {data.hex()}, DLC: {dlc}')
    
def producer(id, N = None):
    """:param id: Spam the bus with messages including the data id."""
    bus = can.interface.Bus(bustype=bustype[0], channel=channel, bitrate=125000)
    for i in range(N):
        msg = can.Message(arbitration_id= 0x601, data=[id, i, 16, 1, 0, 0, 0, 0], is_extended_id= False) 
        print(msg)
        #for msg in bus:
        #    print("{X}: {}".format(msg.arbitration_id, msg.data))
    
        #notifier = can.Notifier(bus, [can.Logger("recorded.log"), can.Printer()])
        try:
            bus.send(msg)
            print("Message sent on {}".format(bus.channel_info))
        except can.CanError:
            print("Message NOT sent")
        
        message = bus.recv(1.0)
        #listener(message)
        if message is None:
            print('Timeout occurred, no message.')
        else:
            cobid, data, dlc, flag, t = message.arbitration_id, message.data, message.dlc, message.is_extended_id, message.timestamp
            print(f'ID: {cobid:03X}; Data: {data.hex()}, DLC: {dlc}')
    time.sleep(1)


if __name__ == '__main__':   
    #producer(64, N = 2)
    server = controlServer.ControlServer(interface = "socketcan", set_channel =True)
    test()

    