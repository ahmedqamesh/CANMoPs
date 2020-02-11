import logging
import coloredlogs 
import coloredlogs as cl

FORMAT = '%(asctime)s-[%(name)-7s]- %(levelname)-7s %(message)s'

def setup_main_logger(name='MYWorkSpace', level=logging.INFO):
    _reset_all_loggers()
    _set_basil_logger_to(logging.WARNING)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    _setup_coloredlogs(logger)
    _add_success_level(logger)

    _add_logfiles_to(logger)

    return logger

def setup_logging(loglevel):  # set logging level of this module
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level)
    
def setup_derived_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    _setup_coloredlogs(logger)
    _add_success_level(logger)

    _add_logfiles_to(logger)

    return logger


def setup_logfile(filename, level=logging.INFO):
    fh = logging.FileHandler(filename)
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter(FORMAT))

    # Add filehandler to all active loggers
    for lg in logging.Logger.manager.loggerDict.values():
        if isinstance(lg, logging.Logger):
            lg.addHandler(fh)

    return fh


def close_logfile(fh):
    for lg in logging.Logger.manager.loggerDict.values():
        if isinstance(lg, logging.Logger):
            lg.removeHandler(fh)


def _add_logfiles_to(logger):
    fhs = []
    for lg in logging.Logger.manager.loggerDict.values():
        if isinstance(lg, logging.Logger):
            for handler in lg.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    fhs.append(handler)

    for fh in fhs:
        logger.addHandler(fh)


def _setup_coloredlogs(logger):
    loglevel = logger.getEffectiveLevel()
    coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {},
                                        'hostname': {},
                                        'levelname': {'bold': True},
                                        'name': {},
                                        'programname': {}}
    coloredlogs.DEFAULT_LEVEL_STYLES = {'critical': {'color': 'red', 'bold': True},
                                        'debug': {'color': 'magenta'},
                                        'error': {'color': 'red', 'bold': True},
                                        'info': {},
                                        'success': {'color': 'green'},
                                        'warning': {'color': 'yellow'}}
    coloredlogs.DEFAULT_LOG_LEVEL = loglevel

    coloredlogs.install(fmt=FORMAT, milliseconds=True, loglevel=loglevel)


def _add_success_level(logger):
    logging.SUCCESS = 25  # WARNING(30) > SUCCESS(25) > INFO(20)
    logging.addLevelName(logging.SUCCESS, 'SUCCESS')
    logger.success = lambda msg, *args, **kwargs: logger.log(logging.SUCCESS, msg, *args, **kwargs)

def _reset_all_loggers():
    logging.root.handlers = []


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
          
