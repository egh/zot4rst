#!/usr/bin/env python
from __future__ import absolute_import
from setuptools import setup

setup(
    name="zot4rst",
    version="0.3.0",
    description="Zotero for reStructuredText",
    author="Erik Hetzner",
    author_email="egh@e6h.org",
    url="http://bitbucket.org/egh/zot4rst/",
    packages=["zot4rst", "xciterst"],
    install_requires=[
        "rst2pdf>=0.93.dev_r0",
        "beautifulsoup4",
        "docutils>=0.9",
        "pyparsing>=1.5.7",
        "pyzotero>=0.9.9",
    ],
    scripts=[
        "bin/zotcite",
        "bin/zrst2html",
        "bin/zrst2odt",
        "bin/zrst2pdf",
        "bin/zrst2pseudoxml",
        "bin/zrst2rst",
        "bin/zupdatekeymap",
    ],
    extras_require={
        "PDF": "rst2pdf>=0.93.dev_r0",
    },
    entry_points={"console_scripts": ["rst2pdf = zot4rst.zrst2pdf:run [PDF]"]},
)
