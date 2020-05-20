# -*- coding: utf-8 -*-
import sys
import os
import analib
import time
import logging
import numpy as np
from analysis import controlServer
rootdir = os.path.dirname(os.path.abspath(__file__))
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
#     #write sdo message
    print('Writing example CAN Expedited read message ...')
#       
    #Example (1): get node Id
    #VendorId = server.sdoRead(NodeIds[0], 0x1000,0,3000)
    #print(f'VendorId: {VendorId:03X}')
#         
#     #Example (2): Read channels 
#     n_channels = np.arange(3,35)
#     values = []
#     for channel in n_channels: # Each i represents one channel
#         c_index = 0x2400
#         c_subindex = channel-2
#         value = server.sdoRead(NodeIds[0], c_index,c_subindex,3000)
#         values = np.append(values, value)
#     n_channels = n_channels.tolist()
#     for channel in n_channels:
#         print("Channel %i = %0.3f "%(channel,values[n_channels.index(channel)]))
    server.stop()        


if __name__=='__main__':
    server = controlServer.ControlServer(interface = "AnaGate", set_channel =True)
    test()