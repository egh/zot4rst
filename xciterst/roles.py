import docutils
import random
import string
import xciterst
from xciterst.parser import CiteParser
from xciterst.directives import CitationTransform

def handle_cite_cluster(inliner, cite_cluster):
    def random_label():
        return "".join(random.choice(string.digits) for x in range(20))

    parent = inliner.parent
    document = inliner.document
    xciterst.cluster_tracker.track(cite_cluster)
    if xciterst.citeproc.in_text_style or \
            (type(parent) == docutils.nodes.footnote):
        # already in a footnote, or in-text style: just add a pending
        pending = docutils.nodes.pending(CitationTransform)
        pending.details['cite_cluster'] = cite_cluster
        document.note_pending(pending)
        return pending
    else:
        # not in a footnote & this is a footnote style; insert a
        # reference & add a footnote to the end

        label = random_label()

	# Set up reference
        refnode = docutils.nodes.footnote_reference('[%s]_' % label)
        refnode['auto'] = 1
        refnode['refname'] = label
        document.note_footnote_ref(refnode)
        document.note_autofootnote_ref(refnode)

	# Set up footnote
        footnote = docutils.nodes.footnote("")
        footnote['auto'] = 1
        footnote['names'].append(label)
        pending = docutils.nodes.pending(CitationTransform)
        pending.details['cite_cluster'] = cite_cluster
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

def cite_role(role, rawtext, text, lineno, inliner,
                  options={}, content=[]):
    """Text role for citations."""
    xciterst.check_citeproc()

    [first_cluster, second_cluster] = CiteParser().parse(text)
    nodeset = []
    if first_cluster is not None:
        nodeset.append(handle_cite_cluster(inliner, first_cluster))
        nodeset.append(docutils.nodes.Text(" ", rawsource=" "))
    nodeset.append(handle_cite_cluster(inliner, second_cluster))
    return nodeset, []

docutils.parsers.rst.roles.register_canonical_role('xcite', cite_role)
