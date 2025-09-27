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
import re
import xciterst


class CitationInfo(object):
    """Class to hold information about a citation for passing to
    citeproc."""

    def __init__(
        self,
        citekey,
        label=None,
        locator=None,
        suppress_author=False,
        prefix=None,
        suffix=None,
        author_only=False,
        theid=None,
    ):
        self.citekey = citekey
        self.label = label
        self.locator = locator
        self.suppress_author = suppress_author
        self.prefix = prefix
        if self.prefix:
            self.prefix = re.sub(r"\s+,", ",", self.prefix)
        self.suffix = suffix
        if self.suffix:
            self.suffix = re.sub(r"\s+,", ",", self.suffix)
        self.author_only = author_only
        self.citeid = theid

    def __str__(self):
        if self.suppress_author:
            suppress_str = "-"
        else:
            suppress_str = ""

        return "%s %s%s(%s) %s" % (
            self.prefix,
            suppress_str,
            self.citekey,
            self.locator,
            self.suffix,
        )

    def __repr__(self):
        return "CitationInfo(%s)" % (
            repr(
                {
                    "citekey": self.citekey,
                    "label": self.label,
                    "locator": self.locator,
                    "suppress_author": self.suppress_author,
                    "prefix": self.prefix,
                    "suffix": self.suffix,
                    "author_only": self.author_only,
                    "id": self.citeid,
                }
            )
        )

    def __eq__(self, other):
        return (
            isinstance(other, CitationInfo)
            and (self.citekey == other.citekey)
            and (self.label == other.label)
            and (self.locator == other.locator)
            and (self.suppress_author == other.suppress_author)
            and (self.prefix == other.prefix)
            and (self.suffix == other.suffix)
            and (self.author_only == other.author_only)
        )


class CitationCluster(object):
    """Class to hold a cluster of citations, with information about
    them suitable for submission to citeproc."""

    def __init__(self, citations):
        self.citations = citations
        self.note_index = 0
        self.index = 0

    def __eq__(self, other):
        return (
            isinstance(other, CitationCluster)
            and (self.citations == other.citations)
            and (self.note_index == other.note_index)
            and (self.index == other.index)
        )

    def __repr__(self):
        return "CitationCluster(%s)" % (repr(self.citations))
