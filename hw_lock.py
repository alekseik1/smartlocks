import threading

from log_writing import *

hw_lock = threading.Lock()

DEBUG_ON_ = False


def hw_acq(s=''):
    global hw_lock, DEBUG_ON_
    hw_lock.acquire()
    if DEBUG_ON_: print_log("hw mutex acqired: " + s)


def hw_rel(s=''):
    global hw_lock, DEBUG_ON_
    hw_lock.release()
    if DEBUG_ON_: print_log("hw mutex released: " + s)
