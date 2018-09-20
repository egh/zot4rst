from zot4rst.jsonencoder import ZoteroJSONEncoder
from xciterst.citations import CitationCluster, CitationInfo
import unittest2

class TestJsonencoder(unittest2.TestCase):
    def setUp(self):
        self.encoder = ZoteroJSONEncoder()
        self.citation = CitationInfo(citekey="foo")
        self.citation.id = "foo"
        citation2 = CitationInfo(citekey="bar")
        citation2.id = "bar"
        self.citation_cluster = CitationCluster([self.citation, citation2])

    def test_basic(self):
        json = self.encoder.encode(self.citation)
        self.assertEqual(json, '{"easyKey": "foo"}')

    def test_suppress_author(self):
        self.citation.suppress_author = True
        json = self.encoder.encode(self.citation)
        self.assertEqual(json, '{"easyKey": "foo", "suppress-author": true}')

    def test_author_only(self):
        self.citation.author_only = True
        json = self.encoder.encode(self.citation)
        self.assertEqual(json, '{"easyKey": "foo", "author-only": true}')

    def test_all(self):
        self.citation.prefix = "see"
        self.citation.suffix = "and nowhere else",
        self.citation.locator = "p. 10"
        json = self.encoder.encode(self.citation)
        self.assertEqual(json, '{"easyKey": "foo", "locator": "p. 10", "prefix": "see ", "suffix": " and nowhere else"}')

    def test_cluster(self):
        self.citation_cluster.index = 2
        self.citation_cluster.note_index = 3
        json = self.encoder.encode(self.citation_cluster)
        self.assertEqual(json, '{"citationItems": [{"easyKey": "foo"}, {"easyKey": "bar"}], "properties": {"index": 2, "noteIndex": 3}}')
