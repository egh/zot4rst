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
import json
from xciterst.citations import CitationInfo, CitationCluster


class ZoteroJSONEncoder(json.JSONEncoder):
    """An encoder for our JSON objects."""

    def default(self, obj):
        if isinstance(obj, CitationInfo):
            retval = {}
            if obj.citekey:
                retval["easyKey"] = obj.citekey
            elif obj.citeid:
                retval["id"] = obj.citeid
            if obj.prefix:
                retval["prefix"] = "%s " % (
                    obj.prefix
                )  # ensure spaces in prefix, suffix
            if obj.suffix:
                retval["suffix"] = " %s" % (obj.suffix)
            if obj.label:
                retval["label"] = obj.label
            if obj.locator:
                retval["locator"] = obj.locator
            if obj.suppress_author:
                retval["suppress-author"] = obj.suppress_author
            if obj.author_only:
                retval["author-only"] = obj.author_only
            return retval
        elif isinstance(obj, CitationCluster):
            return {
                "citationItems": obj.citations,
                "properties": {"index": obj.index, "noteIndex": obj.note_index},
            }
        else:
            return super(ZoteroJSONEncoder, self).default(self, obj)
