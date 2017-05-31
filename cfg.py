import logging
import logging.handlers

# TODO: find all formats
FORMAT = 'bibtex'

URL_ROOT = 'http://dl.acm.org/'
URL_CITATION = URL_ROOT + 'citation.cfm?id={id}&preflayout=flat'
URL_BIBTEX = URL_ROOT + 'exportformats.cfm?id={id}&expformat=' + FORMAT

INVALID_CHARS = list('/?|:*\"<>\\')

BIB_FILE = ''
BIB_ENCODING = 'utf8'

CONFERENCE_LOG = '2017-05-31.log'

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

SLEEP_TIME_RANGE = (0, 5)
SLEEP_ALPHA = 2
SLEEP_BETA = 5
