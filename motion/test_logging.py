"""Test the log logic."""
import logging
import os

try:
    from systemd.journal import JournalHandler
except ModuleNotFoundError:
    pass


def get_logger():
    logger = logging.getLogger('test')
    if not os.name == 'nt':
        logger.addHandler(JournalHandler())
        logger.setLevel(logging.INFO)
    return logger


log = get_logger()

log.info('PID: {}'.format(os.getpid()))
