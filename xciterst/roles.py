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
import logging
from six.moves import range

logging.basicConfig(
    format="%(levelname)s:%(funcName)s:%(message)s", level=logging.DEBUG
)
import random
import string
import xciterst
from xciterst.parser import CiteParser
from xciterst.directives import CitationTransform


def handle_cite_cluster(inliner, cite_cluster):
    document = inliner.document
    xciterst.cluster_tracker.track(cite_cluster)
    if xciterst.citeproc.in_text_style or (
        type(inliner.parent) == docutils.nodes.footnote
    ):
        # already in a footnote, or in-text style: just add a pending
        pending = docutils.nodes.pending(CitationTransform)
        pending.details["cite_cluster"] = cite_cluster
        document.note_pending(pending)
        return pending
    else:
        # not in a footnote & this is a footnote style; insert a
        # reference & add a footnote to the end

        label = "".join(random.choice(string.digits) for x in range(20))

        # Set up reference
        refnode = docutils.nodes.footnote_reference("[%s]_" % label)
        refnode["auto"] = 1
        refnode["refname"] = label
        document.note_footnote_ref(refnode)
        document.note_autofootnote_ref(refnode)

        # Set up footnote
        footnote = docutils.nodes.footnote("")
        footnote["auto"] = 1
        footnote["names"].append(label)
        pending = docutils.nodes.pending(CitationTransform)
        pending.details["cite_cluster"] = cite_cluster
        paragraph = docutils.nodes.paragraph()
        paragraph.setup_child(pending)
        paragraph += pending
        footnote.setup_child(paragraph)
        footnote += paragraph
        document.note_pending(pending)
        document.note_autofootnote(footnote)

        # Temporarily stash footnote as a child of the refnode
        refnode.setup_child(footnote)
        refnode += footnote
        return refnode


def cite_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    """Text role for citations."""
    xciterst.check_citeproc()

    logging.debug("parsing text = %s", text)
    [first_cluster, second_cluster] = CiteParser().parse(text)
    nodeset = []
    if first_cluster is not None:
        nodeset.append(handle_cite_cluster(inliner, first_cluster))
        nodeset.append(docutils.nodes.Text(" ", rawsource=" "))
    nodeset.append(handle_cite_cluster(inliner, second_cluster))
    return nodeset, []
