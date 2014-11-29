import os
import logging

log = logging.Logger('command', level=logging.DEBUG)

# TODO: find all formats
FORMAT = 'bibtex'

URL_ROOT = 'http://dl.acm.org/'
URL_BIBTEX = URL_ROOT + 'exportformats.cfm?id={id}&expformat=' + FORMAT

INVALID_CHARS = list('/?|:*\"<>\\')

CONFERENCE_PAGE = './pages/Proceedings of the 37th international ACM SIGIR conference on Research & development in information retrieval.html'

BIB_FILE = ''
BIB_ENCODING = 'utf8'

SLEEP_TIME_RANGE = (4, 10)
RETRY = 1

# log.info('loading proxy file...')
print('loading proxy file...')
PROXIES = []
with open('proxy.txt') as f:
    PROXIES = [l for l in f]
print('%d proxies loaded.' % len(PROXIES))
# log.info('%d proxies loaded.' % len(PROXIES))

print('testing proxies...')
# log.info('testing proxies...')
PROXIES = list(filter(lambda ip:
        os.system('ping %s -n 1 > nul' % ip.split(':')[1][2:]) == 0, PROXIES))
if PROXIES:
    print('%d proxies available.' % len(PROXIES))
    # log.info('%d proxies available.' % len(PROXIES))
else:
    print('no proxy available.')
    # log.warning('no proxy available.')


ERROR_OUTPUT = 'err.txt'
