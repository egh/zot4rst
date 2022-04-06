# -*- coding: utf-8 -*-
import docutils, docutils.parsers.rst
import json
import urllib.request

import zot4rst.jsonencoder
import xciterst
import xciterst.directives
import xciterst.roles
from xciterst.util import html2rst

DEFAULT_CITATION_STYLE = "http://www.zotero.org/styles/chicago-author-date"


class ZoteroConnection(xciterst.CiteprocWrapper):
    def __init__(self, style, **kwargs):
        self.local_items = {}
        self._in_text_style = True  # XXXX should get from zotxt
        super(ZoteroConnection, self).__init__()

    @property
    def in_text_style(self):
        if not self._in_text_style:
            self._in_text_style = self.methods.isInTextStyle()
        return self._in_text_style

    def citeproc_process(self, clusters):
        request_json = {"styleId": "chicago-author-date", "citationGroups": clusters}
        data = json.dumps(
            request_json, indent=2, cls=zot4rst.jsonencoder.ZoteroJSONEncoder
        )
        req = urllib.request.Request(
            "http://localhost:23119/zotxt/bibliography",
            data.encode("ascii"),
            {"Content-Type": "application/json"},
        )
        try:
            f = urllib.request.urlopen(req)
            resp_json = f.read()
            f.close()
            resp = json.loads(resp_json)
            return [resp["citationClusters"], resp["bibliography"]]
        except urllib.error.HTTPError as e:
            raise urllib.error.HTTPError(e.url, e.code, e.read().decode(), e.hdrs, e.fp)

    def prefix_items(self, items):
        prefixed = {}
        for k in items.keys():
            v = items[k]
            prefixed["MY-%s" % (k)] = v
            v["id"] = "MY-%s" % (v["id"])
        return prefixed

    def load_biblio(self, path):
        pass
        # TODO: solve this
        # self.local_items = json.load(open(path))
        # self.methods.registerLocalItems(self.prefix_items(self.local_items))


def init(style=None):
    if style is None:
        style = DEFAULT_CITATION_STYLE
    xciterst.cluster_tracker = xciterst.ClusterTracker()
    xciterst.citeproc = ZoteroConnection(style)


class ZoteroSetupDirective(docutils.parsers.rst.Directive):
    def __init__(self, *args, **kwargs):
        docutils.parsers.rst.Directive.__init__(self, *args)
        init(self.options.get("style", None))

    required_arguments = 0
    optional_arguments = 0
    has_content = False
    option_spec = {
        "style": docutils.parsers.rst.directives.unchanged,
        "biblio": docutils.parsers.rst.directives.unchanged,
    }

    def run(self):
        if "biblio" in self.options:
            xciterst.citeproc.load_biblio(self.options["biblio"])

        if xciterst.citeproc.in_text_style:
            return []
        else:
            pending = docutils.nodes.pending(xciterst.directives.FootnoteSortTransform)
            self.state_machine.document.note_pending(pending)
            return [pending]


docutils.parsers.rst.directives.register_directive("zotero-setup", ZoteroSetupDirective)
