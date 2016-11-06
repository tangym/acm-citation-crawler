acm-citation-crawler
====================

### Introduction

This program downloads all the bibtex citations from an ACM conference url.


### How to use
Follow these steps:

- Find a ACM conference proceedings page, for example [RecSys 14'](http://dl.acm.org/citation.cfm?id=2645710&preflayout=flat#abstract). 
Notice the page should switch to **flat view** and contains the table of contents (links to each paper).

- Hit `Ctrl-S` to save the conference page in the directory where the program locates.

- Copy the **whole** file name of the saved web page, including the extension `.html`, and paste into `pages.txt`, one file name per line.
The program will automatically parse each web page indicated in `pages.txt` and extract bibtex citations to corresponding files.

- (Maybe optional) Find some free proxies and create `proxy.txt` file in the following format, one proxy per line:
```
<protocol>://<ip>:<port>
```
For example, the content of `proxy.txt` file can be
```
http://1.2.3.4:80
https://5.6.7.8:90
```

- Run command prompt and run `python crawler.py`. If it warns some package is not installed, maybe you can try `pip install -r requirements.txt`.

The program will take a while to finish collecting all the bibtex citations, because ACM library limits the connection speed from the same IP.
The program may also fail crawling some citations sometimes, and it will not out put the fail citations' information.
So if it fails, just try again util it successes. :)


### BibTex format citation

#### JabRef group comments gramma

```tex
@comment{jabref-meta: groupsversion:3;}

@comment{jabref-meta: groupstree:
0 AllEntriesGroup:;
1 ExplicitGroup:1\;0\;b\;;
2 ExplicitGroup:1.1\;0\;a\;;
2 ExplicitGroup:c\;0\;;
}
```

[depth] ExplicitGroup:[group name]\;0\;[bibtex key1]\;[bibtex key2]\;;

The parent node is indicated by the nearest previous line which depth is less than the current node.

Once you have a `.bib` citation file, open it with [JabRef](http://jabref.sourceforge.net/), and browse the citations.
There's a set of [extensions](http://www.lhnr.de/ext/) which can help to download all pdfs automatically.


-- EOF --
