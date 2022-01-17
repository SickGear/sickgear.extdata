from __future__ import print_function

import locale
import os
import sys

import rollback

sys.path.insert(1, '../../../SickGear')

import sickbeard
from sickbeard import logger, classes
try:
    from sickbeard.exceptions import ex
except ImportError:
    from lib.exceptions_helper import ex

try:
    locale.setlocale(locale.LC_ALL, '')
except (locale.Error, IOError):
    pass
try:
    sickbeard.SYS_ENCODING = locale.getpreferredencoding()
except (locale.Error, IOError):
    pass

from lib.configobj import ConfigObj

sickbeard.DATA_DIR = os.environ.get('SickGearData') or os.path.realpath(r'..\..\..\SickGear')
sickbeard.CACHE_DIR = os.environ.get('SickGearCache') or os.path.realpath(r'..\..\..\SickGear\cache')
sickbeard.CONFIG_FILE = os.path.join(sickbeard.DATA_DIR, 'config.ini')
sickbeard.CFG = ConfigObj(sickbeard.CONFIG_FILE)

# For OSes that are poorly configured I'll just randomly force UTF-8
if not sickbeard.SYS_ENCODING or sickbeard.SYS_ENCODING in ('ANSI_X3.4-1968', 'US-ASCII', 'ASCII'):
    sickbeard.SYS_ENCODING = 'UTF-8'


class test_logger(logger.SBRotatingLogHandler):

    def __init__(self, log_file):
        super(test_logger, self).__init__(log_file)

    def log(self, to_log, log_level=logger.MESSAGE):
        if logger.MESSAGE == log_level:
            print('LOGGER:', to_log)


if not hasattr(classes, 'LoadingMessage'):
    import threading
    import copy

    class LoadingMessage(object):
        def __init__(self):
            self.lock = threading.Lock()
            self._message = [{'msg': 'Loading', 'progress': -1}]

        @property
        def message(self):
            with self.lock:
                return copy.deepcopy(self._message)

        @message.setter
        def message(self, msg):
            with self.lock:
                if 0 != len(self._message) and msg != self._message[-1:][0]['msg']:
                    self._message.append({'msg': msg, 'progress': -1})

        def set_msg_progress(self, msg, progress):
            with self.lock:
                for m in self._message:
                    if msg == m.get('msg'):
                        m['progress'] = progress
                        return
                self._message.append({'msg': msg, 'progress': progress})

        def reset(self, msg=None):
            msg = msg or {'msg': 'Loading', 'progress': -1}
            with self.lock:
                self._message = [msg]


    classes.LoadingMessage = LoadingMessage
    classes.loading_msg = LoadingMessage()


class test_load_msg(classes.LoadingMessage):

    def __init__(self):
        super(test_load_msg, self).__init__()

    @property
    def message(self):
        return super(test_load_msg, self).message()

    @message.setter
    def message(self, value):
        print('LOAD MSG:', value)
        super(test_load_msg, self).message(value)

    def set_msg_progress(self, msg, progress):
        print('LOAD MSG:', '%s: %s' % (msg, progress))
        super(test_load_msg, self).set_msg_progress(msg, progress)


# replace logger and loading classes with print debugging
logger.sb_log_instance = test_logger('')
classes.loading_msg = test_load_msg()

try:
    cm = rollback.ConfigFile()
    #cm.run(19)
    rc = rollback.CacheDb()
    rc.load_msg = 'Test Cache'
    # rc.run(7, raise_exception=True)
    rm = rollback.MainDb()
    rm.load_msg = 'Test Main'
    rm.run(20016, raise_exception=True)
    rf = rollback.FailedDb()
    rf.load_msg = 'Test Failed'
    #rf.run(2, raise_exception=True)
except (BaseException, Exception) as e:
    print(ex(e))
