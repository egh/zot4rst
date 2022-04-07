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
    #Zotero should be open and have an entry by John Doe called Book
    req = urllib.request.Request("http://localhost:23119/zotxt/items?easykey=DoeBook2005")
    f = urllib.request.urlopen(req)