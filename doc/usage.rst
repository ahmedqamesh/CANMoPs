.. include:: abbr.rst
Usage
=====
.. role:: bash(code)
   :language: bash

OPC UA server
-------------

Upon installation the commandline tool :bash:`DCSControllerServer` is created. In most cases there should be almost no configuration neccessary as it does not even have any positional arguments::

    usage: DCSControllerServer [-h] [-E ENDPOINT] [-e EDSFILE] [-x XMLFILE]
                               [-K | -A] [-C CHANNEL] [-i IPADDRESS] [-b BITRATE]
                               [-c {NOTSET,WARNING,INFO,VERBOSE,CRITICAL,DEBUG,SUCCESS,NOTICE,ERROR,SPAM}]
                               [-f {NOTSET,WARNING,INFO,VERBOSE,CRITICAL,DEBUG,SUCCESS,NOTICE,ERROR,SPAM}]
                               [-d LOGDIR] [-v]

CAN interfaces:
    -A, --anagate               Use AnaGate CAN Ethernet interface
    -K, --kvaser                Use Kvaser CAN interface

OPC UA server configuration:
    -E ENDPOINT, --endpoint ENDPOINT    Endpoint of the OPCUA server (default: ``opc.tcp://localhost:4840/``)
    -e EDSFILE, --edsfile EDSFILE       File path of Electronic Data Sheet (EDS) (default: */path/to/source/CANControllerForPSPPv1.eds*)
    -x XMLFILE, --xmlfile XMLFILE       File path of OPCUA XML design file (default: */path/to/source/dcscontrollerdesign.xml*)

CAN settings:
    -C CHANNEL, --channel CHANNEL           Number of CAN channel to use (default: 0)
    -i IPADDRESS, --ipaddress IPADDRESS     IP address of the AnaGate Ethernet CAN interface (default: ``192.168.1.254``)
    -b BITRATE, --bitrate BITRATE           CAN bitrate as integer in bit/s (default: 125000)

Logging settings:
    -c LEVEL, --console_loglevel LEVEL      Level of console logging (default: :data:`~verboselogs.NOTICE`)
    -f LEVEL, --file_loglevel LEVEL         Level of file logging (default: :func:`INFO <logging.info>`)
    -d LOGDIR, --logdir LOGDIR              Directory where log files should be stored (default: */path/to/source/log/*)

Possible logging levels are:
    * :data:`~logging.NOTSET`
    * :data:`~verboselogs.SPAM`
    * :func:`DEBUG <logging.debug>`
    * :data:`~verboselogs.VERBOSE`
    * :func:`INFO <logging.info>`
    * :data:`~verboselogs.NOTICE`
    * :data:`~verboselogs.SUCCESS`
    * :func:`WARNING <logging.warning>`
    * :func:`ERROR <logging.error>`
    * :func:`CRITICAL <logging.critical>`

Miscellaneous:
    -h, --help                  Show help message and exit
    -v, --version               Show program's version string and exit

AnaGate CAN interfaces
----------------------
It is very easy to connect to AnaGate |CAN| interfaces using the :class:`~analib.channel.Channel` class. Incoming |CAN| messages can be received via the :meth:`analib.channel.Channel.getMessage` method or by defining a callback function like :func:`analib.channel.cbFunc`.

Using callback functions
^^^^^^^^^^^^^^^^^^^^^^^^
It is quite easy to define a callback function for incoming CAN messages. Once defined it can be easily applied using the the :meth:`~analib.channel.Channel.setCallback` method. To deactivate a callback function it is neccessary to create a NULL pointer with the :func:`~ctypes.cast` function. This is done automatically when the :class:`~analib.channel.Channel` is :meth:`closed <analib.channel.Channel.close>`. For documentation of the arguments please refer to :func:`analib.channel.cbFunc`. An example code is given below::

    import analib
    import ctypes as ct

    def cbFunc(cobid, data, dlc, flag, handle):
        # Convert ct.LP_c_char to bytes object
        data = ct.string_at(data, dlc)
        print('Calling callback function with the following arguments:')
        print(f'    COBID: {cobid:03X}; Data: {data[:dlc].hex()}; DLC: {dlc}; '
              f'Flags: {flags}; Handle: {handle}')

    # Open a connection
    with analib.channel.Channel() as ch:
        # Activate the callback function
        ch.setCallback(analib.wrapper.dll.CBFUNC(cbFunc))
        while True:
            # Do some more work here
            pass

Note that the arguments of the callback function are passed as Python build-in types except for the data bytes which come as a :class:`~ctypes.c_char` :func:`~ctypes.POINTER` and needs to be converted to a :class:`bytes` object first using the :func:`~ctypes.string_at` function. It is not possible to define :class:`~ctypes.c_char_p` as argument type instead because it behaves differently and interprets bytes containing zero as terminating the byte sequence.
