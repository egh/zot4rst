from __future__ import absolute_import
from pelican import signals
import zot4rst
import zot4rst.register
import xciterst


def register():
    signals.article_generator_init.connect(setup_zotero)
    signals.article_generator_preread.connect(article_setup_zotero)


def setup_zotero(generator):
    zot4rst.init(
        generator.settings.get("CITATION_STYLE", zot4rst.DEFAULT_CITATION_STYLE)
    )


def article_setup_zotero(generator):
    zot4rst.init(
        generator.settings.get("CITATION_STYLE", zot4rst.DEFAULT_CITATION_STYLE)
    )
