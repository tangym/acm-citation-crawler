acm-citation-crawler
====================

### Introduction

downloads all the bibtex citations of a conference from an ACM DL url

The program may fail crawling some citations sometimes, and it will not out put the fail citations' information.
So if it fails, just try again util it successes. :)

Open the output bibtex with [JabRef](http://jabref.sourceforge.net/), and browse the citations.
There's a set of [extensions](http://www.lhnr.de/ext/) which can help to download all pdfs automatically.

### JabRef group comments gramma

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

the parent node is indicated by the nearest previous line which depth is less than the current node.

-- EOF --
