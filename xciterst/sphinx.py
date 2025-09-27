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
from xciterst import smallcaps
from xciterst.roles import cite_role
from xciterst.directives import BibliographyDirective


def setup(app):
    """Install the plugin.

    :param app: Sphinx application context.
    """

    app.add_directive("bibliography", BibliographyDirective)
    app.add_role("smallcaps", smallcaps)
    app.add_role("xcite", cite_role)
    return
