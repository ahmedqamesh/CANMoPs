# -*- coding: utf-8 -*-
"""
Auxiliary functions which extend logging functionality

Example
-------
>>> import logging, coloredlogs, verboselogs
>>> from extend_logging import extend_logging
>>> extend_logging()
>>> verboselogs.install()
>>> logger = logging.getLogger(__name__)
>>> coloredlogs.install(isatty=True)
>>> logger.notice('This is a notice.')
>>> logger.success('This was a success.')


:Author: Sebastian Scholz
:Contact: sebastian.scholz@cern.ch
"""

import coloredlogs as cl

# Platform dependent imports
if cl.WINDOWS:
    from win32gui import GetWindowText, GetForegroundWindow


def extend_logging():
    """Some extras for users of the Anaconda Prompt on Windows.

    This customizes the coloredlogs module so that bold fonts are displayed
    correctly. Note that detects the usage of the Anaconda Prompt and Spyder
    console via its window title.
    """
    cl.DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
    if cl.WINDOWS:
        SPYDER = GetWindowText(GetForegroundWindow()).startswith('Spyder')
        if SPYDER:
            print('Spyder detected!')
        cl.NEED_COLORAMA = not SPYDER
        ANACONDA = GetWindowText(GetForegroundWindow()).startswith('Anaconda')
        if ANACONDA:
            print('Anaconda detected!')
        cl.CAN_USE_BOLD_FONT = not cl.NEED_COLORAMA or ANACONDA
        cl.DEFAULT_FIELD_STYLES['levelname']['bold'] = cl.CAN_USE_BOLD_FONT
        cl.DEFAULT_LEVEL_STYLES['success']['bold'] = cl.CAN_USE_BOLD_FONT
        cl.DEFAULT_LEVEL_STYLES['critical']['bold'] = cl.CAN_USE_BOLD_FONT


def removeAllHandlers(logger):
    """Ensure that all each :class:`~logging.FileHandler` is removed.

    When errors during initialisation appear the Handlers may not removed and
    still be present in the next run. This method cleanes up any Handlers that
    may have survived.

    Parameters
    ----------
    logger : :obj:`~logging.Logger`
        The Logger object from which all Handlers are removed.
    """
    while len(logger.handlers) > 0:
        h = logger.handlers[0]
        logger.removeHandler(h)


if __name__ == '__main__':
    import verboselogs

    extend_logging()
    verboselogs.install()

    logger = verboselogs.VerboseLogger(__name__)

    cl.install(fmt='%(asctime)s %(levelname)-8s %(message)s', 
               level='DEBUG', isatty=True, milliseconds=True)

    logger.notice('This is a notice.')
    logger.success('This was a success.')

