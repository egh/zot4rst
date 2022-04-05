import urllib.request
import json


data = {"styleId": "chicago-author-date",
  "citationGroups": [
    {
      "citationItems": [
        {
          "easyKey": "DoeBook2005",
          "author-only": True
        }
      ],
      "properties": {
        "index": 0,
        "noteIndex": 0
      }
    },
    {
      "citationItems": [
        {
          "easyKey": "DoeBook2005",
          "suppress-author": True
        }
      ],
      "properties": {
        "index": 1,
        "noteIndex": 0
      }
    }
  ]
}

print(json.dumps(data))
req = urllib.request.Request("http://localhost:23119/zotxt/bibliography", json.dumps(data).encode("ascii"), {'Content-Type': 'application/json'})
f = urllib.request.urlopen(req)

def find_item(item: str):
    req = urllib.request.Request("http://localhost:23119/zotxt/search", str({"q":item}).encode("ascii"),method="GET")
    print(req.data, req.headers, req.full_url)
    return urllib.request.urlopen(req)

# print(find_item("Jon Doe"))

def test_get_item():
    req = urllib.request.Request("http://localhost:23119/zotxt/items", str({"easykey":"DoeBook2005"}).encode("ascii"), method="GET")
    urllib.request.urlopen(req)

