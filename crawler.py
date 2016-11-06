# !/usr/bin/python
# -*- coding: utf-8 -*-

from urllib import request, parse, error
import requests
import os
import time
import random
import http
from multiprocessing.dummy import Pool as ThreadPool
from bs4 import BeautifulSoup
import bibtexparser as bp
import cfg

random.seed(time.time())
log = cfg.log


def main():
    for conference_page in cfg.CONFERENCE_PAGE:
        bibs = get_url_citations(conference_page)
        # bibs, errs = get_url_citations(conference_page)
        conference_name = os.path.basename(conference_page)
        name = conference_name.split('.')
        name[-1] = 'bib'
        conference_name = '.'.join(name)

        bib_file = cfg.BIB_FILE if cfg.BIB_FILE else get_valid_file_name(conference_name)
        with open(bib_file, 'w', encoding=cfg.BIB_ENCODING) as f:
            for bib in bibs:
                f.write(bibs[bib])
                f.write('\n')
            f.write(get_group_tree_string(bibs, conference_page))
            # with open(cfg.ERROR_OUTPUT, 'w', encoding=cfg.BIB_ENCODING) as f:
            # for err in errs:
            #         f.write(err)
            #         f.write('\n')


def retry(func):
    def _decorator(url):
        for i in range(1 + cfg.RETRY):
            try:
                return func(url)
            # except (error.HTTPError, error.URLError,
            # ConnectionResetError, http.client.BadStatusLine) as e:
            except Exception as e:
                log.error(e)
                log.info('%s error occurs, retrying...' % url)
                time.sleep(10)

    return _decorator


# def random_proxy(func):
#     def set_proxy(proxy):
#         proxy_handler = request.ProxyHandler({'http': proxy})
#         opener = request.build_opener(proxy_handler)
#         request.install_opener(opener)

#     def _decorator(url):
#         if len(cfg.PROXIES) > 0:
#             r_index = random.randint(0, len(cfg.PROXIES) - 1)
#             set_proxy(cfg.PROXIES[r_index])
#         return func(url)

#     return _decorator


@retry
def urlopen(url):
    # random_proxy
    proxy = None
    if len(cfg.PROXIES) > 0:
        r_index = random.randint(0, len(cfg.PROXIES) - 1)
        while cfg.PROXIES[r_index] in cfg.PROXY_TABOO:
            r_index = random.randint(0, len(cfg.PROXIES) - 1)
        proxy = {'http': cfg.PROXIES[r_index]}
    # without this camouflage, response will return HTTP Error 403 Forbidden
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
    }
    if proxy:
        proxy_handler = request.ProxyHandler(proxy)
        opener = request.build_opener(proxy_handler)
        request.install_opener(opener)
    req = request.Request(url, headers=headers)
    res = request.urlopen(req)
    if res.getcode() != 200 and proxy:
        if proxy['http'] not in cfg.PROXY_TABOO:
            cfg.PROXY_TABOO += [proxy['http']]
            log.info('%d available proxies'
                % (len(cfg.PROXIES) - len(cfg.PROXY_TABOO)))
    return res


def get_citation_id(func):
    def _decorator(url_citation):
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
        t = random.betavariate(cfg.SLEEP_ALPHA, cfg.SLEEP_BETA) \
                * (cfg.SLEEP_TIME_RANGE[1] - cfg.SLEEP_TIME_RANGE[0]) + cfg.SLEEP_TIME_RANGE[0]
        time.sleep(t)
        text = func(citation_id)
        # time.sleep(random.uniform(cfg.SLEEP_TIME_RANGE[0], cfg.SLEEP_TIME_RANGE[1]))
        return text

    return _decorator


@random_sleep
@get_citation_id
def get_citation_text(citation_id):
    log.info(citation_id)
    res = urlopen(cfg.URL_BIBTEX.format(id=citation_id))
    if res:
        soup = BeautifulSoup(res.read())
        if soup.pre:
            bibtex = soup.pre.get_text()
            bib = bp.loads(bibtex)
            bib.entries[0]['abstract'] = get_abstract(citation_id)
            return {citation_id: bp.dumps(bib)}
    return ''


def get_abstract(citation_id):
    abstract = ''
    res = requests.get(cfg.URL_CITATION.format(id=citation_id))
    # res = requests.get('http://dl.acm.org/citation.cfm?doid=1277741.1277774&preflayout=flat')
    log.info(citation_id + ' status - ' + str(res.status_code))
    if res.status_code == 200:
        soup = BeautifulSoup(res.text)
        if soup.find('div', {'class': 'flatbody'}):
            log.info(citation_id + ' - abstract not found')
            if soup.find('div', {'class': 'flatbody'}).find('div'):
                abstract = soup.find('div', {'class': 'flatbody'}).find('div').text
                if '<p>' in abstract:
                    abstract = abstract.replace('<p>', '').replace('</p>', '\n')
                else:
                    abstract
                log.info('fetched abstract - ' + citation_id)
    return abstract


def get_url_citations(url_conference):
    # the citation details are appended by javascript
    # because I'm lazy, the user has to use the browser run javascript,
    # and save the html file on the local hard disk
    # url_conference = 'http://dl.acm.org/citation.cfm?id=2600428&picked=prox&CFID=586594267&CFTOKEN=76400862'
    # res = urlopen(url_conference)
    # soup = BeautifulSoup(res.read())
    # citations = {}
    # error_urls = []

    with open(url_conference, encoding='utf-8') as f:
        soup = BeautifulSoup(f)
        links = soup.find(class_='text12').find_all('a')
        urls = map(lambda link: link['href'], links)
        url_citations = filter(lambda url: 'citation.cfm' in url, urls)
        url_citations = list(url_citations)

    log.info('%d citations found in %s.' % (len(url_citations), url_conference))

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

    log.info('%d of %d citations fetched.' % (len(citations), len(url_citations)))
    return citations  # , error_urls


def get_valid_file_name(file_name):
    for c in cfg.INVALID_CHARS:
        file_name = file_name.replace(c, ' ')
    return file_name


def get_jabref_comment_string(func):
    def _decorator(bibs, conference_page):
        return '@comment{jabref-meta: groupsversion:3;}\n' \
               + '@comment{jabref-meta: groupstree:\n%s}' % func(bibs, conference_page)

    return _decorator


@get_jabref_comment_string
def get_group_tree_string(bibs, conference_page):
    def get_id_key(bibs):
        citation_id_key = {}
        for citation_id in bibs:
            citation_id_key[citation_id] = bibs[citation_id].strip() \
                .split('\n')[0].split('{')[-1].split(',')[0]
        return citation_id_key

    def get_groups(url_conference):
        groups = {'': [], }
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

    groups = get_groups(conference_page)
    id_key = get_id_key(bibs)

    def get_group_string(group):
        group_keys = map(lambda citation_id: id_key[citation_id]
                         if citation_id in id_key else '', groups[group])
        group_keys = filter(lambda e: e, group_keys)
        if group:
            return '1 ExplicitGroup:%s\\;0\\;%s\\;;' % (group, '\\;'.join(group_keys))
        else:
            return '0 AllEntriesGroup:\\;0\\;%s\\;;' % '\\;'.join(group_keys)

    group_tree = map(get_group_string, groups.keys())
    return '\n'.join(group_tree)


main()
