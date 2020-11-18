.. include:: abbr.rst
Installation
============

You can install the two packages very easy using :std:doc:`pip<installing/index>`. Once you have downloaded and unpacked or cloned the repository go into its top-level directory and run::

	$ pip install .

If you want to edit the code to your likings then run instead::

	$ pip install -e .

Dependencies
------------
All third-party Python packages that are needed are installed on-the-fly so you do not need to worry about these. The necessary AnaGate libraries are also included in this repository. For the use of Kvaser |CAN| interfaces you have to install the `Kvaser drivers`_ first which are available for `Windows`_ and `Linux`_.

Usage of AnaGate CAN interfaces
-------------------------------
AnaGate CAN interfaces (assuming the ones connected via Ethernet) have the default IP address ``192.168.1.254``. In order to be able to talk to the device you might want to change the IP address of your network card to something like ``192.168.1.1`` so that these two sit in the same network.

.. _`Kvaser drivers`: https://www.kvaser.com/downloads-kvaser/
.. _`Windows`: https://www.kvaser.com/downloads-kvaser/?utm_source=software&utm_ean=7330130980013&utm_status=latest
.. _`Linux`: https://www.kvaser.com/downloads-kvaser/?utm_source=software&utm_ean=7330130980754&utm_status=latest