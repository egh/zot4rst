docutils with Zotero
====================

Shamelessly stolen from the pandoc example:
http://johnmacfarlane.net/pandoc/demo/CITATIONS

.. zotero-setup::
   :style: chicago-author-date

.. default-role:: xcite

- `@DoeBook2005` says blah.

- `@DoeBook2005 [p. 30]` says blah.

- `@DoeBook2005 [p. 30, with suffix]` says blah.

- `@DoeBook2005 [-@DoeArticle2006 p. 30; see also @DoeWhy2007]` says blah.

- In a note.\ [#]_

- A citation group `[see @DoeBook2005 p. 34-35; also @DoeWhy2007 chap. 3]`.

- Another one `[see @DoeBook2005 p. 34-35]`.

- And another one in a note.\ [#]_

- Citation with a suffix and locator `[@DoeBook2005 pp. 33, 35-37 and nowhere else]`.

- Citation with suffix only `[@DoeBook2005 and nowhere else]`.

- Now some modifiers.\ [#]_

- With some markup `[*see* @DoeBook2005 p. **32**]`.

.. [#] A citation without locators `[@DoeWhy2007]`.

.. [#] Some citations `[see @DoeArticle2006 chap. 3; @DoeWhy2007; @DoeBook2005]`.

.. [#] Like a citation without author: `[-@DoeBook2005]`, and now Doe
   with a locator `[-@DoeArticle2006 p. 44]`.

References
==========
.. bibliography::
