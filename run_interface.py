# -*- coding: utf-8 -*-
import sys
import os
import analib
import time
import logging
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from analysis import logger, analysis_utils
from analysis import controlServer
from graphics_Utils import  mainWindow
rootdir = os.path.dirname(os.path.abspath(__file__))

def test(NodeIds = None, interface = None,  SDO_RX = 0x600,index = 0x2200, Bytes =None):
    # Define parameters
    if NodeIds is None: 
        NodeIds = server.get_nodeIds()
    if interface is None:
        interface =server.get_interface()
    if Bytes is None: 
        Byte0= cmd = 0x40 #Defines a read (reads data only from the node) dictionary object in CANOPN standard
        Byte1, Byte2 = index.to_bytes(2, 'little')
        Byte3 = subindex = 1 
        Byets  = [Byte0,Byte1,Byte2,Byte3,0,0,0,0]
    server.start_channelConnection(interface = interface)
    # write CAN message [read dictionary request from master to node]
    server.writeCanMessage(SDO_RX + NodeIds[0], Byets, flag=0, timeout=1000)
     
    #Response from the node to master
    cobid, data, dlc, flag, t = server.readCanMessages()
    print(f'ID: {cobid:03X}; Data: {data.hex()}, DLC: {dlc}')
     
    #write sdo message
    print('Writing example CAN Expedited read message ...')
    #Example (1): get node Id
    VendorId = server.sdoRead(NodeIds[0], 0x1000,0,1000)
    print(VendorId, f'VendorId: {VendorId:03X}')
    
    #Example (2): print Pspp parameters ( 4 PSPPs)
    N_PSPP =1
    for PSPP in range(0,N_PSPP): # Each i represents one PSPP
        Pindex = index+PSPP
        monVals = server.sdoRead(NodeIds[0], Pindex, subindex,3000)
        vals = [(monVals >> i * 10) & (2**10 - 1) for i in range(3)]
        print(f'PSPP: {PSPP} ,Temp1: {vals[0]} ,Temp2: {vals[1]} ,Voltage: {vals[2]}')
    # print('Restarting device ...')
    # analib.wrapper.restart(ch.ipAddress)

if __name__=='__main__':
    server = controlServer.ControlServer(GUI=None)
    test()
