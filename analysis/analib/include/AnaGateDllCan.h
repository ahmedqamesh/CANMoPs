// ----------------------------------------------------------------------------
// Projekt       : Analytica AnaGate API
// File          : AnaGateDllCAN.h
// Author        : Axel Schmidt
// Copyright     : (C) 2004 by Analytica GmbH
// ----------------------------------------------------------------------------
// $Id: AnaGateDllCan.h,v 1.17 2009/04/30 13:24:56 stefanwelisch Exp $
//
// $Log: AnaGateDllCan.h,v $
// Revision 1.17  2009/04/30 13:24:56  stefanwelisch
// Referenzen als Pointer implementiert
//
// Revision 1.16  2009/03/30 11:17:18  stefanwelisch
// Timestamp hinzugefügt
//
// Revision 1.15  2008/05/13 12:19:33  stefanwelisch
// DevicePort bei CANOpenDevice hinzugefügt
//
// Revision 1.14  2008/04/18 10:23:39  stefanwelisch
// neue Parameter bei CAN-Kommunikation (Termination, HighSpeed, ConsiderPrio)
//
// Revision 1.13  2008/01/14 17:00:53  axelschmidt
// zusätzlicher Parameter für CAN callback
//
// Revision 1.12  2007/11/21 09:19:22  axelschmidt
// real c interface for DLL
//
// Revision 1.11  2007/11/08 11:11:43  StefanWelisch
// Defaultwert bei SetGlobals() angegeben
//
// Revision 1.10  2007/11/07 12:09:14  StefanWelisch
// In Get/SetGlobals() die Terminierung mit aufgenommen
//
// Revision 1.9  2007/10/29 08:53:11  axelschmidt
// new define for VB6 support (special DLL)
//
// Revision 1.8  2007/05/21 11:43:39  axelschmidt
// standard timeout 500 -> 1000 ms
//
// Revision 1.7  2005/09/16 09:18:48  axelschmidt
// Digital IO support for I2C and CAN
//
// Revision 1.6  2005/08/15 14:54:49  axelschmidt
// TCP-Protocol changed for global settings
//
// Revision 1.5  2005/08/03 16:28:39  axelschmidt
// SetFiter/GetFilter implementation
//
// Revision 1.4  2005/07/08 12:04:07  AxelSchmidt
// Baurate is int32
//
// Revision 1.3  2005/06/09 16:11:43  axelschmidt
// new CANWrite + CANSetCallback
//
// Revision 1.2  2005/02/09 12:09:08  axelschmidt
// function to set baudrate
//
// Revision 1.1  2005/01/31 16:24:31  axelschmidt
// initial
//
// ----------------------------------------------------------------------------

#ifndef _ANAGATE_DLL_CAN_H
#define _ANAGATE_DLL_CAN_H

// Defines --------------------------------------------------------------------
#if WIN32
#  include <winsock2.h>
#  include <windows.h>
#endif
#include <AnaGateDLL.h>

