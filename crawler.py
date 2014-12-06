# !/usr/bin/python
# -*- coding: utf-8 -*-

from urllib import request, parse, error
# import requests
import os
import time
import random
import logging
from multiprocessing.dummy import Pool as ThreadPool
from bs4 import BeautifulSoup
import cfg

random.seed(time.time())
log = cfg.log

def main():
    bibs = get_url_citations(cfg.CONFERENCE_PAGE)
    # bibs, errs = get_url_citations(cfg.CONFERENCE_PAGE)
    conference_name = os.path.basename(cfg.CONFERENCE_PAGE)
    name = conference_name.split('.')
    name[-1] = 'bib'
    conference_name = '.'.join(name)

    bib_file = cfg.BIB_FILE if cfg.BIB_FILE else get_valid_file_name(conference_name)
    with open(bib_file, 'w', encoding=cfg.BIB_ENCODING) as f:
        for bib in bibs:
            f.write(bibs[bib])
            f.write('\n')
        f.write(get_group_tree_string(bibs))
    # with open(cfg.ERROR_OUTPUT, 'w', encoding=cfg.BIB_ENCODING) as f:
    #     for err in errs:
    #         f.write(err)
    #         f.write('\n')


def retry(func):
    def _decorator(url):
        for i in range(1 + cfg.RETRY):
            try:
                return func(url)
            except (error.HTTPError, error.URLError, ConnectionResetError) as e:
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


def random_sleep(func):
    def _decorator(citation_id):
        text = func(citation_id)
        time.sleep(random.uniform(cfg.SLEEP_TIME_RANGE[0], cfg.SLEEP_TIME_RANGE[1]))
        return text
    return _decorator


@random_sleep
@get_citation_id
def get_citation_text(citation_id):
    print(citation_id)
    res = urlopen(cfg.URL_BIBTEX.format(id=citation_id))
    if res:
        soup = BeautifulSoup(res.read())
        if soup.pre:
            return {citation_id: soup.pre.get_text()}
    return ''


def get_url_citations(url_conference):
    # the citation details are appended by javascript
    # because I'm lazy, the user has to use the browser run javascript,
    # and save the html file on the local hard disk
    # url_conference = 'http://dl.acm.org/citation.cfm?id=2600428&picked=prox&CFID=586594267&CFTOKEN=76400862'
    # res = urlopen(url_conference)
    # soup = BeautifulSoup(res.read())
    citations = {}
    error_urls = []

    with open(url_conference, encoding='utf-8') as f:
        soup = BeautifulSoup(f)
        links = soup.find(class_='text12').find_all('a')
        urls = map(lambda link: link['href'], links)
        url_citations = filter(lambda url: 'citation.cfm' in url, urls)
        url_citations = list(url_citations)

    print('%d citations found.' % len(url_citations))
    # log.info('%d citations found.' % len(url_citations))

    pool = ThreadPool(cfg.WORKER)
    citations = pool.map(get_citation_text, url_citations)
    pool.close()
    pool.join()

    temp_citations = {}
    for citation in citations:
        if citation:
            for key in citation:
                temp_citations[key] = citation[key]
    citations = temp_citations

    print('%d of %d citations fetched.' % (len(citations), len(url_citations)))
    return citations  # , error_urls


def get_valid_file_name(file_name):
    for c in cfg.INVALID_CHARS:
        file_name = file_name.replace(c, ' ')
    return file_name


def get_jabref_comment_string(func):
    def _decorator(bibs):
        return '@comment{jabref-meta: groupsversion:3;}\n' \
                + '@comment{jabref-meta: groupstree:\n%s}' % func(bibs)
    return _decorator


@get_jabref_comment_string
def get_group_tree_string(bibs):
    def get_id_key(bibs):
        citation_id_key = {}
        for citation_id in bibs:
            citation_id_key[citation_id] = bibs[citation_id].strip()  \
                .split('\n')[0].split('{')[-1].split(',')[0]
        return citation_id_key


    def get_groups(url_conference):
        groups = {'':[],}
        with open(url_conference, encoding='utf-8') as f:
            soup = BeautifulSoup(f)
            current_session = ''
            # for i in soup.find(class_='text12').find_all('td'):
            for i in soup.find_all('td'):
                if 'SESSION' in i.get_text():
                    current_session = i.get_text()
                    groups[current_session] = []
                elif i.find('a'):
                    url = i.find('a')['href']
                    if 'citation.cfm' in url:
                        if current_session:
                            groups[current_session] += [get_citation_id(lambda e: e)(url)]
        return groups

    groups = get_groups(cfg.CONFERENCE_PAGE)
    id_key = get_id_key(bibs)

    def get_group_string(group):
        group_keys = map(lambda citation_id: id_key[citation_id] \
            if citation_id in id_key else '', groups[group])
        group_keys = filter(lambda e: e, group_keys)
        if group:
            return '1 ExplicitGroup:%s\\;0\\;%s\\;;' % (group, '\\;'.join(group_keys))
        else:
            return '0 AllEntriesGroup:\\;0\\;%s\\;;' % '\\;'.join(group_keys)

    group_tree = map(get_group_string, groups.keys())
    return '\n'.join(group_tree)

main()

