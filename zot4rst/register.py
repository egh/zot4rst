"""
This module must be explicitly imported
in order to register docutils directives and roles,
unless this registration is done otherwise (e.g. Sphinx extension).
"""
from __future__ import absolute_import
import xciterst.register

from docutils.parsers.rst import directives, roles
from . import ZoteroSetupDirective

directives.register_directive('zotero-setup', ZoteroSetupDirective)
