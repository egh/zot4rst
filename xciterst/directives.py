import docutils
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

docutils.parsers.rst.directives.register_directive('bibliography', BibliographyDirective)
