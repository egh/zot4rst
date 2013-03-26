import docutils
import docutils.transforms
import xciterst

class BibliographyDirective(docutils.parsers.rst.Directive):
    """Directive for bibliographies."""
    ## This could be extended to support selection of
    ## included bibliography entries. The processor has
    ## an API to support this, although it hasn't yet been
    ## implemented in any products that I know of.
    required_arguments = 0
    optional_arguments = 1
    has_content = False

    def run(self):
        pending = docutils.nodes.pending(BibliographyTransform)
        pending.details.update(self.options)
        self.state_machine.document.note_pending(pending)
        return [pending]

class BibliographyTransform(docutils.transforms.Transform):
    """Transform which generates a bibliography. Wait for all items to
    be registered, then we generate a bibliography."""
    default_priority = 700

    def apply(self):
        xciterst.cluster_tracker.register_items(xciterst.citeproc)
        self.startnode.replace_self(xciterst.citeproc.generate_rest_bibliography())

class FootnoteSortTransform(docutils.transforms.Transform):
    default_priority = 641

    def apply(self):
        # Footnotes inserted via xcite are numbered before
        # normal reST auto-numbered footnotes, so we renumber
        # them as a single set, according to order of appearance
        # of the refs in text, taking care to keep the
        # ref and footnote numbering lined up.
        footnotemap = {}
        footnotes = self.document.autofootnotes
        for i in range(0, len(self.document.autofootnotes), 1):
            footnotemap[footnotes[i]['ids'][0]] = i
        newlist = []
        refs = self.document.autofootnote_refs
        for i in range(0, len(refs), 1):
            newlist.append(footnotes[footnotemap[refs[i]['refid']]])
        self.document.autofootnotes = newlist

        # The lists are now congruent and in document order, but the
        # footnote numbers are screwed up, and the notes themselves
        # may be in the wrong position.

        # Reassign numbers to the footnotes
        for i in range(0, len(self.document.autofootnotes), 1):
            label = self.document.autofootnotes[i].children[0]
            oldnum = label.children[0]
            newnum = docutils.nodes.Text(str(i + 1))
            label.replace(oldnum, newnum)

        # Move the footnotes themselves to a more sensible location
        # get the footnote label
        for i in range(0, len(self.document.autofootnotes), 1):
            footnote_node = self.document.autofootnotes[i]
            ref_node = self.document.autofootnote_refs[i]

            footnote_node.parent.remove(footnote_node)

            footnotes_at_end = getattr(self.document.settings, 'footnotes_at_end', 1)

            if footnotes_at_end:
                self.document += footnote_node
                self.document.setup_child(footnote_node)
            else:
                ref_parent = ref_node.parent
                ref_and_note = docutils.nodes.generated()
                ref_and_note += ref_node
                ref_and_note.setup_child(ref_node)
                ref_and_note += footnote_node
                ref_and_note.setup_child(footnote_node)
                ref_parent.replace(ref_node, ref_and_note)
                ref_parent.setup_child(ref_and_note)

        # Reassign numbers to the refs
        # (we don't touch these until now because they may contain
        # trojan footnotes)
        for i in range(0, len(self.document.autofootnote_refs), 1):
            ref = self.document.autofootnote_refs[i]
            if len(ref.children) == 2:
                ref.children.pop(0)
            oldnum = ref.children[0]
            newnum = docutils.nodes.Text(str(i + 1))
            ref.replace(oldnum, newnum)

        for i in range(0, len(self.document.autofootnotes), 1):
            footnote = self.document.autofootnotes[i]
            for child in footnote.children:
                for grandchild in child.children:
                    if isinstance(grandchild, docutils.nodes.pending):
                        cluster = grandchild.details['cite_cluster']
                        cluster.note_index = i

        empty = docutils.nodes.generated()
        self.startnode.replace_self(empty)

class CitationTransform(docutils.transforms.Transform):
    #
    # Before Footnote
    #
    default_priority = 538

    def apply(self):
        cite_cluster = self.startnode.details['cite_cluster']
        
        next_pending = docutils.nodes.pending(CitationSecondTransform)
        next_pending.details['cite_cluster'] = cite_cluster
        self.document.note_pending(next_pending)
	self.startnode.replace_self(next_pending)

class CitationSecondTransform(docutils.transforms.Transform):
    """Second pass transform for a citation. We use two passes because
    we want to generate all the citations in a batch, and we need to
    get the note indexes first."""
    #
    # After Footnote (to pick up the note number)
    #
    default_priority = 650
    def apply(self):
        cite_cluster = self.startnode.details['cite_cluster']
        footnote_node = self.startnode.parent.parent
        if type(footnote_node) == docutils.nodes.footnote:
            cite_cluster.note_index = int(str(footnote_node.children[0].children[0]))
        cite_cluster = self.startnode.details['cite_cluster']
        newnode = xciterst.citeproc.get_citation(cite_cluster)
        self.startnode.replace_self(newnode)

docutils.parsers.rst.directives.register_directive('bibliography', BibliographyDirective)
