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

"""
This module must be explicitly imported
in order to register docutils directives and roles,
unless this registration is done otherwise (e.g. Sphinx extension).
"""

from __future__ import absolute_import
import xciterst.register

from docutils.parsers.rst import directives, roles
from . import ZoteroSetupDirective

directives.register_directive("zotero-setup", ZoteroSetupDirective)
