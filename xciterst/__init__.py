import docutils
import itertools
import re

class CitationInfo(object):
    """Class to hold information about a citation for passing to
    citeproc."""

    def __init__(self, **kwargs):
        self.key = kwargs.get('key')
        self.label = kwargs.get('label', None)
        self.locator = kwargs.get('locator', None)
        self.suppress_author = kwargs.get('suppress_author', False)
        self.prefix = kwargs.get('prefix', None)
        if self.prefix:
            self.prefix = re.sub(r'\s+,', ',', self.prefix)
        self.suffix = kwargs.get('suffix', None)
        if self.suffix:
            self.suffix = re.sub(r'\s+,', ',', self.suffix)
        self.author_only = kwargs.get('author_only', False)
        self.id = None
    
    def __str__(self):
        return "%s %s(%s) %s"%(self.prefix, self.key, self.locator, self.suffix)

    def __eq__(self, other):
        return ((self.key == other.key) and
                (self.label == other.label) and
                (self.locator == other.locator) and
                (self.suppress_author == other.suppress_author) and
                (self.prefix == other.prefix) and
                (self.suffix == other.suffix) and
                (self.author_only == other.author_only) and
                (self.id == other.id))
                
class CitationCluster(object):
    """Class to hold a cluster of citations, with information about
    them suitable for submission to citeproc."""

    def __init__(self, citations):
        self.citations = citations
        self.note_index = 0
        self.index = 0

    def __eq__(self, other):
        return ((self.citations == other.citations) and
                (self.note_index == other.note_index) and
                (self.index == other.index))

class CiteprocWrapper(object):
    """Class which represents a citeproc instance."""

    def __init__(self):
        self.tracked_clusters = []
        self.registered_items = set([])

    def track_cluster(self, cluster):
        self.tracked_clusters.append(cluster)
        
    def reset_tracked_clusters(self):
        self.tracked_clusters = []

    def get_cluster_index(self, cluster):
        return self.tracked_clusters.index(cluster)

    def get_unique_keys(self):
        def flatten(listoflists):
            return itertools.chain.from_iterable(listoflists)
        return list(set([ item.key for item in flatten([ c.citations for c in self.tracked_clusters ]) ]))

    def register_items(self):
        """Register items in tracked clusters with the citeproc
        instance."""
        uniq_ids = self.get_unique_ids()
        if (uniq_ids != self.registered_items):
            self.citeproc_update_items(list(uniq_ids))
            self.registered_items = uniq_ids

    # override in subclass
    def citeproc_update_items(self, ids):
        pass

class smallcaps(docutils.nodes.Inline, docutils.nodes.TextElement): pass
docutils.parsers.rst.roles.register_local_role("smallcaps", smallcaps)
