"""
This module must be explicitly imported
in order to register docutils directives and roles,
unless this registration is done otherwise (e.g. Sphinx extension).
"""

from __future__ import absolute_import
from docutils.parsers.rst import directives, roles
from . import smallcaps
from .directives import BibliographyDirective
from .roles import cite_role

roles.register_local_role("smallcaps", smallcaps)
directives.register_directive("bibliography", BibliographyDirective)
roles.register_canonical_role("xcite", cite_role)
