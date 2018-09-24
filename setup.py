#!/usr/bin/env python
from setuptools import setup

setup(name             = 'zot4rst',
      version          = '0.3.0',
      description      = 'Zotero for reStructuredText',
      author           = 'Erik Hetzner',
      author_email     = 'egh@e6h.org',
      url              = 'http://bitbucket.org/egh/zot4rst/',
      packages         = ['zot4rst',
                          'xciterst'],
      install_requires = ["beautifulsoup4",
                          "docutils>=0.9",
                          "rst2pdf>=0.93.dev_r0",
                          "pyparsing==1.5.7",
                          "pyzotero>=0.9.9"],
      scripts          = ['bin/zotcite',
                          'bin/zrst2html',
                          'bin/zrst2odt', 
                          'bin/zrst2pdf',
                          'bin/zrst2pseudoxml',
                          'bin/zrst2rst',
                          'bin/zupdatekeymap']
      )
