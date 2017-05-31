# !/usr/bin/python
# -*- coding: utf-8 -*-

import platform
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import bibtexparser

import cfg


if platform.system() == 'Windows':
    PHANTOMJS_PATH = './phantomjs.exe'
else:
    PHANTOMJS_PATH = './phantomjs'

browser = webdriver.PhantomJS(PHANTOMJS_PATH)


url = r'http://dl.acm.org/citation.cfm?id=2750858&preflayout=flat'


def extract_paper_ids(html):
    soup = BeautifulSoup(html, "html.parser")
    links = soup.findAll('a')
    links = filter(lambda link: 'citation.cfm' in str(link), links)
    ids = map(lambda link: re.findall(r'(?<=id=)\d+(?=.*)', str(link)), links)
    ids = map(lambda e: e[0], filter(lambda e: e, ids))
    return set(ids)


def get(url, execute_js=True, proxy=''):
    if not execute_js:
        # without this camouflage, response will return 403 Forbidden
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1;'
                          'en-US; rv:1.9.1.6) Gecko/20091201 '
                          'Firefox/3.5.6'
        }
        if proxy:
            try:
                r = requests.get(url, headers=headers, proxies={'http': proxy})
            except requests.exceptions.ProxyError as pe:
                # The local network does not support using proxies
                r = requests.get(url, headers=headers)
        else:
            r = requests.get(url, headers=headers)
        return r.text
    else:
        browser.get(url)
        return browser.page_source


def export_citation(paper_id):
    # log.info(citation_id)
    html_content = get(cfg.URL_BIBTEX.format(id=paper_id))
    soup = BeautifulSoup(html_content)
    if soup.pre:
        bibtex = soup.pre.get_text()
        bib = bibtexparser.loads(bibtex)
        bib.entries[0]['abstract'] = get_abstract(paper_id)
        return bibtexparser.dumps(bib)
    return ''


def get_abstract(paper_id):
    abstract = ''
    html_content = get(cfg.URL_CITATION.format(id=paper_id))
    soup = BeautifulSoup(html_content)
    if soup.find('div', {'class': 'flatbody'}):
        if soup.find('div', {'class': 'flatbody'}).find('div'):
            abstract = soup.find('div', {'class': 'flatbody'}).find('div').text
            if '<p>' in abstract:
                abstract = abstract.replace('<p>', '').replace('</p>', '\n')
            else:
                abstract
    return abstract
