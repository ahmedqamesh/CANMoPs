import ctypes as ct

from .. import dllLoader
from .exceptions import can_error

_no_errcheck = dllLoader.no_errcheck


class CanlibDll(dllLoader.MyDll):
    function_prototypes = {
        'canAccept': [[ct.c_int, ct.c_long, ct.c_uint]],
        'canBusOff': [[ct.c_int]],
        'canBusOn': [[ct.c_int]],
        'canClose': [[ct.c_int]],
        'canGetBusParams': [[ct.c_int, ct.POINTER(ct.c_long), ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint)]],
        'canGetBusParamsFd': [[ct.c_int, ct.POINTER(ct.c_long), ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint)]],
        'canGetChannelData': [[ct.c_int, ct.c_int, ct.c_void_p, ct.c_size_t]],
        'canGetErrorText': [[ct.c_int, ct.c_char_p, ct.c_uint]],
        'canGetNumberOfChannels': [[ct.POINTER(ct.c_int)]],
        'canGetVersion': [[], ct.c_short, _no_errcheck],  # Never fails (supposedly)
        'canGetVersionEx': [[ct.c_uint], ct.c_uint, _no_errcheck],  # Never fails
        'canInitializeLibrary': [[], None, _no_errcheck],  # Returns void, no errcheck function
        'canIoCtl': [[ct.c_int, ct.c_uint, ct.c_void_p, ct.c_uint]],
        'canOpenChannel': [[ct.c_int, ct.c_int]],
        'canReadSpecificSkip': [[ct.c_int, ct.c_long, ct.c_void_p, ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint), ct.POINTER(ct.c_ulong)]],
        'canReadStatus': [[ct.c_int, ct.POINTER(ct.c_ulong)]],
        'canReadSyncSpecific': [[ct.c_int, ct.c_long, ct.c_ulong]],
        'canReadWait': [[ct.c_int, ct.POINTER(ct.c_long), ct.c_void_p, ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint), ct.POINTER(ct.c_ulong), ct.c_ulong]],
        'canRequestChipStatus': [[ct.c_int]],
        'canSetAcceptanceFilter': [[ct.c_int, ct.c_uint, ct.c_uint, ct.c_int]],
        'canSetBusOutputControl': [[ct.c_int, ct.c_ulong]],
        'canSetBusParams': [[ct.c_int, ct.c_long, ct.c_uint, ct.c_uint, ct.c_uint, ct.c_uint, ct.c_uint]],
        'canSetBusParamsFd': [[ct.c_int, ct.c_long, ct.c_uint, ct.c_uint, ct.c_uint]],
        'canTranslateBaud': [[ct.POINTER(ct.c_long), ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint)]],
        'canUnloadLibrary': [[]],
        'canWrite': [[ct.c_int, ct.c_long, ct.c_void_p, ct.c_uint, ct.c_uint]],
        'canWriteWait': [[ct.c_int, ct.c_long, ct.c_void_p, ct.c_uint, ct.c_uint, ct.c_ulong]],
        'kvDeviceGetMode': [[ct.c_int, ct.POINTER(ct.c_int)]],
        'kvDeviceSetMode': [[ct.c_int, ct.c_int]],
        'kvFileCopyFromDevice': [[ct.c_int, ct.c_char_p, ct.c_char_p]],
        'kvFileCopyToDevice': [[ct.c_int, ct.c_char_p, ct.c_char_p]],
        'kvFileDelete': [[ct.c_int, ct.c_char_p]],
        'kvFileGetCount': [[ct.c_int, ct.POINTER(ct.c_int)]],
        'kvFileGetName': [[ct.c_int, ct.c_int, ct.c_char_p, ct.c_int]],
        'kvFlashLeds': [[ct.c_int, ct.c_int, ct.c_int]],
        'kvReadDeviceCustomerData': [[ct.c_int, ct.c_int, ct.c_int, ct.c_void_p, ct.c_size_t]],
        'kvReadTimer': [[ct.c_int, ct.POINTER(ct.c_int)]],
        'kvScriptEnvvarClose': [[ct.c_int64]],
        'kvScriptEnvvarGetData': [[ct.c_int64, ct.c_void_p, ct.c_int, ct.c_int]],
        'kvScriptEnvvarGetFloat': [[ct.c_int64, ct.POINTER(ct.c_float)]],
        'kvScriptEnvvarGetInt': [[ct.c_int64, ct.POINTER(ct.c_int)]],
        'kvScriptEnvvarOpen': [[ct.c_int, ct.c_char_p, ct.POINTER(ct.c_int), ct.POINTER(ct.c_int)], ct.c_int64],
        'kvScriptEnvvarSetData': [[ct.c_int64, ct.c_void_p, ct.c_int, ct.c_int]],
        'kvScriptEnvvarSetFloat': [[ct.c_int64, ct.c_float]],
        'kvScriptEnvvarSetInt': [[ct.c_int64, ct.c_int]],
        'kvScriptLoadFile': [[ct.c_int, ct.c_int, ct.c_char_p]],
        'kvScriptLoadFileOnDevice': [[ct.c_int, ct.c_int, ct.c_char_p]],
        'kvScriptSendEvent': [[ct.c_int, ct.c_int, ct.c_int, ct.c_int, ct.c_uint]],
        'kvScriptStart': [[ct.c_int, ct.c_int]],
        'kvScriptStop': [[ct.c_int, ct.c_int, ct.c_int]],
        'kvScriptTxeGetData': [[ct.c_char_p, ct.c_int, ct.c_void_p, ct.POINTER(ct.c_uint)]],
        'kvScriptUnload': [[ct.c_int, ct.c_int]],
    }

    def __init__(self, ct_dll):
        # set default values for function_prototypes
        self.default_restype = ct.c_int
        self.default_errcheck = self._error_check
        super(CanlibDll, self).__init__(ct_dll, **self.function_prototypes)

    def _error_check(self, result, func, arguments):
        """Error function used in ctype calls for canlib DLL."""
        if result < 0:
            raise can_error(result)
        else:
            return result
