from pelican import signals
import zot4rst
import xciterst

def register():
    signals.initialized.connect(setup_zotero)

def setup_zotero(zotero_o):
    xciterst.cluster_tracker = xciterst.ClusterTracker()
    xciterst.citeproc = zot4rst.ZoteroConnection(zotero_o.settings.get('CITATION_STYLE', zot4rst.DEFAULT_CITATION_STYLE))
    xciterst.citekeymap = zot4rst.ZoteroCitekeyMapper(xciterst.citeproc, None)
