"""
  Module
"""
# -*- coding: utf-8 -*-
import docutils, docutils.parsers.rst
import ConfigParser
import json
import os
import re
import socket
import urllib2

import zot4rst.jsonencoder
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
        self._in_text_style = True # XXXX should get from zotxt
        super(ZoteroConnection, self).__init__()

    @property
    def in_text_style(self):
        if not self._in_text_style:
            self._in_text_style = self.methods.isInTextStyle()
        return self._in_text_style

    def citeproc_process(self, clusters):
        request_json = { "styleId" : "chicago-author-date",
                         "citationGroups" : clusters }
        data = json.dumps(request_json, indent=2,cls=zot4rst.jsonencoder.ZoteroJSONEncoder)
        req = urllib2.Request("http://localhost:23119/zotxt/bibliography", data, {'Content-Type': 'application/json'})
        f = urllib2.urlopen(req)
        resp_json = f.read()
        f.close()
        resp = json.loads(resp_json)
        return [resp['citationClusters'], resp['bibliography']]

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
