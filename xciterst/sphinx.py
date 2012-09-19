from xciterst import smallcaps
from xciterst.roles import cite_role
from xciterst.directives import BibliographyDirective

def setup(app):
    """Install the plugin.
    
    :param app: Sphinx application context.
    """

    app.add_directive('bibliography', BibliographyDirective)
    app.add_role("smallcaps", smallcaps)
    app.add_role('xcite', cite_role)
    return
