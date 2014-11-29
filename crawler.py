# !/usr/bin/python
# -*- coding: utf-8 -*-

from urllib import request, parse, error
# import requests
import os
import time
import random
import logging
from bs4 import BeautifulSoup
import cfg

random.seed(time.time())
log = cfg.log

def main():
    bibs, errs = get_url_citations(cfg.CONFERENCE_PAGE)
    conference_name = os.path.basename(cfg.CONFERENCE_PAGE)
    conference_name.split('.')[-1] = 'bib'
    conference_name = '.'.join(conference_name)

    bib_file = cfg.BIB_FILE if not cfg.BIB_FILE else get_valid_file_name()
    with open(bib_file, 'w', encoding=cfg.BIB_ENCODING) as f:
        for bib in bibs:
            f.write(bib)
            f.write('\n')
    with open(cfg.ERROR_OUTPUT, 'w', encoding=cfg.BIB_ENCODING) as f:
        for err in errs:
            f.write(err)
            f.write('\n')


def retry(func):
    def _decorator(url):
        for i in range(1 + cfg.RETRY):
            try:
                return func(url)
            except error.HTTPError as e:
                # logging.error(e)
                # logging.info('retrying...')
                print('error occurs, retrying...')
                time.sleep(10)
    return _decorator



def random_proxy(func):
    def set_proxy(proxy):
        proxy_handler = request.ProxyHandler({'http': proxy})
        opener = request.build_opener(proxy_handler)
        request.install_opener(opener)
    def _decorator(url):
        if len(cfg.PROXIES) > 0:
            r_index = random.randint(0, len(cfg.PROXIES)-1)
            set_proxy(cfg.PROXIES[r_index])
        return func(url)
    return _decorator


@retry
@random_proxy
def urlopen(url):
    # without this camouflage, response will return HTTP Error 403 Forbidden
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
    }
    req = request.Request(url, headers=headers)
    res = request.urlopen(req)
    return res


def get_citation_id(func):
    def _decorator(url_citation):
        # url_citation = 'citation.cfm?id=2617557&CFID=586594267&CFTOKEN=76400862'
        url_citation_parsed = parse.urlparse(url_citation)
        params = parse.parse_qs(url_citation_parsed.query)

        if 'id' in params:
            return func(params['id'][0])
        else:
            # TODO: throw exception?
            pass
    return _decorator


@get_citation_id
def get_citation_text(citation_id):
    res = urlopen(cfg.URL_BIBTEX.format(id=citation_id))
    if res:
        soup = BeautifulSoup(res.read())
        if soup.pre:
            return soup.pre.get_text()
    return ''


def get_url_citations(url_conference):
    # the citation details are appended by javascript
    # because I'm lazy, the user has to use the browser run javascript,
    # and save the html file on the local hard disk
    # url_conference = 'http://dl.acm.org/citation.cfm?id=2600428&picked=prox&CFID=586594267&CFTOKEN=76400862'
    # res = urlopen(url_conference)
    # soup = BeautifulSoup(res.read())
    citations = []
    error_urls = []

    with open(url_conference, encoding='utf-8') as f:
        soup = BeautifulSoup(f)
        links = soup.find(class_='text12').find_all('a')
        urls = map(lambda link: link['href'], links)
        url_citations = filter(lambda url: 'citation.cfm' in url, urls)
        url_citations = list(url_citations)

        print('%d citations found.' % len(url_citations))
        # log.info('%d citations found.' % len(url_citations))
        for i in url_citations:
            print(i)
            # log.info(i)
            citation_text = get_citation_text(i)
            if citation_text:
                citations += [citation_text]
            else:
                error_urls += [i]
            time.sleep(random.uniform(cfg.SLEEP_TIME_RANGE[0], cfg.SLEEP_TIME_RANGE[1]))
    print(len(citations))
    return citations, error_urls


def get_valid_file_name(file_name):
    for c in cfg.INVALID_CHARS:
        file_name = file_name.replace(c, ' ')
    return file_name

main()
