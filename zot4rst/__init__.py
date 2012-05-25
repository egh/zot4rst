"""
  Module
"""
# -*- coding: utf-8 -*-
import docutils, docutils.parsers.rst
import ConfigParser
import jsbridge
import json
import os
import re
import socket

import zot4rst.jsonencoder
from   zot4rst.util import unquote
import xciterst
import xciterst.directives
import xciterst.roles
from   xciterst.util import html2rst

DEFAULT_CITATION_FORMAT = "http://www.zotero.org/styles/chicago-author-date"

class ZoteroCitekeyMapper(object):
    """class used for mapping citekeys to IDs."""
    
    def __init__(self, conn, path=None):
        self.conn = conn
        # setup key mapping
        self.citekey2zotkey = ConfigParser.SafeConfigParser()
        self.citekey2zotkey.optionxform = str
        if path is not None:
            self.citekey2zotkey.read(os.path.relpath(path))
        self.zotkey2id = {}
        
    def __getitem__(self, citekey):
        """Get a citation id from a citekey."""

        # First, get zotero key from citekey
        if self.citekey2zotkey.has_option('keymap', citekey):
            # return only the first part, the real key - rest is comment
            zotkey = re.match("^([0-9A-Z_]+)", self.citekey2zotkey.get('keymap', citekey)).group(1)
        else:
            zotkey = citekey
        
        return self.get_item_id_batch([zotkey])[0]

    def get_item_id_batch(self, keys):
        to_lookup = []
        for key in keys:
            if self.conn.local_items.has_key(key):
                self.zotkey2id[key] = "MY-%s"%(key)
            else:
                if not(self.zotkey2id.has_key(key)):
                    to_lookup.append(key)
        if len(to_lookup) > 0:
            ids = json.loads(self.conn.methods.getItemIdBatch(to_lookup))
            for n, new_id in enumerate(ids):
                self.zotkey2id[to_lookup[n]] = new_id
        return [ self.zotkey2id[key] for key in keys ]

class ZoteroConnection(xciterst.CiteprocWrapper):
    def __init__(self, format, **kwargs):
        # connect & setup
        self.back_channel, self.bridge = jsbridge.wait_and_create_network("127.0.0.1", 24242)
        self.back_channel.timeout = self.bridge.timeout = 60
        self.methods = jsbridge.JSObject(self.bridge, "Components.utils.import('resource://citeproc/citeproc.js')")
        self.methods.instantiateCiteProc(format)
        self.in_text_style = self.methods.isInTextStyle()
        self.local_items = {}
        super(ZoteroConnection, self).__init__()

    def set_format(self, format):
        self.methods.instantiateCiteProc(format)

    def citeproc_update_items(self, ids):
        self.methods.updateItems(ids)

    def citeproc_make_bibliography(self):
        raw = self.methods.makeBibliography()
        if raw is None: return None
        else: return unquote(json.loads(raw))

    def _chunks(self, l, n):
        """Break a list into evenly sized groups."""
        return [l[i:i+n] for i in range(0, len(l), n)]

    def citeproc_append_citation_cluster_batch(self, clusters):
        # Implement mini-batching. This is a hack to avoid what
        # appears to be a string size limitation of some sort in
        # jsbridge or code that it calls.
        retval = []
        for chunk in self._chunks(clusters, 15):
            raw = self.methods.appendCitationClusterBatch(chunk)
            cooked = [ html2rst(unquote(block)) for block in json.loads(raw) ]
            retval.extend(cooked)
        return retval

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
        xciterst.citekeymap = ZoteroCitekeyMapper(xciterst.citeproc, self.options.get('keymap', None))
        if self.options.has_key('biblio'):
            xciterst.citeproc.load_biblio(self.options['biblio'])

        if xciterst.citeproc.in_text_style:
            return []
        else:
            pending = docutils.nodes.pending(xciterst.directives.FootnoteSortTransform)
            self.state_machine.document.note_pending(pending)
            return [pending]

docutils.parsers.rst.directives.register_directive('zotero-setup', ZoteroSetupDirective)
