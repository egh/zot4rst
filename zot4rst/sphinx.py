from  zot4rst import ZoteroBibliographyDirective, ZoteroSetupDirective, zot_cite_role, smallcaps

def setup(app):
    """Install the plugin.
    
    :param app: Sphinx application context.
    """

    app.add_directive('zotero-setup', ZoteroSetupDirective)
    app.add_directive('zotero-bibliography', ZoteroBibliographyDirective)
    app.add_role("smallcaps", smallcaps)
    app.add_role('xcite', zot_cite_role)
    return
