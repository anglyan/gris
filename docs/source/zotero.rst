RIS and Zotero: how they differ
===============================

The :doc:`specification` page describes the RIS format as defined by the
original Refman specification. `Zotero <https://www.zotero.org>`_ reads and writes RIS
files too, but it does not follow that specification to the letter. 

This page summarizes where Zotero's behaviour differs from the standard Refman specification
as of Jan 2026.

Overview
--------

Zotero stores references as typed items with named fields (``title``,
``publicationTitle``, ``journalAbbreviation``, ...), not as RIS tags. Its
RIS translator maps those fields to tags on export, and tags back to
fields on import. Two consequences follow:

* When exporting files, Zotero uses one fixed, consistent tag for each field, and
  the tag it uses for some fields differs from the one preferred by the
  original specification. For instance, it writes the journal name in
  ``T2``.
* When importing files, Zotero accepts many more variations than the
  specification allows, including variants written by EndNote, Citavi,
  ProCite and publishers.

``gris`` parses RIS files into a Python dictionary object, so it can read any
format or specification. However, its helper functions 
are stricter than Zotero's.

Records exported by Zotero
--------------------------

A record written by Zotero starts with ``TY`` and ends with ``ER``. Between
them, tags follow a fixed order for each item type. By default it starts
with ``TI``, ``AU``, ``T2``, ``A2``, ``T3``, ``A3``, ``A4`` and ``AB``. Records are separated by a blank
line, and lines end in ``\r\n``. A short example of a Zotero-style
record is:

.. code-block:: ignore

    TY  - JOUR
    TI  - A test article
    AU  - Doe, Jane
    AU  - Roe, Richard
    T2  - Journal of Tests
    AB  - Abstract text.
    DA  - 2020/01/15/
    PY  - 2020
    DO  - 10.1000/xyz
    VL  - 12
    IS  - 3
    SP  - 100
    EP  - 110
    J2  - J. Test.
    KW  - alpha
    KW  - beta
    ER  -

Zotero does not write empty fields, and it does not wrap long values: a
multi-line abstract or note is written with its line breaks inside the value.

Differences in how information is encoded
-----------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 16 42 42

   * - Information
     - Original RIS specification and common usage
     - Zotero
   * - Publication type
     - ``TY`` takes one of the standard types, plus some later additions
       (see :doc:`specification`).
     - Uses most standard types, but also writes ``BLOG``, ``DICT``,
       ``ENCYC`` and ``MANSCPT``. Conference papers are exported as
       ``CONF``; ``CPAPER`` is only recognized when importing. Item types
       with no RIS equivalent are mapped to a shared type: letters and
       interviews both become ``PCOMM``, and e-mails, instant messages and
       forum posts all become ``ICOMM``. Web pages are exported as
       ``ELEC`` and anything else as ``GEN``.
   * - Primary title
     - ``T1``, ``TI``, ``CT`` or ``BT``.
     - Exports ``TI``. Imports ``TI`` and ``T1``.
   * - Journal name
     - ``JF`` or ``JO`` hold the full name, but many sources use ``T2``.
     - Exports the full name of a journal, magazine or newspaper in
       ``T2``. On import it also reads ``JF``.
   * - Journal abbreviation
     - ``JA`` is the standard abbreviation. ``J1`` and ``J2`` are
       user-defined.
     - Exports the abbreviation in ``J2``. On import ``J2``, ``JA`` and,
       for most item types, ``JO`` are all read as the abbreviation
       (``JO`` is read as the conference name for conference papers).
   * - Authors
     - ``AU`` or ``A1``, one author per tag, as
       ``LastName, FirstName, Suffix``.
     - Exports ``AU``. The meaning of ``A2`` and ``A3`` depends on the
       item type. For example, ``A2`` is the editor of a journal article,
       book chapter or conference paper, the series editor of a book or
       report, and the performer of an audio recording. ``A3`` is the
       contributor of a thesis.
   * - Publication date
     - ``PY`` and ``Y1`` hold ``YYYY/MM/DD/extra info``.
     - ``PY`` holds the year only. ``DA`` holds the full date as
       ``YYYY/MM/DD/part``, with empty fields left blank, so a year-only
       date becomes ``2020///``. If Zotero cannot parse the date it writes
       the original text in ``DA`` and ``PY``. ``Y1`` is treated as
       ``DA`` when reading older files.
   * - Abstract
     - ``AB`` or ``N2``, sometimes both.
     - Exports ``AB``. Reads both.
   * - DOI
     - ``DO``, although some sources use ``M3``.
     - Exports ``DO``. Also reads ``M3``.
   * - Keywords
     - One ``KW`` tag per keyword.
     - Same. Zotero tags are exported as keywords.
   * - Notes
     - ``N1``.
     - Exports notes in ``N1`` (HTML markup is kept), unless note export is
       turned off.
   * - Attachments
     - ``L1`` is a link to a PDF, ``L2`` to the full text and ``L4`` to
       images.
     - Uses ``L1`` for PDF attachments, ``L2`` for HTML attachments and
       ``L4`` for any other attachment.
   * - Access date
     - ``Y2``.
     - Same. Written in the ``YYYY/MM/DD/`` format.
   * - Library catalogue data
     - ``DB`` and ``DP``, ``AN``, ``CN``.
     - Same, mapped to the Zotero fields ``archive``, ``libraryCatalog``,
       ``archiveLocation`` and ``callNumber``.
   * - Encoding and line endings
     - Not enforced.
     - UTF-8 by default, with ``\r\n`` line endings. See :doc:`encodings`.

