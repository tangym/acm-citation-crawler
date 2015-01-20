import os
import logging
import logging.handlers
from multiprocessing.dummy import Pool as ThreadPool

# TODO: find all formats
FORMAT = 'bibtex'

URL_ROOT = 'http://dl.acm.org/'
URL_CITATION = URL_ROOT + 'citation.cfm?id={id}&preflayout=flat'
URL_BIBTEX = URL_ROOT + 'exportformats.cfm?id={id}&expformat=' + FORMAT

INVALID_CHARS = list('/?|:*\"<>\\')

CONFERENCE_PAGE = []
with open('pages.txt') as f:
    for l in f:
        if l.strip():
            CONFERENCE_PAGE += [l.strip()]

BIB_FILE = ''
BIB_ENCODING = 'utf8'



# CONFERENCE_NAME = os.path.basename(CONFERENCE_PAGE)
# name = CONFERENCE_NAME.split('.')
# name[-1] = 'bib'
# CONFERENCE_BIB = '.'.join(name)
# name[-1] = 'log'
# CONFERENCE_LOG = '.'.join(name)
CONFERENCE_LOG = '2015-01-17.log'

log = logging.getLogger('my logger')

handler = logging.handlers.RotatingFileHandler(CONFERENCE_LOG)
fmt = '%(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)
log.addHandler(handler)

handler = logging.StreamHandler()
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)
log.addHandler(handler)

log.setLevel(logging.DEBUG)

log.info('loading proxy file...')
PROXIES = []
PROXY_TABOO = []
with open('proxy.txt') as f:
    PROXIES = [l for l in f]
log.info('%d proxies loaded.' % len(PROXIES))

SLEEP_TIME_RANGE = (30, 150) # (2, 5)

# the distribution shape parameters of random sleep time
SLEEP_ALPHA = 2
SLEEP_BETA = 5

RETRY = 3
WORKER = int(len(PROXIES) * 0.3)
if WORKER > 15:
    WORKER = 15

log.info('%d workers boosted' % WORKER)
log.info('testing proxies...')

pool = ThreadPool(WORKER)
def is_available(ip):
    if os.system('ping %s -n 1 > nul' % ip.split(':')[1][2:]) == 0:
        return ip
    else:
        return ''
PROXIES = pool.map(is_available, PROXIES)
pool.close()
pool.join()

PROXIES = list(filter(lambda ip: ip, PROXIES))
if PROXIES:
    log.info('%d proxies available.' % len(PROXIES))
else:
    log.warning('no proxy available.')

