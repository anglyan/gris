gris
====

``gris`` is a lightweight Python parser for
`RIS files <https://en.wikipedia.org/wiki/RIS_(file_format)>`. 

RIS is one of the main standardized formats used by libraries, publishers and reference
managers to exchange citation and bibliographic data.

``gris`` reads RIS files into plain Python dictionaries that can be inspected,
filtered, or converted to other formats such as ``json``. It is also tolerant
of the non-standard variations found in files exported by publishers and
tools such as Zotero.

Installation
------------

Install ``gris`` from PyPI using ``pip``::

   pip install gris

The latest development version is available on
`GitHub <https://github.com/anglyan/gris>`_.

Quickstart
----------

Read a RIS file with :func:`gris.read_ris`::

   from gris import read_ris

   data = read_ris("myreferences.ris")

Each reference is a dictionary keyed by its two-letter RIS tags. See the
:doc:`tutorial` for a walkthrough.

Where to go next
----------------

* New to ``gris``? Start with the :doc:`tutorial`.
* Check :doc:`encodings` to see how `gris` works with multiple text encodings and older files.
* See :doc:`zotero` to explore how `gris` handles exports from Zotero.

.. toctree::
   :hidden:
   :caption: Getting started

   tutorial

.. toctree::
   :hidden:
   :caption: Guides

   encodings
   zotero
   fields

.. toctree::
   :hidden:
   :caption: Reference

   specification
   apidocs/documentation
