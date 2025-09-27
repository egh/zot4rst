# Copyright (C) 2010-2025 Erik Hetzner
#
# This file is part of zot4rst.
#
# zot4rst is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# zot4rst is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with zot4rst. If not, see
# <https://www.gnu.org/licenses/>.

from __future__ import absolute_import
import docutils
import itertools
from xciterst.util import html2rst
import xciterst
from xciterst.parser import CiteParser
import sys


def check_citeproc():
    if not xciterst.citeproc:
        ## A kludge, but makes a big noise about the extension syntax for clarity.
        sys.stderr.write("#####\n")
        sys.stderr.write("##\n")
        sys.stderr.write(
            "##  Must setup a citeproc directive before xcite role is used.\n"
        )
        sys.stderr.write("##\n")
        sys.stderr.write("#####\n")
        raise docutils.utils.ExtensionOptionError(
            "must set a citeproc directive before xcite role is used."
        )


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
        self.bibdata = None

    def generate_rest_bibliography(self):
        """Generate a bibliography of reST nodes."""
        self.cache_citations()
        bibdata = self.bibdata
        if not (bibdata):
            return html2rst("")
        else:
            return html2rst(
                "".join(
                    (
                        bibdata[0]["bibstart"],
                        "".join(self.bibdata[1]),
                        bibdata[0]["bibend"],
                    )
                )
            )

    def cache_citations(self):
        if self.citations is None:
            clusters = xciterst.cluster_tracker.get()
            citdata, bibdata = self.citeproc_process(clusters)
            self.citations = [html2rst(n) for n in citdata]
            self.bibdata = bibdata

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


class smallcaps(docutils.nodes.Inline, docutils.nodes.TextElement):
    pass
