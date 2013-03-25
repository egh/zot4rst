=================================================
 zot4rst: Zotero for reStructuredText (docutils)
=================================================

Background
~~~~~~~~~~

Zotero_ is a useful tool for managing citations.

``zot4rst`` is an extension to the Python docutils_ package for
including citations in reStructuredText_ documents.

Installation
~~~~~~~~~~~~

1. Install Zotero_.
2. Install docutils from a `docutils snapshot`_ release.
3. Install zot4rst::

     sudo python setup.py install

4. Download and install the Firefox extension:

  https://bitbucket.org/egh/zot4rst/downloads/zotero-for-restructured-text.xpi

Quickstart
~~~~~~~~~~

See ``example/example.rst``, and the generated ``example/example.pdf``
and ``example/example.html``. Citation syntax is identical to pandoc.

zot4rst automatically maps citation keys (e.g., @DoeTitle2010) to
entries in the zotero database. The key should be of the form
@AuthorTitleDate. So, for the item:

  John Doe, “Article,” Journal of Generic Studies, 2006.

You could use: @DoeArticle2006. This should be easy to use, but the
reference needs to be unambiguous, which can be difficult if there are
multiple items with the same author, title, and year. I am looking
into ways to handle this better.

To include Zotero_ citations in a reStructuredText_ document, you must
use the bundled ``zrst2*`` scripts, which have been modified to
include support for ``zotero`` directives. These executables are
installed using ``setup.py`` above. Currently, they are:

- ``zrst2html``
- ``zrst2odt``
- ``zrst2pdf``
- ``zrst2pseudoxml``
- ``zrst2rst``

Sphinx
~~~~~~

To use in sphinx, simply add the ``zot4rst.sphinx`` extension to your
``conf.py`` file::

  extensions = ['zot4rst.sphinx']

Pelican
~~~~~~~

To use in pelican_ (version 3.1 or later), add the following to your
``pelicanconf.py`` file:

  PLUGINS = ['zot4rst.pelican_plugin',]

Details
~~~~~~~

Some details, in no particular order.

Note that ``zrst2rst`` will transform your citations into plain
reStructuredText files without the Zotero extension. For example::

  A citation group :xcite:`[see @item1 p. 34-35; also @item3 chap. 3]`.

will become::

  A citation group (see Doe 2005, p. 34–35; also Doe and Roe 2007,
  chap. 3).

and the bibliography will be fully expanded. This can be used to
create RST files that will work without zot4rst.

If you use a footnote citation format, zot4rst will insert footnotes
for you.

However, if you also use regular autonumbered footnotes in the same
section or paragraph, the ordering will be wrong. So if you want to do
this, you will need to put your citations in a footnote
explicitly. For example::

  Water is wet. [#]_ But there are those who dispute it. [#]_

  .. [#] :xcite:`[See @item3]`.

  .. [#] These people are wrong.

.. _Zotero: http://www.zotero.org/
.. _`org-mode`: http://orgmode.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _docutils: http://docutils.sourceforge.net/
.. _`docutils snapshot`: http://docutils.sourceforge.net/docutils-snapshot.tgz

.. _`sphinx bibtex`: http://sphinxcontrib-bibtex.readthedocs.org/
.. _pelican: https://github.com/getpelican/pelican/
