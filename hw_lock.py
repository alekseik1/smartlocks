import threading

from loguru import logger

hw_lock = threading.Lock()

DEBUG_ON_ = False


def hw_acq(s=''):
    logger.debug('acquiring lock with reason: {}'.format(s))
    global hw_lock, DEBUG_ON_
    hw_lock.acquire()
    logger.debug('(DONE) acquiring lock with reason: {}'.format(s))


def hw_rel(s=''):
    logger.debug('releasing lock taken by: {}'.format(s))
    global hw_lock, DEBUG_ON_
    hw_lock.release()
    logger.debug('(DONE) releasing lock taken by: {}'.format(s))
