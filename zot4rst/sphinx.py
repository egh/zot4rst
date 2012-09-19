import xciterst.sphinx

from zot4rst import ZoteroSetupDirective

def setup(app):
    """Install the plugin.
    
    :param app: Sphinx application context.
    """

    app.add_directive('zotero-setup', ZoteroSetupDirective)
    xciterst.sphinx.setup(app)
    return
