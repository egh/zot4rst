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

import urllib.request
import json


data = {
    "styleId": "chicago-author-date",
    "citationGroups": [
        {
            "citationItems": [{"easyKey": "DoeBook2005", "author-only": True}],
            "properties": {"index": 0, "noteIndex": 0},
        },
        {
            "citationItems": [{"easyKey": "DoeBook2005", "suppress-author": True}],
            "properties": {"index": 1, "noteIndex": 0},
        },
    ],
}

print(json.dumps(data))
req = urllib.request.Request(
    "http://localhost:23119/zotxt/bibliography",
    json.dumps(data).encode("ascii"),
    {"Content-Type": "application/json"},
)
f = urllib.request.urlopen(req)


def test_get_item():
    # Zotero should be open and have an entry by John Doe called Book
    req = urllib.request.Request(
        "http://localhost:23119/zotxt/items?easykey=DoeBook2005"
    )
    f = urllib.request.urlopen(req)
