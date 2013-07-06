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

    def get(self):
        return self.clusters

    def track(self, cluster):
        self.clusters.append(cluster)
        index = len(self.clusters) - 1
        cluster.index = index

# tracker for clusters
cluster_tracker = ClusterTracker()

class CiteprocWrapper(object):
    """Class which represents a citeproc instance."""

    def __init__(self):
        self.citations = None

    def generate_rest_bibliography(self):
        """Generate a bibliography of reST nodes."""
        clusters = xciterst.cluster_tracker.get()
        bibdata = self.citeproc_process(clusters)[1]
        if not(bibdata):
            return html2rst("")
        else:
            return html2rst("%s%s%s"%(bibdata[0]["bibstart"], "".join(bibdata[1]), bibdata[0]["bibend"]))

    def cache_citations(self):
        if (self.citations is None):
            clusters = xciterst.cluster_tracker.get()
            html = self.citeproc_process(clusters)[0]
            self.citations = [ html2rst(n) for n in html ]

    def get_citation(self, cluster):
        self.cache_citations()
        return self.citations[cluster.index]

    # override in subclass
    def citeproc_process(self, citations):
        """Return (citations, bibliograph)."""
        pass
    
# placeholder for citeproc instance
citeproc = None
citekeymap = None

class smallcaps(docutils.nodes.Inline, docutils.nodes.TextElement): pass

roles.register_local_role("smallcaps", smallcaps)
