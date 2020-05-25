from . import constants as const
from .exceptions import EnvvarNameError


class EnvVar(object):
    class Attrib(object):
        def __init__(self, handle=None, type_=None, size=None):
            self.handle = handle
            self.type_ = type_
            self.size = size

    def __init__(self, channel):
        self.__dict__['_channel'] = channel
        self.__dict__['_attrib'] = {}

    def _ensure_open(self, name):
        if not name.startswith('_'):
            raise EnvvarNameError(name)
        # We just check the handle here
        if name not in self.__dict__['_attrib']:
            self._attrib[name] = EnvVar.Attrib(
                *self._channel.scriptEnvvarOpen(name))

    def __getattr__(self, name):
        self._ensure_open(name)
        handle = self._attrib[name].handle
        if self._attrib[name].type_ == const.kvENVVAR_TYPE_INT:
            value = self._channel.scriptEnvvarGetInt(handle)
        elif self._attrib[name].type_ == const.kvENVVAR_TYPE_FLOAT:
            value = self._channel.scriptEnvvarGetFloat(handle)
        elif self._attrib[name].type_ == const.kvENVVAR_TYPE_STRING:
            size = self._attrib[name].size
            value = self._channel.scriptEnvvarGetData(handle, size)
        else:
            msg = "getting is not implemented for type {type_}"
            msg = msg.format(type_=self._attrib[name].type_)
            raise TypeError(msg)
        return value

    def __setattr__(self, name, value):
        self._ensure_open(name)
        handle = self._attrib[name].handle
        if self._attrib[name].type_ == const.kvENVVAR_TYPE_INT:
            value = self._channel.scriptEnvvarSetInt(handle, value)
        elif self._attrib[name].type_ == const.kvENVVAR_TYPE_FLOAT:
            value = self._channel.scriptEnvvarSetFloat(handle, value)
        elif self._attrib[name].type_ == const.kvENVVAR_TYPE_STRING:
            value = str(value)
            size = self._attrib[name].size
            value = self._channel.scriptEnvvarSetData(handle, value, size)
        else:
            msg = "setting is not implemented for type {type_}"
            msg = msg.format(type_=self._attrib[name].type_)
            raise TypeError(msg)
