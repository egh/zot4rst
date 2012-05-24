"""
  Module
"""
# -*- coding: utf-8 -*-
import docutils, docutils.parsers.rst
import ConfigParser
import jsbridge
import json
import os
import random
import re
import socket
import string
import sys
import zot4rst.jsonencoder
import xciterst

from zot4rst.util import unquote
import xciterst.directives
import xciterst.roles
from xciterst.util import html2rst

DEFAULT_CITATION_FORMAT = "http://www.zotero.org/styles/chicago-author-date"

class CiteKeyMapper(object):
    def __init__(self, path=None):
        # setup key mapping
        self.citekeymap = ConfigParser.SafeConfigParser()
        self.citekeymap.optionxform = str
        if path is not None:
            self.citekeymap.read(os.path.relpath(path))
        
    def __getitem__(self, citekey):
        if self.citekeymap.has_option('keymap', citekey):
            # return only the first part, the real key - rest is comment
            return re.match("^([0-9A-Z_]+)", self.citekeymap.get('keymap', citekey)).group(1)
        else:
            return citekey

class ZoteroConnection(xciterst.CiteprocWrapper):
    def __init__(self, format, **kwargs):
        # connect & setup
        self.back_channel, self.bridge = jsbridge.wait_and_create_network("127.0.0.1", 24242)
        self.back_channel.timeout = self.bridge.timeout = 60
        self.methods = jsbridge.JSObject(self.bridge, "Components.utils.import('resource://citeproc/citeproc.js')")
        self.methods.instantiateCiteProc(format)
        self.in_text_style = self.methods.isInTextStyle()

        self.key2id = {}
        self.local_items = {}
        self.citations = None

        super(ZoteroConnection, self).__init__()

    def set_format(self, format):
        self.methods.instantiateCiteProc(format)

    def get_item_id(self, key):
        """Returns the id of an item with a given key. Key will be
        looked up in the local keymap before the id is looked up."""
        return self.get_item_id_batch([key])[0]

    def get_item_id_batch(self, keys):
        to_lookup = []
        for key in keys:
            if self.local_items.has_key(key):
                self.key2id[key] = "MY-%s"%(key)
            else:
                if not(self.key2id.has_key(key)):
                    to_lookup.append(key)
        if len(to_lookup) > 0:
            ids = json.loads(self.methods.getItemIdBatch(to_lookup))
            for n, new_id in enumerate(ids):
                self.key2id[to_lookup[n]] = new_id
        return [ self.key2id[key] for key in keys ]

    def get_unique_ids(self):
        return set(self.get_item_id_batch(xciterst.cluster_tracker.get_unique_citekeys()))
        
    def citeproc_update_items(self, ids):
        self.methods.updateItems(ids)

    def citeproc_make_bibliography(self):
        data = self.methods.makeBibliography()
        if data is None: return None
        else:            return unquote(json.loads(data))

    def cache_citations(self):
        if (self.citations is None):
            xciterst.cluster_tracker.register_items(self)
            citations = []
            for cluster in xciterst.cluster_tracker.get():
                index = xciterst.cluster_tracker.get_index(cluster)
                citations.append({ 'citationItems' : cluster.citations,
                                   'properties'    : { 'index'    : index,
                                                       'noteIndex': cluster.note_index } })
            for cit in citations:
                for c in cit['citationItems']:
                    c.id = self.get_item_id(c.citekey)
            # Implement mini-batching. This is a hack to avoid what
            # appears to be a string size limitation of some sort in
            # jsbridge or code that it calls.
            batchlen = 15
            offset = 0
            self.citations = []
            while len(self.citations) < len(citations):
                raw = self.methods.appendCitationClusterBatch(citations[offset:offset+batchlen])
                citation_blocks_html = json.loads(raw)
                self.citations.extend([ html2rst(unquote(block)) for block in citation_blocks_html ])
                offset = offset + batchlen

    def get_citation(self, cluster):
        self.cache_citations()
        return self.citations[xciterst.cluster_tracker.get_index(cluster)]

    def prefix_items(self, items):
        prefixed = {}
        for k in items.keys():
            v = items[k]
            prefixed["MY-%s"%(k)] = v
            v['id'] = "MY-%s"%(v['id'])
        return prefixed

    def load_biblio(self, path):
        self.local_items = json.load(open(path))
        self.methods.registerLocalItems(self.prefix_items(self.local_items));
    
class ZoteroSetupDirective(docutils.parsers.rst.Directive):
    def __init__(self, *args, **kwargs):
        docutils.parsers.rst.Directive.__init__(self, *args)
        # This is necessary: connection hangs if created outside of an instantiated
        # directive class.
        if xciterst.citeproc is None:
            xciterst.citeproc = ZoteroConnection(self.options.get('format', DEFAULT_CITATION_FORMAT))
        else:
            xciterst.citeproc.set_format(self.options.get('format', DEFAULT_CITATION_FORMAT))

    required_arguments = 0
    optional_arguments = 0
    has_content = False
    option_spec = {'format' : docutils.parsers.rst.directives.unchanged,
                   'keymap': docutils.parsers.rst.directives.unchanged,
                   'biblio' : docutils.parsers.rst.directives.unchanged }
    def run(self):
        if self.options.has_key('keymap'):
            xciterst.citeproc.citekeymap = CiteKeyMapper(self.options['keymap'])
        else:
            xciterst.citeproc.citekeymap = CiteKeyMapper()
        if self.options.has_key('biblio'):
            xciterst.citeproc.load_biblio(self.options['biblio'])
        if xciterst.citeproc.in_text_style:
            return []
        else:
            pending = docutils.nodes.pending(xciterst.directives.FootnoteSortTransform)
            self.state_machine.document.note_pending(pending)
            return [pending]

docutils.parsers.rst.directives.register_directive('zotero-setup', ZoteroSetupDirective)
