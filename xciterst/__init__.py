import docutils
import itertools
from xciterst.util import html2rst
import xciterst
from xciterst.parser import CiteParser
from docutils.parsers.rst import roles
import sys

def check_citeproc():
    if not xciterst.citeproc:
        ## A kludge, but makes a big noise about the extension syntax for clarity.
        sys.stderr.write("#####\n")
        sys.stderr.write("##\n")
        sys.stderr.write("##  Must setup a citeproc directive before xcite role is used.\n")
        sys.stderr.write("##\n")
        sys.stderr.write("#####\n")
        raise docutils.utils.ExtensionOptionError("must set a citeproc directive before xcite role is used.")

class ClusterTracker(object):
    """Class used to track citation clusters."""

    def __init__(self):
        self.clusters = []
        self.registered_items = set([])

    def get(self):
        return self.clusters

    def track(self, cluster):
        self.clusters.append(cluster)
        index = len(self.clusters) - 1
        cluster.index = index

    def reset(self):
        self.clusters = []

    def get_unique_ids(self):
        def flatten(listoflists):
            return itertools.chain.from_iterable(listoflists)
        citekeys = list(set([ item.citekey for item in flatten([ c.citations for c in self.clusters ]) ]))
        return xciterst.citekeymap.batch_get(citekeys)

    def register_items(self, citeproc):
        """Register items in tracked clusters with the citeproc
        instance."""
        uniq_ids = self.get_unique_ids()
        if (uniq_ids != self.registered_items):
            citeproc.citeproc_update_items(list(uniq_ids))
            self.registered_items = uniq_ids

# tracker for clusters
cluster_tracker = ClusterTracker()

class CiteprocWrapper(object):
    """Class which represents a citeproc instance."""

    def __init__(self):
        self.reset()

    def generate_rest_bibliography(self):
        """Generate a bibliography of reST nodes."""
        bibdata = self.citeproc_make_bibliography()
        if not(bibdata):
            return html2rst("")
        else:
            return html2rst("%s%s%s"%(bibdata[0]["bibstart"], "".join(bibdata[1]), bibdata[0]["bibend"]))

    def cache_citations(self):
        if (self.citations is None):
            xciterst.cluster_tracker.register_items(self)
            clusters = xciterst.cluster_tracker.get()
            self.citations = self.citeproc_append_citation_cluster_batch(clusters)

    def get_citation(self, cluster):
        self.cache_citations()
        return self.citations[cluster.index]

    # override in subclass
    def citeproc_update_items(self, ids):
        """Call updateItems in citeproc."""
        pass

    def citeproc_make_bibliography(self):
        """Call makeBibliography in citeproc. Should return an HTML string."""
        pass

    def citeproc_append_citation_cluster_batch(self, clusters):
        """Call appendCitationCluster for a batch of citations."""
        pass

    def reset(self):
        self.citations = None
    
# placeholder for citeproc instance
citeproc = None
citekeymap = None

class smallcaps(docutils.nodes.Inline, docutils.nodes.TextElement): pass

roles.register_local_role("smallcaps", smallcaps)
