# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 12:16:51 2018

@author: Sebastian Scholz
"""

import ctypes as ct

from . import dllLoader


class libCANDLL(dllLoader.MyDll):
    
    CBFUNC = ct.CFUNCTYPE(ct.c_void_p, ct.c_int32, ct.POINTER(ct.c_char),
                          ct.c_int32, ct.c_int32, ct.c_int32)
    CBFUNCEX = ct.CFUNCTYPE(ct.c_void_p, ct.c_int32, ct.POINTER(ct.c_char),
                            ct.c_int32, ct.c_int32, ct.c_int32, ct.c_int32,
                            ct.c_int32)
    function_prototypes = {
        'DLLInfo': [[ct.c_char_p, ct.c_int32], ct.c_int32],
        'CANOpenDevice': [[ct.POINTER(ct.c_int32), ct.c_int32,
                           ct.c_int32, ct.c_int32, ct.c_char_p, ct.c_int32],
                          ct.c_int32],
        'CANOpenDeviceEx': [[ct.POINTER(ct.c_int32), ct.c_int32,
                           ct.c_int32, ct.c_int32, ct.c_char_p, ct.c_int32,
                           ct.c_int32], ct.c_int32],
        'CANCloseDevice': [[ct.c_int32], ct.c_int32],
        'CANSetGlobals': [[ct.c_int32, ct.c_uint32, ct.c_uint8,
                           ct.c_int32, ct.c_int32, ct.c_int32], ct.c_int32],
        'CANGetGlobals': [[ct.c_int32, ct.POINTER(ct.c_uint32),
                           ct.POINTER(ct.c_uint8), ct.POINTER(ct.c_uint32),
                           ct.POINTER(ct.c_uint32), ct.POINTER(ct.c_uint32)],
                          ct.c_int32],
        'CANSetFilter': [[ct.c_int32, ct.POINTER(ct.c_uint32)], ct.c_int32],
        'CANGetFilter': [[ct.c_int32, ct.POINTER(ct.c_uint32)], ct.c_int32],
        'CANSetTime': [[ct.c_int32, ct.c_uint32, ct.c_uint32], ct.c_int32],
        'CANGetTime': [[ct.c_int32, ct.POINTER(ct.c_int32),
                        ct.POINTER(ct.c_uint32), ct.POINTER(ct.c_uint32)],
                       ct.c_int32],
        'CANWrite': [[ct.c_int32, ct.c_int32, ct.c_char_p,
                      ct.c_int32, ct.c_int32], ct.c_int32],
        'CANWriteEx': [[ct.c_int32, ct.c_int32, ct.c_char_p,
                      ct.c_int32, ct.c_int32, ct.POINTER(ct.c_int32),
                      ct.POINTER(ct.c_int32)], ct.c_int32],
        'CANSetCallback': [[ct.c_int32, CBFUNC], ct.c_int32],
        'CANSetCallbackEx': [[ct.c_int32, CBFUNCEX], ct.c_int32],
        'CANSetMaxSizePerQueue': [[ct.c_int32, ct.c_uint32], ct.c_int32],
        'CANGetMessage': [[ct.c_int32, ct.POINTER(ct.c_uint32),
                           ct.POINTER(ct.c_int32), ct.c_char_p,
                           ct.POINTER(ct.c_uint8), ct.POINTER(ct.c_int32),
                           ct.POINTER(ct.c_int32), ct.POINTER(ct.c_int32)],
                          ct.c_int32],
        'CANReadDigital': [[ct.c_int32, ct.POINTER(ct.c_uint32),
                            ct.POINTER(ct.c_uint32)], ct.c_int32],
        'CANWriteDigital': [[ct.c_int32, ct.c_uint32], ct.c_int32],
        # TODO: Include array
        'CANReadAnalog': [[ct.c_int32, ct.POINTER(ct.c_uint32),
                           ct.POINTER(ct.c_uint32), ct.POINTER(ct.c_uint16)],
                          ct.c_int32],
        'CANWriteAnalog': [[ct.c_int32, ct.c_uint32 * 4, ct.c_uint16],
                           ct.c_int32],
        'CANRestart': [[ct.c_char_p, ct.c_int32], ct.c_int32],
        'CANDeviceConnectState': [[ct.c_int32], ct.c_int32],
        'CANErrorMessage': [[ct.c_int32, ct.c_char_p, ct.c_int32], ct.c_int32]
        }

    def __init__(self, ct_dll):
        # set default values for function_prototypes
        self.default_restype = ct.c_int
        self.default_errcheck = self._error_check
        super(libCANDLL, self).__init__(ct_dll, **self.function_prototypes)

    def _error_check(self, result, func, arguments):
        """Error function used in ctype calls for canlib DLL."""
        if result < 0:
            # raise can_error(result)
            pass
        else:  
            return result