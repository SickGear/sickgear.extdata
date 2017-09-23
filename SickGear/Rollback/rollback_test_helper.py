import locale
import os

import rollback
import sickbeard

try:
    locale.setlocale(locale.LC_ALL, '')
except (locale.Error, IOError):
    pass
try:
    sickbeard.SYS_ENCODING = locale.getpreferredencoding()
except (locale.Error, IOError):
    pass

sickbeard.DATA_DIR = os.environ.get('SickGearData') or os.path.realpath(r'..\..\DataSG')

# For OSes that are poorly configured I'll just randomly force UTF-8
if not sickbeard.SYS_ENCODING or sickbeard.SYS_ENCODING in ('ANSI_X3.4-1968', 'US-ASCII', 'ASCII'):
    sickbeard.SYS_ENCODING = 'UTF-8'

rollback.CacheDb().run(2)
rollback.MainDb().run(20005)
rollback.FailedDb().run(1)
