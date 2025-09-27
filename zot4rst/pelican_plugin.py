# Copyright (C) 2010-2025 Erik Hetzner
#
# This file is part of zot4rst.
#
# zot4rst is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# zot4rst is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with zot4rst. If not, see
# <https://www.gnu.org/licenses/>.

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
