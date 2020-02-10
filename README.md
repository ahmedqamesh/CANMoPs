# MOPS DAQ for DCS Controller
This Python package provides a command line tool which communicate with the [<abbr title="Detector Control System">DCS</abbr>](https://twiki.cern.ch/twiki/bin/viewauth/Atlas/DetectorControlSystemMainPage "Only accessible with CERN account") ASIC: [Monitoring Of Pixel System (MOPS)](https://edms.cern.ch/ui/file/1909505/3/MOPS-specs-V3_docx_cpdf.pdf). It communicates with a <abbr title="Controller Area Network">CAN</abbr> interface and talks CANopen with connected DCS Controllers. Currently only CAN interfaces from [AnaGate](https://www.anagate.de/) (Ethernet) and [Kvaser](https://www.kvaser.com/) (USB) are supported.
## Installation
This Python package requires a working [Python 3.6](https://www.python.org/ "Official Python Homepage") Installation. I recommend the usage of [Anaconda](https://anaconda.org/ "Official Anaconda Homepage") which is available for all platforms and also easy to install and manage.
```
For more information contact ahmed.qamesh@cern.ch
```
## Dependencies
All third-party Python packages that are needed are installed on-the-fly so you do not need to worry about these. The necessary AnaGate libraries are also included in this repository. For the use of Kvaser CAN interfaces you have to install the [Kvaser drivers](https://www.kvaser.com/downloads-kvaser/ "Kvaser download page") first which are avaiable for [Windows](https://www.kvaser.com/downloads-kvaser/?utm_source=software&utm_ean=7330130980013&utm_status=latest) and [Linux](https://www.kvaser.com/downloads-kvaser/?utm_source=software&utm_ean=7330130980754&utm_status=latest).

### AnaGate
If you are using an AnaGate Ethernet CAN interface you will probably need to manually set the IP address of your network card so that the interface is part of its network. The default IP address of an AnaGate CAN interface is *192.168.1.254*, so you should set the IP address of your network card to *192.168.1.1*.

## Remarks
Although a Python program should be platform-independent, some things behave differently due to unequal behaviour of the drivers.
### Linux
If you want to use a virtual channel on a Linux machine you have to may have to start it manually with the following command

    $ sudo /usr/sbin/virtualcan.sh start

It has happened that the USB port was not correctly reset after the Kvaser interface has been disconnected so that the connection to other USB devices could not be established. As a workaround I recommend rebooting the system.
