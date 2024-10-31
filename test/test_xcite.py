from __future__ import absolute_import
from xciterst.parser import CiteParser
from xciterst.citations import CitationInfo, CitationCluster
import random
import string
import unittest
from six.moves import range


class TestXciteParserp(unittest.TestCase):
    def setUp(self):
        self.parser = CiteParser()

    def parse(self, parse_string):
        return self.parser.parse(parse_string)

    def mk_citekey(self):
        """Make crazy cite keys to stress test parser."""
        start_chars = string.digits + string.ascii_letters + "_"
        chars = start_chars + ":.#$%&-+?<>~/"
        return random.choice(start_chars) + "".join(
            random.choice(chars) for _ in range(1000)
        )

    # @item1
    def test_parse_1(self):
        item1 = self.mk_citekey()
        [first_cluster, second_cluster] = self.parse("@%s" % (item1))
        self.assertEqual(
            first_cluster,
            CitationCluster([CitationInfo(citekey=item1, author_only=True)]),
        )
        self.assertEqual(
            second_cluster,
            CitationCluster([CitationInfo(citekey=item1, suppress_author=True)]),
        )

    # @item1, [p. 30]
    def test_parse_2(self):
        item1 = self.mk_citekey()
        [first_cluster, second_cluster] = self.parse("@%s [p. 30]" % (item1))
        self.assertEqual(
            first_cluster,
            CitationCluster([CitationInfo(citekey=item1, author_only=True)]),
        )
        self.assertEqual(
            second_cluster,
            CitationCluster(
                [CitationInfo(citekey=item1, suppress_author=True, locator="p. 30")]
            ),
        )

    # @item1 [p. 30, with suffix]
    # XXX - is this parse right?
    def test_parse_3(self):
        item1 = self.mk_citekey()
        [first_cluster, second_cluster] = self.parse(
            "@%s [p. 30, with suffix]" % (item1)
        )
        self.assertEqual(
            first_cluster,
            CitationCluster([CitationInfo(citekey=item1, author_only=True)]),
        )
        self.assertEqual(
            second_cluster,
            CitationCluster(
                [
                    CitationInfo(
                        citekey=item1,
                        suppress_author=True,
                        locator="p. 30,",
                        suffix="with suffix",
                    )
                ]
            ),
        )

    # @item1 [-@item2 p. 30; see also @item3]
    def test_parse_4(self):
        item1 = self.mk_citekey()
        item2 = self.mk_citekey()
        item3 = self.mk_citekey()
        [first_cluster, second_cluster] = self.parse(
            "@%s [-@%s p. 30; see also @%s]" % (item1, item2, item3)
        )
        self.assertEqual(
            first_cluster,
            CitationCluster([CitationInfo(citekey=item1, author_only=True)]),
        )
        self.assertEqual(
            second_cluster,
            CitationCluster(
                [
                    CitationInfo(citekey=item1, suppress_author=True),
                    CitationInfo(citekey=item2, suppress_author=True, locator="p. 30"),
                    CitationInfo(citekey=item3, prefix="see also"),
                ]
            ),
        )

    # [see @item1 p. 34-35; also @item3 chap. 3]
    def test_parse_5(self):
        item1 = self.mk_citekey()
        item3 = self.mk_citekey()
        [first_cluster, second_cluster] = self.parse(
            "[see @%s p. 34-35; also @%s chap. 3]" % (item1, item3)
        )
        self.assertEqual(first_cluster, None)
        self.assertEqual(
            second_cluster,
            CitationCluster(
                [
                    CitationInfo(citekey=item1, prefix="see", locator="p. 34-35"),
                    CitationInfo(citekey=item3, prefix="also", locator="chap. 3"),
                ]
            ),
        )

    # [see @item1 p. 34-35]
    def test_parse_6(self):
        item1 = self.mk_citekey()
        [first_cluster, second_cluster] = self.parse("[see @%s p. 34-35]" % (item1))
        self.assertEqual(first_cluster, None)
        self.assertEqual(
            second_cluster,
            CitationCluster(
                [CitationInfo(citekey=item1, prefix="see", locator="p. 34-35")]
            ),
        )

    # [@item1 pp. 33, 35-37 and nowhere else]
    def test_parse_7(self):
        item1 = self.mk_citekey()
        [first_cluster, second_cluster] = self.parse(
            "[@%s pp. 33, 35-37 and nowhere else]" % (item1)
        )
        self.assertEqual(first_cluster, None)
        self.assertEqual(
            second_cluster,
            CitationCluster(
                [
                    CitationInfo(
                        citekey=item1,
                        locator="pp. 33, 35-37",
                        suffix="and nowhere else",
                    )
                ]
            ),
        )

    # [@item1 and nowhere else]
    def test_parse_8(self):
        item1 = self.mk_citekey()
        [first_cluster, second_cluster] = self.parse("[@%s and nowhere else]" % (item1))
        self.assertEqual(first_cluster, None)
        self.assertEqual(
            second_cluster,
            CitationCluster([CitationInfo(citekey=item1, suffix="and nowhere else")]),
        )

    # XXX BROKEN
    # [*see* @item1 p. **32**]
    # def test_parse_9(self):
    #    [first_cluster, second_cluster] = self.parse("[*see* @item1 p. **32**]")
    #    self.assertEqual(first_cluster, None)
    #    self.assertEqual(second_cluster,
    #                     CitationCluster([CitationInfo(citekey="item1",
    #                                   prefix="<i>see</i>",
    #                                   locator="p. <b>32</b>")]))

    # [@item3]
    def test_parse_10(self):
        item3 = self.mk_citekey()
        [first_cluster, second_cluster] = self.parse("[@%s]" % (item3))
        self.assertEqual(first_cluster, None)
        self.assertEqual(second_cluster, CitationCluster([CitationInfo(citekey=item3)]))

    # [see @item2 chap. 3; @item3; @item1]
    def test_parse_11(self):
        item1 = self.mk_citekey()
        item2 = self.mk_citekey()
        item3 = self.mk_citekey()
        [first_cluster, second_cluster] = self.parse(
            "[see @%s chap. 3; @%s; @%s]" % (item2, item3, item1)
        )
        self.assertEqual(first_cluster, None)
        self.assertEqual(
            second_cluster,
            CitationCluster(
                [
                    CitationInfo(citekey=item2, prefix="see", locator="chap. 3"),
                    CitationInfo(citekey=item3),
                    CitationInfo(citekey=item1),
                ]
            ),
        )

    # [-@item1]
    def test_parse_12(self):
        item1 = self.mk_citekey()
        [first_cluster, second_cluster] = self.parse("[-@%s]" % (item1))
        self.assertEqual(first_cluster, None)
        self.assertEqual(
            second_cluster,
            CitationCluster([CitationInfo(citekey=item1, suppress_author=True)]),
        )

    # [-@item2 p. 44]
    def test_parse_13(self):
        item2 = self.mk_citekey()
        [first_cluster, second_cluster] = self.parse("[-@%s p. 44]" % (item2))
        self.assertEqual(first_cluster, None)
        self.assertEqual(
            second_cluster,
            CitationCluster(
                [CitationInfo(citekey=item2, suppress_author=True, locator="p. 44")]
            ),
        )

    # [@item1, p. 30]
    def test_parse_14(self):
        item1 = self.mk_citekey()
        [first_cluster, second_cluster] = self.parse("[@%s, p. 30]" % (item1))
        self.assertEqual(first_cluster, None)
        self.assertEqual(
            second_cluster,
            CitationCluster([CitationInfo(citekey=item1, locator="p. 30")]),
        )

    def test_parse_unicode_quotes(self):
        UNICODE_PUNCT_FINAL = (
            "\u00BB\u2019\u201D\u203A\u2E03\u2E05\u2E0A\u2E0D\u2E1D\u2E21"
        )
        UNICODE_PUNCT_INITIAL = (
            "\u00AB\u2018\u201B\u201C\u201F\u2039\u2E02\u2E04\u2E09\u2E0C\u2E1C\u2E20"
        )
        item1 = self.mk_citekey()
        suffix = "%sfoo%s" % (
            random.choice(UNICODE_PUNCT_INITIAL),
            random.choice(UNICODE_PUNCT_FINAL),
        )

        [first_cluster, second_cluster] = self.parse("[@%s %s]" % (item1, suffix))
        self.assertEqual(first_cluster, None)
        self.assertEqual(
            second_cluster,
            CitationCluster([CitationInfo(citekey=item1, suffix=suffix)]),
        )


if __name__ == "__main__":
    unittest.main()