// Prototyping ----------------------------------------------------------------
#ifdef __cplusplus
extern "C"
{
#endif // __cplusplus

   typedef void (WINAPI * CAN_PF_CALLBACK)    ( AnaUInt32 nID, const char *pcBuf, AnaInt32 nLen, AnaInt32 nFlags, AnaInt32 hHandle );
   typedef void (WINAPI * CAN_PF_CALLBACK_EX) ( AnaUInt32 nID, const char *pcBuf, AnaInt32 nLen, AnaInt32 nFlags, AnaInt32 hHandle, AnaInt32 nSeconds, AnaInt32 nMicroseconds );

   /// SWe 07.12.2009 Erweiterung für CANOpen
   typedef void (WINAPI * CAN_OPEN_PF_CALLBACK_PDO)       ( AnaUInt8 nNodeID, AnaUInt8 nPDOTyp, AnaUInt8 nDataLen, const char *pcData, AnaInt32 hHandle, AnaInt32 nSeconds, AnaInt32 nMicroseconds );
   typedef void (WINAPI * CAN_OPEN_PF_CALLBACK_SYNC)      ( AnaUInt8 nReturnCode, AnaInt32 hHandle, AnaInt32 nSeconds, AnaInt32 nMicroseconds );
   typedef void (WINAPI * CAN_OPEN_PF_CALLBACK_EMCY)      ( AnaUInt8 nNodeID, AnaUInt16 nErrorCode, AnaUInt8 nErrorRegister, const AnaUInt8 *pcErrorDescription, AnaInt32 hHandle, AnaInt32 nSeconds, AnaInt32 nMicroseconds );
   typedef void (WINAPI * CAN_OPEN_PF_CALLBACK_GUARD)     ( AnaUInt8 nNodeID, AnaUInt8 nStatus, AnaInt32 hHandle, AnaInt32 nSeconds, AnaInt32 nMicroseconds );
   typedef void (WINAPI * CAN_OPEN_PF_CALLBACK_UNDEFINED) ( AnaInt32 nCANID, AnaUInt8 nNodeID, AnaUInt8 nFunctionCode, AnaUInt8 nDataLen, const char *pcData, AnaInt32 hHandle, AnaInt32 nSeconds, AnaInt32 nMicroseconds );



   /** Opens an AnaGate CAN device.
      @param pHandle Pointer to an integer, in which the device handle is stored, if device is
                     opened successfully.
      @param bDataCnf     Telegrams are to be confirmed by client and AnaGate CAN.
      @param bMonitor     AnaGate CAN sents all CAN messages to client anyway.
      @param nDevicePort  Portnumber of the Angate (0 - 99).
      @param pcIPAddress  IP address of the AnaGate device.
      @param nTimeout     Standard tcp/ip timeout in millseconds.
      @return If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANOpenDevice( AnaInt32 *pHandle, AnaInt32 bDataCnf, AnaInt32 bMonitor, AnaInt32 nDevicePort,
                                                             const char * pcIPAddress, AnaInt32 nTimeout );


   /** Opens an AnaGate CAN device with setting of ethernet protocol layer4 (tcp/udp).
      @param pHandle Pointer to an integer, in which the device handle is stored, if device is
                     opened successfully.
      @param bDataCnf     Telegrams are to be confirmed by client and AnaGate CAN.
      @param bMonitor     AnaGate CAN sents all CAN messages to client anyway.
      @param nDevicePort  Portnumber of the Angate (0 - 99).
      @param pcIPAddress  IP address of the AnaGate device.
      @param nTimeout     Standard tcp/ip timeout in millseconds.
      @param nProtocol    Protocol (Layer4) of ip connection (TCP/UDP).
      @return If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANOpenDeviceEx( AnaInt32 *pHandle, AnaInt32 bDataCnf, AnaInt32 bMonitor, AnaInt32 nDevicePort,
                                                           const char * pcIPAddress, AnaInt32 nTimeout, AnaInt32 nProtocol );


   /** Closes an open AnaGate CAN device.
       @param hHandle Device handle (from a successfull #OpenDevice call).
       @return If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING  CANCloseDevice( AnaInt32 hHandle );


   /** Restarts an AnaGate CAN device.
   @param pcIPAddress  Tcp/ip address of the AnaGate device (Port is always 5001).
   @param nTimeout     Standard tcp/ip timeout in millseconds.
   @return If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
    */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANRestart( const char * pcIPAddress, AnaInt32 nTimeout );


   /** Gets the defined filter set of the current connection.
       @param hHandle Device handle (from a successfull #OpenDevice call).
       @param pnFilter Pointer to 8 software filter definitions. A single filter definiton contains
                        of two 32 bit values, so pnFilter should be a pointer array of 16 integer values.
       @return If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANGetFilter( AnaInt32 hHandle, AnaUInt32 * pnFilter );

   /** Sets the filter set of the current connection.
       @param hHandle Device handle (from a successfull #OpenDevice call).
       @param pnFilter Pointer to 8 software filter definitions. A single filter definiton contains
                        of two 32 bit values, so pnFilter should be a pointer array of 16 integer values.
       @return If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANSetFilter( AnaInt32 hHandle, const AnaUInt32 * pnFilter );

   /** Sets the global settings of an AnaGate CAN device.
       @param hHandle        Device handle (from a successfull #OpenDevice call).
       @param nBaudrate      Baud rate.
       @param nBaudrate      Operating mode.
       @param bTermination   Termination  on/off.
       @param bHighSpeed     HighSpeed    on/off.
       @param bTimestamp     Timestamp in DataIndication on/off.
       @return If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANSetGlobals( AnaInt32 hHandle, AnaUInt32 nBaudrate, AnaUInt8 nOperatingMode, AnaInt32 bTermination, AnaInt32 bHighSpeed, AnaInt32 bTimestampOn );

   /** Gets the global settings of an open AnaGate CAN device.
       @param hHandle        Device handle (from a successfull #OpenDevice call).
       @param nBaudrate      Baud rate.
       @param nBaudrate      Operating mode.
       @param bTermination   Termination  on/off.
       @param bHighSpeed     HighSpeed    on/off.
       @param bTimestamp     Timestamp in DataIndication on/off.
       @return If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANGetGlobals( AnaInt32 hHandle, AnaUInt32 * pnBaudrate, AnaUInt8 * pnOperatingMode, AnaInt32 * pbTermination, AnaInt32 * pbHighSpeed, AnaInt32 * pbTimestampOn);

   /** Sends telegramm to the CAN bus.
       @param hHandle Device handle (from a successfull #OpenDevice call).
       @param nIdentifier            Id of the sendet message.
       @param pcBuffer               Pointer to the buffer containing the CAN data.
       @param nBufferLen             Length of the data buffer.
       @param nFlags                 format flags (bit 0 = extended CAN id, bit 1 = remote telegram).
       @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANWrite ( AnaInt32 hHandle, AnaInt32 nIdentifier, const char *pcBuffer, AnaInt32 nBufferLen, AnaInt32 nFlags );

   /** Sends telegramm to the CAN bus.
       @param hHandle Device handle (from a successfull #OpenDevice call).
       @param nIdentifier            Id of the sendet message.
       @param pcBuffer               Pointer to the buffer containing the CAN data.
       @param nBufferLen             Length of the data buffer.
       @param nFlags                 format flags (bit 0 = extended CAN id, bit 1 = remote telegram).
       @param pnSeconds              Pointer to long in which the seconds of the timeval will be written.
       @param pnMicroseconds         Pointer to long in which the microseconds of the timeval will be written.
       @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANWriteEx ( AnaInt32 hHandle, AnaInt32 nIdentifier, const char *pcBuffer, AnaInt32 nBufferLen, AnaInt32 nFlags, AnaInt32 * pnSeconds, AnaInt32 * pnMicroseconds );


   /** Sets the callback function which is called every time an incoming CAN message arrives.
       @param hHandle Device handle (from a successfull #OpenDevice call).
       @param pFunction Pointer to the function which is to be called (NULL for reset).
       @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANSetCallback( AnaInt32 hHandle, CAN_PF_CALLBACK pFunction );

   /** Sets the callbackex function which is called every time an incoming CAN message arrives.
       @param hHandle Device handle (from a successfull #OpenDevice call).
       @param pFunction Pointer to the function which is to be called (NULL for reset).
       @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANSetCallbackEx( AnaInt32 hHandle, CAN_PF_CALLBACK_EX pFunction );

   /** Sets the maximum size of the receive telegram queues (see #CANGetMessage, ...).
       If the size is set to zero then the queueing mechanism is disabled and
       all stored telegrams are discarded.
       @param hHandle  Device handle (from a successfull #OpenDevice call).
       @param nMaxSize Maximum size of each queue.
       @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANSetMaxSizePerQueue( AnaInt32 hHandle, AnaUInt32 nMaxSize );

   /** Returns a CAN Data Indication telegram from the internal receive buffer, if available.
       Received telegrams are only stored if the mechanism has previously been
       enabled via #CANSetMaxSizePerQueue, and no callback handler has been
       installed via #CANSetCallback or #CANSetCallbackEx.
       The output parameter pnAvailMsgs is set to -1 if no telegram was available.
       In that case all other output parameters are invalid.
       @param hHandle        [in]  Device handle (from a successfull #OpenDevice call).
       @param pnAvailMsgs    [out] pointer to number of available messages after the current one has been removed.
       @param pnID           [out] pointer to message ID.
       @param pcData         [out] pointer to message buffer (must be able to hold 8 bytes).
       @param pnDataLen      [out] pointer to message length.
       @param pnFlags        [out] pointer to message flags.
       @param pnSeconds      [out] pointer to receive time seconds.
       @param pnMicroseconds [out] pointer to receive time microseconds.
       @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANGetMessage( AnaInt32   hHandle,   AnaUInt32 * pnAvailMsgs,
                                                             AnaInt32 * pnID,      char      * pcData,
                                                             AnaUInt8 * pnDataLen, AnaInt32  * pnFlags,
                                                             AnaInt32 * pnSeconds, AnaInt32  * pnMicroseconds);

   /** Returns a CANOpen PDO Indication telegram from the internal receive buffer, if available.
       Received telegrams are only stored if the mechanism has previously been
       enabled via #CANSetMaxSizePerQueue, and no PDO callback handler has been
       installed via #CANopenSetCallback.
       The output parameter pnAvailMsgs is set to -1 if no telegram was available.
       In that case all other output parameters are invalid.
       @param hHandle     [in]  Device handle (from a successfull #OpenDevice call).
       @param pnAvailMsgs [out] pointer to number of available messages after the current one has been removed.
       @param pnNodeID    [out] pointer to node ID.
       @param pnPDOType   [out] pointer to PDO type.
       @param pnDataLen   [out] pointer to data length.
       @param pcData      [out] pointer to data buffer (must be able to hold 8 bytes).
       @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenGetPDO( AnaInt32   hHandle,   AnaUInt32 * pnAvailMsgs,
                                                             AnaUInt8 * pnNodeID,  AnaUInt8  * pnPDOType,
                                                             AnaUInt8 * pnDataLen, char      * pcData );

   /** Returns a CANOpen SYNC Indication telegram from the internal receive buffer, if available.
       Received telegrams are only stored if the mechanism has previously been
       enabled via #CANSetMaxSizePerQueue, and no SYNC callback handler has
       been installed via #CANopenSetCallback.
       The output parameter pnAvailMsgs is set to -1 if no telegram was available.
       In that case all other output parameters are invalid.
       @param hHandle      [in]  Device handle (from a successfull #OpenDevice call).
       @param pnAvailMsgs  [out] pointer to number of available messages after the current one has been removed.
       @param pnReturnCode [out] pointer to return code.
       @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenGetSYNC( AnaInt32   hHandle,     AnaUInt32 * pnAvailMsgs,
                                                              AnaUInt8 * pnReturnCode );

   /** Returns a CANOpen EMCY Indication telegram from the internal receive buffer, if available.
       Received telegrams are only stored if the mechanism has previously been
       enabled via #CANSetMaxSizePerQueue, and no EMCY callback handler has
       been installed via #CANopenSetCallback.
       The output parameter pnAvailMsgs is set to -1 if no telegram was available.
       In that case all other output parameters are invalid.
       @param hHandle            [in]  Device handle (from a successfull #OpenDevice call).
       @param pnAvailMsgs        [out] pointer to number of available messages after the current one has been removed.
       @param pnNodeID           [out] pointer to node ID.
       @param pnErrorCode        [out] pointer to error code.
       @param pnErrorRegister    [out] pointer to error register.
       @param pcErrorDescription [out] pointer to error description (must be able to hold 5 bytes).
       @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenGetEMCY( AnaInt32   hHandle,         AnaUInt32 * pnAvailMsgs,
                                                              AnaUInt8 * pnNodeID,        AnaUInt16 * pnErrorCode,
                                                              AnaUInt8 * pnErrorRegister, AnaUInt8  * pcErrorDescription );

   /** Returns a CANOpen GUARD Indication telegram from the internal receive buffer, if available.
       Received telegrams are only stored if the mechanism has previously been
       enabled via #CANSetMaxSizePerQueue, and no GUARD callback handler has
       been installed via #CANopenSetCallback.
       The output parameter pnAvailMsgs is set to -1 if no telegram was available.
       In that case all other output parameters are invalid.
       @param hHandle     [in]  Device handle (from a successfull #OpenDevice call).
       @param pnAvailMsgs [out] pointer to number of available messages after the current one has been removed.
       @param pnNodeID    [out] pointer to node ID.
       @param pnStatus    [out] pointer to status.
       @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenGetGUARD( AnaInt32   hHandle,  AnaUInt32 * pnAvailMsgs,
                                                               AnaUInt8 * pnNodeID, AnaUInt8  * pnStatus );

   /** Returns a CANOpen Undefined Indication telegram from the internal receive buffer, if available.
       Received telegrams are only stored if the mechanism has previously been
       enabled via #CANSetMaxSizePerQueue, and no Undefined callback handler
       has been installed via #CANopenSetCallback.
       The output parameter pnAvailMsgs is set to -1 if no telegram was available.
       In that case all other output parameters are invalid.
       @param hHandle        [in]  Device handle (from a successfull #OpenDevice call).
       @param pnAvailMsgs    [out] pointer to number of available messages after the current one has been removed.
       @param pnCANID        [out] pointer to CAN ID.
       @param pnNodeID       [out] pointer to node ID.
       @param pnFunctionCode [out] pointer to function code.
       @param pnDataLen      [out] pointer to data length.
       @param pcData         [out] pointer to message buffer (must be able to hold 8 bytes).
       @param pnSeconds      [out] pointer to receive time seconds.
       @param pnMicroseconds [out] pointer to receive time microseconds.
       @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenGetUndefined( AnaInt32   hHandle,        AnaUInt32 * pnAvailMsgs,
                                                                   AnaInt32 * pnCANID,        AnaUInt8  * pnNodeID,
                                                                   AnaUInt8 * pnFunctionCode,
                                                                   AnaUInt8 * pnDataLen,      char      * pcData,
                                                                   AnaInt32 * pnSeconds,      AnaInt32  * pnMicroseconds );

   /** Retrieves a textual error description of the supplied return code.
      @param nRC Return code.
      @param pcMessage Pointer to a c-style character buffer, in which the retrieved error string is stored.
      @param nMessageLen Length of the supplied charcter buffer. If the error string does not fit into the
             buffer, the string is shortened.
      @return The byte of the returned error string.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANErrorMessage( AnaInt32 nRC, char *pcMessage, AnaInt32 nMessageLen );

   /** Reads data from digital io register of the partner.
      @param hHandle Device handle (from a successfull #OpenDevice call).
      @param nInputBits   Pointer to the variable that receives the digtial input register read.
      @param nOutputBits  Pointer to the variable that receives the digtial output register read.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANReadDigital( AnaInt32 hHandle, AnaUInt32 * pnInputBits, AnaUInt32 * pnOutputBits );

   /** Writes data to digital io register of the partner.
      @param hHandle Device handle (from a successfull #OpenDevice call).
      @param nOutputBits  Variable that hold the digtial IO output register bits to write.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANWriteDigital( AnaInt32 hHandle, AnaUInt32 nOutputBits );

   /** Reads data from analog inputs of the partner.
      @param hHandle        Device handle (from a successful #OpenDevice call).
      @param pnPowerSupply  [out]    Power supply voltage in millivolt.
      @param anAnalogInputs [out]    Analog input voltages in millivolt.
      @param pnInputCount   [in+out] Number of anAnalogInputs array elements and number of received input voltages.
      @return If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANReadAnalog( AnaInt32 hHandle, AnaUInt32 * pnPowerSupply, AnaUInt32 anAnalogInputs[], AnaUInt16 * pnInputCount );

   /** Writes data to analog outputs of the partner.
      @param hHandle         Device handle (from a successful #OpenDevice call).
      @param anAnalogOutputs [in] Analog output voltages in millivolt.
      @param nOutputCount    [in] Number of output voltages.
      @return If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANWriteAnalog( AnaInt32 hHandle, const AnaUInt32 anAnalogOutputs[], AnaUInt16 nOutputCount );

   /** Writes the time to the CAN partner.
      @param hHandle         Device handle (from a successfull #OpenDevice call).
      @param nSeconds        seconds elapsed since 01.01.1970 (attribut tv_sec of struct timeval).
      @param nMicroseconds   microseconds since the last full second (attribut tv_usec of struct timeval).
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANSetTime( AnaInt32 hHandle, AnaUInt32 nSeconds, AnaUInt32 nMicroseconds );


   /** Reads the time from the CAN partner.
      @param hHandle         Device handle (from a successfull #OpenDevice call).
      @param nSeconds        seconds elapsed since 01.01.1970 (attribut tv_sec of struct timeval).
      @param nMicroseconds   microseconds since the last full second (attribut tv_usec of struct timeval).
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANGetTime( AnaInt32 hHandle, AnaInt32 * pbTimeWasSet, AnaUInt32 * pnSeconds, AnaUInt32 * pnMicroseconds );


   /** Reads the power status from the CAN quattro PM partner.
      @param hHandle                   Device handle (from a successfull #OpenDevice call).
      @param nPowerSupplyCountExpected Number of expected power supplies.
      @param pnPowerSupplyCountRcvd    Number of received power supplies.
      @param nLinkRelayCountExpected   Number of expected link relays.
      @param pnLinkRelayCountRcvd      Number of received link relays.
      @param nFanCountExpected         Number of expected fans.
      @param pnFanCountRcvd            Number of received fans.
      @param pnTemperature             Temperature of the device.
      @param pnOutputVoltage           Output voltage of the CAN port.
      @param pnOutputCurrent           Output current of the CAN port.
      @param pbPortRelay               State of the relay of the CAN port.
      @param pnInputVoltage            Array of power supply input voltages.
      @param pbLinkRelay               Array of link relay states.
      @param pbFanLock                 Array of fan lock states.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANGetPowerStatus( AnaInt32    hHandle,
                                                                 AnaUInt8    nPowerSupplyCountExpected, AnaUInt8  * pnPowerSupplyCountRcvd,
                                                                 AnaUInt8    nLinkRelayCountExpected,   AnaUInt8  * pnLinkRelayCountRcvd,
                                                                 AnaUInt8    nFanCountExpected,         AnaUInt8  * pnFanCountRcvd,
                                                                 AnaInt16  * pnTemperature,             AnaUInt16 * pnOutputVoltage,
                                                                 AnaUInt16 * pnOutputCurrent,           AnaInt32  * pbPortRelay,
                                                                 AnaUInt16 * pnInputVoltage,            AnaInt32  * pbLinkRelay,
                                                                 AnaInt32  * pbFanLock );


   /** Sets the output power relais status from the CAN quattro PM partner.
      @param hHandle             Device handle (from a successfull #OpenDevice call).
      @param bRelaisCurrentPort  State of the output power relay of the current CAN port.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANSetPowerRelais( AnaInt32 hHandle, AnaInt32 bRelaisCurrentPort );


   /** Sets the active power supplies of the CAN quattro PM partner.
      Note that this only tells the driver which supplies should be active for
      monitoring purposes. It doesn't really enable or disable them.
      @param hHandle             Device handle (from a successfull #OpenDevice call).
      @param nBitmask   Bitmask with the active power supplies.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANSetActivePowerSupplies( AnaInt32 hHandle, AnaUInt32 nBitmask );


   /** Gets the Connect state of the ip connection to the CAN partner.
      @param hHandle         Device handle (from a successfull #OpenDevice call).
      @return. ConnectState.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANDeviceConnectState( AnaInt32 hHandle );


   /** Gets the Connect state of the ip connection to the CAN partner.
      @param hHandle         Device handle (from a successfull #OpenDevice call).
      @param nAliveTime      Standard tcp/ip timeout in seconds.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANStartAlive( AnaInt32 hHandle, AnaUInt32 nAliveTime );
   

   /** Sets the callback functions for CANOpen mode which are called for incoming CANOpen message.
       @param hHandle Device handle (from a successfull #OpenDevice call).
       @param pFunctionPDO    Pointer to the function which is called for incoming PDO message.
       @param pFunctionSYNC   Pointer to the function which is called for incoming SYNC message.
       @param pFunctionEMCY   Pointer to the function which is called for incoming EMCY message.
       @param pFunctionGUARD  Pointer to the function which is called for incoming GUARD message.
       @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero.
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenSetCallback( AnaInt32 hHandle,
                                                                  CAN_OPEN_PF_CALLBACK_PDO       pFunctionPDO,
                                                                  CAN_OPEN_PF_CALLBACK_SYNC      pFunctionSYNC,
                                                                  CAN_OPEN_PF_CALLBACK_EMCY      pFunctionEMCY,
                                                                  CAN_OPEN_PF_CALLBACK_GUARD     pFunctionGUARD,
                                                                  CAN_OPEN_PF_CALLBACK_UNDEFINED pFunctionUndefined );


   
   /** Sets the CANOpen parameter of the AnaGate CAN device.
      @param hHandle        Device handle (from a successfull #OpenDevice call).
      @param nCANOpenModus  0=Off / 1=On.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero. 
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenSetConfig( AnaInt32 hHandle, AnaUInt8 nCANOpenModus );

   /** Gets the CANOpen parameter of the AnaGate CAN device.
      @param hHandle         Device handle (from a successfull #OpenDevice call).
      @param pnCANOpenModus  Pointer to the CanOpenModus 0=Off / 1=On.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero. 
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenGetConfig( AnaInt32 hHandle, AnaUInt8 * pnCANOpenModus );

   /** Sets the Sync mode of the AnaGate.
      @param hHandle      Device handle (from a successfull #OpenDevice call).
      @param nPeriodTime  0 = Sync mode off / >0 = Sync mode on with specified period time.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero. 
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenSetSYNCMode( AnaInt32 hHandle, AnaInt32 nPeriodTime );

   /** Sends a NMT message to the specified CANOpen slave.
      @param hHandle  Device handle (from a successfull #OpenDevice call).
      @param nNodeID  Node id of CANOpen slave.
      @param nNMTTyp  Type of NMT message.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero. 
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenSendNMT( AnaInt32 hHandle, AnaUInt8 nNodeID, AnaUInt8 nNMTTyp );

   /** Sends a SYNC message to the CAN bus.
      @param hHandle Device handle (from a successfull #OpenDevice call).
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero. 
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenSendSYNC( AnaInt32 hHandle );

   /** Sends a TIME STAMP message to the CAN bus.
      @param hHandle Device handle (from a successfull #OpenDevice call).
      @param nDay    Days since 01.01.1984.
      @param nMs     Milliseconds since midnight.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero. 
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenSendTIME( AnaInt32 hHandle, AnaUInt32 nDay, AnaUInt32 nMs );

   /** Sends a PDO message to the specified CANOpen slave.
      @param hHandle      Device handle (from a successfull #OpenDevice call).
      @param nNodeID      Node id of CANOpen slave.
      @param nPDOTyp      Type of PDO message.
      @param nDataLength  Number of bytes in PDO (1-8).
      @param pcBuffer     Pointer to the buffer containing the data to be written.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero. 
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenSendPDO( AnaInt32 hHandle, AnaUInt8 nNodeID, AnaUInt8 nPDOTyp, AnaUInt8 nDataLength, const char * pcBuffer );

   /** Sends a SDO message (for reading a trivial entry 1-4Bytes) to the specified CANOpen slave.
      @param hHandle       Device handle (from a successfull #OpenDevice call).
      @param nNodeID       Node id of CANOpen slave.
      @param nIndex        Index of CANOpenSlave to be readed.
      @param nSubindex     Subindex of CANOpenSlave to be readed.
      @param nTimeout      Timeout of wait for confirmation of CANOpen slave.
      @param pnSDOTyp      Pointer to the buffer type of readed SDO message.
      @param pnSDOReadData Pointer to the buffer who containing the readed data.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero. 
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenSendSDORead( AnaInt32 hHandle, AnaUInt8 nNodeID, AnaInt32 nIndex, AnaUInt8 nSubindex, AnaInt32 nTimeout, AnaUInt8 * pnSDOReadTyp, AnaUInt32 * pnSDOReadData );

   /** Sends a SDO message (for writing a trivial entry 1-4Bytes) to the specified CANOpen slave.
      @param hHandle       Device handle (from a successfull #OpenDevice call).
      @param nNodeID       Node id of CANOpen slave.
      @param nSDOWriteTyp  Type of SDO message.
      @param nIndex        Index of CANOpenSlave to be readed.
      @param nSubindex     Subindex of CANOpenSlave to be readed.
      @param nTimeout      Timeout of wait for confirmation of CANOpen slave.
      @param nSDOWriteData buffer who containing the data to be written.
      @param pnSDOReadTyp  Pointer to the type of readed SDO message.
      @param pnSDOReadData Pointer to the buffer who containing the readed data.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero. 
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenSendSDOWrite( AnaInt32 hHandle, AnaUInt8 nNodeID, AnaUInt8 nSDOWriteTyp, AnaInt32 nIndex, AnaUInt8 nSubindex, AnaInt32 nTimeout, AnaUInt32 nSDOWriteData, AnaUInt8 * pnSDOReadTyp, AnaUInt32 * pnSDOReadData );

   /** Sends a SDO message (for reading a complex entry) to the specified CANOpen slave.
      @param hHandle      Device handle (from a successfull #OpenDevice call).
      @param nNodeID      Node id of CANOpen slave.
      @param nIndex       Index of CANOpenSlave to be readed.
      @param nSubindex    Subindex of CANOpenSlave to be readed.
      @param nTimeout     Timeout of wait for confirmation of CANOpen slave.
      @param nReadLen     Length of data to read.
      @param pnSDOTyp     Pointer to the type of readed SDO message.
      @param pnReadedLen  Pointer to the length of the readed data
      @param pSDOReadData Pointer to the buffer who containing the readed data.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero. 
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenSendSDOReadBlock( AnaInt32 hHandle, AnaUInt8 nNodeID, AnaInt32 nIndex, AnaUInt8 nSubindex, AnaInt32 nTimeout, AnaInt32 nReadLen, AnaUInt8 * pnSDOReadTyp, AnaInt32 * pnReadedLen, unsigned char * pSDOReadData );

   /** Sends a SDO message (for writing a complex entry) to the specified CANOpen slave.
      @param hHandle       Device handle (from a successfull #OpenDevice call).
      @param nNodeID       Node id of CANOpen slave.
      @param nIndex        Index of CANOpenSlave to be readed.
      @param nSubindex     Subindex of CANOpenSlave to be readed.
      @param nTimeout      Timeout of wait for confirmation of CANOpen slave.
      @param nWriteLen     Length of data to write.
      @param pSDOWriteData Pointer to the buffer who containing the data to be written.
      @param pnSDOReadTyp  Pointer to the type of readed SDO message.
      @param pnSDOReadData Pointer to the buffer buffer who containing the readed data.
      @return. If the function succeeds, the return value is zero. If the function fails, the return value is non zero. 
   */
   ANAGATEDLL_API AnaInt32 ANAGATEDLL_CALLING CANopenSendSDOWriteBlock( AnaInt32 hHandle, AnaUInt8 nNodeID, AnaInt32 nIndex, AnaUInt8 nSubindex, AnaInt32 nTimeout, AnaInt32 nWriteLen, const unsigned char * pSDOWriteData, AnaUInt8 * pnSDOReadTyp, AnaUInt32 * pnSDOReadData );



#ifdef __cplusplus
}
#endif // __cplusplus

#endif // _ANAGATE_DLL_CAN_H
