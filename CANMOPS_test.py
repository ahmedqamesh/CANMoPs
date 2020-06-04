# -*- coding: utf-8 -*-
import sys
import os
import analib
import time
import logging
import numpy as np
from analysis import controlServer
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
    VendorId = server.sdoRead(NodeIds[0], 0x1000,0,3000)
    print(f'VendorId: {VendorId:03X}')
#         
    #Example (2): Read channels 
    n_channels = np.arange(3,35)
    c_subindices  = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F",
                   "10","11","12","13","14","15","16","17","18","19","1A","1B","1C","1D","1E",
                   "20","21","22","23","24","25","26","27","28","29","2A","2B","2C","2D","2E","2F","30","31"]
    values = []
    for c_subindex in c_subindices: # Each i represents one channel
        c_index = 0x2200
        value = server.sdoRead(NodeIds[0], c_index,int(c_subindex,16),3000)
        values = np.append(values, value)
    n_channels = n_channels.tolist()
    for channel in n_channels:
        if values[n_channels.index(channel)] is not None:
            print("Channel %i = %0.3f "%(channel,values[n_channels.index(channel)]))
        else:
            print("Channel %i = %s "%(channel,"None"))
    server.stop()        


if __name__=='__main__':
    #server = controlServer.ControlServer(interface = "AnaGate", set_channel =True)
    server = controlServer.ControlServer(interface = "socketcan", set_channel =True)
    #server = controlServer.ControlServer(interface = "Kvaser", set_channel =True)
    server.read_adc_channels()
    test()