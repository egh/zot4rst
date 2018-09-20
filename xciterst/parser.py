from __future__ import absolute_import
import re
import sys
from pyparsing import Group, OneOrMore, Optional, Regex, White, Word, ZeroOrMore, ParseException
from xciterst.citations import CitationInfo, CitationCluster

class CiteParser(object):
    class Base():
        def __init__(self, name, content):
            self.content = content
            self.name = name

        def __str__(self):
            if type(self.content) == list:
                return "%s(%s)"%(self.name, ", ".join([ str(c) for c in self.content]))
            else:
                return "%s(%s)"%(self.name, self.content)

    class Locator(Base):
        def __init__(self, content):
            CiteParser.Base.__init__(self, "Locator", content)

    class Suffix(Base):
        def __init__(self, content):
            CiteParser.Base.__init__(self, "Suffix", content)

    class Prefix(Base):
        def __init__(self, content):
            CiteParser.Base.__init__(self, "Prefix", content)

    class CiteKey(Base):
        def __init__(self, toks):
            self.suppress_author = False
            if len(toks) == 3:
                self.suppress_author = True
            self.citekey = toks[-1]
            CiteParser.Base.__init__(self, "CiteKey", self.citekey)

    class FullCite(Base):
        def __init__(self, toks):
            CiteParser.Base.__init__(self, "FullCite", toks.asList())

    class ShortCite(Base):
        def __init__(self, toks):
            self.suppress_author = False
            if len(toks) == 3:
                self.suppress_author = True
            self.citekey = toks[-1]
            CiteParser.Base.__init__(self, "ShortCite", self.citekey)

    class ShortCiteExtra(Base):
        def __init__(self, toks):
            CiteParser.Base.__init__(self, "ShortCiteExtra", toks.asList())

    def _results2cites(self, pieces, cites=None, current_cite=None):
        if cites is None: cites = [None, CitationCluster([])]
        prefix = None
        for piece in pieces:
            if isinstance(piece, CiteParser.ShortCite):
                # actually 2 cites, first author-only, then suppress-author
                first = CitationInfo(citekey=piece.citekey,
                                     author_only=True)
                current_cite = CitationInfo(citekey=piece.citekey,
                                            suppress_author=True)
                cites[0] = CitationCluster([first])
                cites[1].citations.append(current_cite)
            elif isinstance(piece, CiteParser.CiteKey):
                current_cite = CitationInfo(citekey=piece.citekey,
                                            suppress_author=piece.suppress_author,
                                            prefix=prefix)
                cites[1].citations.append(current_cite)
            elif isinstance(piece, CiteParser.Prefix):
                prefix = piece.content
            elif isinstance(piece, CiteParser.Locator):
                current_cite.locator = piece.content
            elif isinstance(piece, CiteParser.Suffix):
                current_cite.suffix = piece.content
            elif isinstance(piece, CiteParser.ShortCiteExtra):
                self._results2cites(piece.content, cites, current_cite)
            elif isinstance(piece, CiteParser.FullCite):
                self._results2cites(piece.content, cites)
        return cites

    def parse(self, what):
        UNICODE_PUNCT_FINAL=ur'\u00BB\u2019\u201D\u203A\u2E03\u2E05\u2E0A\u2E0D\u2E1D\u2E21'
        UNICODE_PUNCT_INITIAL=ur'\u00AB\u2018\u201B\u201C\u201F\u2039\u2E02\u2E04\u2E09\u2E0C\u2E1CU+2E20'
        WORD_CHAR_RE = r'[\w.,\'\"\(\)</>%s%s-]'%(UNICODE_PUNCT_INITIAL, UNICODE_PUNCT_FINAL)
        CITEKEY_RE = r'\w[\w\(:.#\$%&+?<>~/\)-]+'
        greedyToken = Regex(r'%s+'%(WORD_CHAR_RE))
        wordWithDigits = Regex(r'%s*[0-9]%s*'%(WORD_CHAR_RE, WORD_CHAR_RE))

        # translate embedded emph & strong RST to HTML
        emText = '*' + OneOrMore(greedyToken) + '*'
        emText.setParseAction(lambda s,l,t:
                                  "<i>%s</i>"%(" ".join(t[1:-1])))
        strongText = '**' + OneOrMore(greedyToken) + '**'
        strongText.setParseAction(lambda s,l,t:
                                  "<b>%s</b>"%(" ".join(t[1:-1])))

        text = strongText | emText | greedyToken

        locator = (Optional(',') + OneOrMore(wordWithDigits)) ^ (Optional(',') + Optional(greedyToken) + OneOrMore(wordWithDigits))

        def locator_parse_action(s, l, t):
            raw = " ".join(t)
            # strip leading comma
            return CiteParser.Locator(re.sub('^,\s+', '', raw))
        locator.setParseAction(locator_parse_action)

        citeKey = Optional('-') + '@' + Regex(CITEKEY_RE)
        citeKey.setParseAction(lambda s,l,t: CiteParser.CiteKey(t))

        # suffix comes after a cite
        suffix = OneOrMore(text)
        suffix.setParseAction(lambda s,l,t: CiteParser.Suffix(" ".join(t)))

        # prefix comes before a cite
        prefix = OneOrMore(text)
        prefix.setParseAction(lambda s,l,t: CiteParser.Prefix(" ".join(t)))

        # a short cite, author + (date)
        shortCite = Optional('-') + '@' + Regex(CITEKEY_RE)
        shortCite.setParseAction(lambda s,l,t: CiteParser.ShortCite(t))

        # a full & complete cite (for use in brackets)
        fullCite = (citeKey | (prefix + citeKey)) + Optional(locator) + Optional(suffix)
        fullCite.setParseAction(lambda s,l,t: CiteParser.FullCite(t))

        restCite = ';' + fullCite

        bracketedCite = ('[' + fullCite + ZeroOrMore(restCite) + ']')

        shortCiteExtra = ('[' + locator + Optional(suffix) + ZeroOrMore(restCite) + ']')
        shortCiteExtra.setParseAction(lambda s,l,t: CiteParser.ShortCiteExtra(t))

        topCite = bracketedCite ^ shortCite + shortCiteExtra ^ shortCite + bracketedCite ^ shortCite

        try:
            raw = topCite.parseString(what, True)
            return self._results2cites(list(raw))
        except ParseException:
            raise Exception('The citation %s was not parseable.'%(what))