Reading: how Zotero is more lenient
-----------------------------------

Zotero's importer is deliberately forgiving, since it must cope with files
from many sources. The parser in ``gris`` is stricter. The differences that
matter if you process the same files with both are:

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Situation
     - Zotero
     - ``gris``
   * - Tag separator
     - Accepts one or two spaces before the dash (``TY - JOUR`` and
       ``TY  - JOUR``). Also accepts empty values with no trailing space.
     - Requires two spaces and a dash (``TY  -``). A file using one space
       raises ``OSError`` ("No valid RIS content found").
   * - Record without ``ER``
     - Forgiven: a new ``TY`` starts a new record.
     - A new ``TY`` before ``ER`` raises ``OSError``. If the file ends
       without ``ER``, the last record is dropped with a warning, or an
       error if ``allow_truncated=False``.
   * - Tags before the first ``TY``
     - A missing ``TY`` is tolerated.
     - Raises ``OSError`` ("Invalid start tag").
   * - Text between records
     - Ignored.
     - Skipped only before the first valid tag. Later it raises
       ``OSError`` ("Expected start tag").
   * - Multi-line values
     - Continuation lines are joined with a space, except for ``AB``,
       ``N1``, ``N2`` and ``RN``, where line breaks are kept when the text
       looks hard-wrapped, and ``KW`` and ``L1`` to ``L3``, where they
       are always kept.
     - Always joins continuation lines with ``\n`` after stripping each
       one.
   * - Unknown or unsupported tags
     - Ignored by default. A hidden preference makes Zotero store them in
       a note instead.
     - Kept in the dictionary as they are.

What gris does about it
-----------------------

``gris`` does not convert records to a common model. It returns the tags as
they were read and offers accessor functions that try the tags used by
different sources in order of preference:

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Function
     - Tags tried, in order
     - Zotero case
   * - ``get_title``
     - ``TI``
     - Matches the ``TI`` that Zotero exports. ``T1`` and ``CT`` are not
       used.
   * - ``get_authors``
     - ``AU``, otherwise ``A1``
     - Matches ``AU``.
   * - ``get_journal``
     - ``JO``, ``T2``, ``JF``, ``JA``, ``J2``, ``J1``
     - Finds the journal in ``T2``. Falls back to the abbreviation in
       ``J2`` if there is no other name.
   * - ``get_pubyear``
     - ``PY``, ``Y1``, ``DA``, taking the first four-digit year
     - Gets the year from ``PY``, or from ``DA`` when Zotero left ``PY``
       out.
   * - ``get_pubdate``
     - ``DA``, ``Y1``, ``PY``, the first one with a year
     - Returns the most detailed date. Pass it to ``parse_pubyear`` to
       split it into year, month, day and extra information. Free text
       dates give the year only.
   * - ``get_abstract``
     - ``AB``, otherwise ``N2``
     - Matches ``AB``.
   * - ``get_keywords``
     - ``KW``
     - Matches ``KW``.

``check_conforms(ref, zotero=True)`` accepts the Zotero-specific publication
types (``BLOG``, ``DICT``, ``ENCYC`` and ``MANSCPT``) in addition to the
original ones. Without ``zotero=True`` those records are reported as not
conforming to the standard.

Known gaps
~~~~~~~~~~

* ``get_title`` only reads ``TI``. Records from sources that put the title
  in ``T1`` or ``CT`` return ``NA``.
* The strictness differences in the table above are not relaxed in
  ``read_ris``.
* ``get_journal`` returns the secondary title (``T2``) for any item type, so
  for a book chapter it returns the book title.
