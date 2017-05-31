# !/usr/bin/python
# -*- coding: utf-8 -*-

import re
import shelve

import crawler
import cfg


def export_paper_citations(conference_id):
    url = cfg.URL_CITATION.format(id=conference_id)
    html_content = crawler.get(url)
    ids = crawler.extract_paper_ids(html_content)
    conference_name = crawler.extract_conference_title(html_content)
    for paper_id in ids:
        cfg.log.info(paper_id)
        if paper_id not in db:
            db[paper_id] = crawler.export_citation(paper_id)
    with open(conference_name + '.bib', 'w', encoding='utf-8') as f:
        for paper_id in ids:
            f.write(db[paper_id] + '\n')


def main():
    url = r'http://dl.acm.org/citation.cfm?id=2971648&picked=prox'
    conference_id = re.findall(r'(?<=id=)\d+(?=.*)', str(url))
    if not conference_id:
        # the url is not a valid ACM DL url
        return
    export_paper_citations(conference_id[0])


if __name__ == '__main__':
    with shelve.open('db') as db:
        main()
