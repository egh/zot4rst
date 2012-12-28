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

DEFAULT_CITATION_STYLE = "http://www.zotero.org/styles/chicago-author-date"

class ZoteroCitekeyMapper(object):
    """Class used for mapping citekeys to IDs."""
    
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

        # First, get zotero key from citekey using keymap file
        if self.citekey2zotkey.has_option('keymap', citekey):
            # return only the first part, the real key - rest is comment
            zotkey = re.match("^([0-9A-Z_]+)", self.citekey2zotkey.get('keymap', citekey)).group(1)
        else:
            zotkey = citekey
        
        # now return the item id
        if zotkey in self.zotkey2id:
            return self.zotkey2id[zotkey]
        else:
            return self.batch_get([zotkey])[0]

    def get_item_id_dynamic_batch(self, keys):
        """A simpler method for..."""
        if len(keys) == 0: return []
        data = []
        for key in keys:
            m = re.match(r"^([A-Z][a-z]+)([A-Z][a-z]+)?([0-9]+)?", key)
            data.append([m.group(1), m.group(2), m.group(3)])
        return json.loads(self.conn.methods.getItemIdDynamicBatch(data))

    def get_item_id_raw_batch(self, keys):
        if len(keys) == 0: return []
        return json.loads(self.conn.methods.getItemIdRawBatch(keys))
    
    def batch_get(self, keys):
        local_keys =   [ k for k in keys if self.conn.local_items.has_key(k) and (k not in self.zotkey2id) ]
        raw_keys =     [ k for k in keys if re.match(r"^[A-Z0-9]{8}$", k) and (k not in self.zotkey2id) ]
        dynamic_keys = [ k for k in keys if (k not in local_keys) and (k not in raw_keys) and (k not in self.zotkey2id) ]
        for k in local_keys:
            self.zotkey2id[k] = "MY-%s"%(k)
        for k, i in zip(raw_keys, self.get_item_id_raw_batch(raw_keys)):
            self.zotkey2id[k] = i
        for k, i in zip(dynamic_keys, self.get_item_id_dynamic_batch(dynamic_keys)):
            self.zotkey2id[k] = i

        return [ self.zotkey2id[k] for k in keys ]

class ZoteroConnection(xciterst.CiteprocWrapper):
    def __init__(self, style, **kwargs):
        self.local_items = {}
        self._methods = None
        self._needs_reinstantiation = False
        self._in_text_style = None
        self.reset(style)
        super(ZoteroConnection, self).__init__()

    @property
    def methods(self):
        if not self._methods:
            # connect & setup
            back_channel, bridge = jsbridge.wait_and_create_network("127.0.0.1", 24242)
            back_channel.timeout = bridge.timeout = 60
            self._methods = jsbridge.JSObject(bridge, "Components.utils.import('resource://citeproc/citeproc.js')")
            self._needs_reinstantiation = True
        if self._needs_reinstantiation:
            self._needs_reinstantiation = False
            self._methods.instantiateCiteProc(self.style)
        return self._methods

    @property
    def in_text_style(self):
        if not self._in_text_style:
            self._in_text_style = self.methods.isInTextStyle()
        return self._in_text_style

    def reset(self, style=None):
        if (style is not None): self.style = style
        self._needs_reinstantiation = True
        self._in_text_style = None
        super(ZoteroConnection, self).reset()

    def citeproc_update_items(self, ids):
        self.methods.updateItems(ids)

    def citeproc_make_bibliography(self):
        raw = self.methods.makeBibliography()
        if (raw is None) or (raw == ""): return None
        else: return unquote(json.loads(raw))

    def _chunks(self, l, n):
        """Break a list into evenly sized groups."""
        return [l[i:i+n] for i in range(0, len(l), n)]

    def citeproc_append_citation_cluster_batch(self, clusters):
        # Bridge hangs if output contains above-ASCII chars (I guess Telnet kicks into
        # binary mode in that case, leaving us to wait for a null string terminator)
        # JS strings are in Unicode, and the JS escaping mechanism for Unicode with
        # escape() is, apparently, non-standard. I played around with various
        # combinations of decodeURLComponent() / encodeURIComponent() and escape() /
        # unescape() ... applying escape() on the JS side of the bridge, and
        # using the following suggestion for a Python unquote function worked,
        # so I stuck with it:
        #   http://stackoverflow.com/questions/300445/how-to-unquote-a-urlencoded-unicode-string-in-python

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

def reset(style=None):
    if style is None: style = DEFAULT_CITATION_STYLE
    xciterst.cluster_tracker = xciterst.ClusterTracker()
    xciterst.citekeymap = zot4rst.ZoteroCitekeyMapper(xciterst.citeproc, None)
    if xciterst.citeproc is None:
        xciterst.citeproc = ZoteroConnection(style)
    else:
        xciterst.citeproc.reset(style)

def init(style=None):
    if style is None: style = DEFAULT_CITATION_STYLE
    xciterst.citeproc = zot4rst.ZoteroConnection(style)
    reset(style)

class ZoteroSetupDirective(docutils.parsers.rst.Directive):
    def __init__(self, *args, **kwargs):
        docutils.parsers.rst.Directive.__init__(self, *args)
        init(self.options.get('style', None))

    required_arguments = 0
    optional_arguments = 0
    has_content = False
    option_spec = {'style' : docutils.parsers.rst.directives.unchanged,
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
