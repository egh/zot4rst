# -*- coding: utf-8 -*-
import json
import logging
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.DEBUG)
import urllib2

import docutils
import docutils.parsers.rst

import xciterst
import xciterst.directives
import xciterst.roles

import zot4rst.jsonencoder
#from xciterst.util import html2rst

DEFAULT_CITATION_STYLE = "http://www.zotero.org/styles/chicago-author-date"
BIBLIOGRAPHY_REQUEST_URL = "http://localhost:23119/zotxt/items"

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
        logging.debug('clusters = %s', clusters)
        request_json = {
            "format": "bibliography",
            "styleId": "chicago-author-date",
            "citationGroups": clusters
        }
        data = json.dumps(request_json, indent=2,
                          cls=zot4rst.jsonencoder.ZoteroJSONEncoder)
        try:
            req = urllib2.Request(BIBLIOGRAPHY_REQUEST_URL,
                                  data, {'Content-Type': 'application/json'})
            f = urllib2.urlopen(req)
            resp_json = f.read()
            f.close()
        except:
            logging.warning('cannot open URL %s', BIBLIOGRAPHY_REQUEST_URL)
            raise
        resp = json.loads(resp_json)
        return [resp['citationClusters'], resp['bibliography']]

    def prefix_items(self, items):
        prefixed = {}
        for k in items.keys():
            v = items[k]
            prefixed["MY-%s" % (k)] = v
            v['id'] = "MY-%s" % (v['id'])
        return prefixed

    def load_biblio(self, path):
        self.local_items = json.load(open(path))
        self.methods.registerLocalItems(self.prefix_items(self.local_items))

def init(style=None):
    if style is None:
        style = DEFAULT_CITATION_STYLE
    xciterst.cluster_tracker = xciterst.ClusterTracker()
    xciterst.citeproc = ZoteroConnection(style)

class ZoteroSetupDirective(docutils.parsers.rst.Directive):
    def __init__(self, *args, **kwargs):
        docutils.parsers.rst.Directive.__init__(self, *args)
        init(self.options.get('style', None))

    required_arguments = 0
    optional_arguments = 0
    has_content = False
    option_spec = {'style' : docutils.parsers.rst.directives.unchanged,
                   'biblio' : docutils.parsers.rst.directives.unchanged }
    def run(self):
        if self.options.has_key('biblio'):
            xciterst.citeproc.load_biblio(self.options['biblio'])

        if xciterst.citeproc.in_text_style:
            return []
        else:
            pending = docutils.nodes.pending(xciterst.directives.FootnoteSortTransform)
            self.state_machine.document.note_pending(pending)
            return [pending]

docutils.parsers.rst.directives.register_directive('zotero-setup', ZoteroSetupDirective)
