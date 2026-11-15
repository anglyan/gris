Specific fields information
===========================

One of the challenges of the RIS format is that there is not
one way of describing key fields used for references. In fact,
both publishers and digital libraries use different tags
for the same fields, including in some cases their own
extensions to the standard.

`gris` sidesteps this problem by returning a dictionary with the tags as keys.
To improve usability, `gris` has a series of helper functions 
to extract specific information from the records. Here is a summary of the different
tags used by different services.

A worked example
----------------

All the examples in this page use the following RIS record, saved
as ``example.ris``:

.. code-block:: text

    TY  - JOUR
    AU  - Smith, John
    AU  - Doe, Jane, Jr.
    A2  - Rivera, Maria
    TI  - Introduction to Atomic Layer Deposition
    T2  - Journal of Materials Science
    DA  - 2025/03/14/
    PY  - 2025
    AB  - We review the basic principles of atomic layer deposition.
    KW  - thin films
    KW  - ALD
    VL  - 42
    IS  - 3
    SP  - 123
    EP  - 145
    ER  -

:func:`gris.read_ris` returns a list with one dictionary per record. Tags
that appear once are stored as strings, and tags that appear more than once
(here ``AU`` and ``KW``) are stored as lists of strings:

.. code-block:: python

    >>> from gris import read_ris
    >>> refs = read_ris("example.ris")
    >>> len(refs)
    1
    >>> ref = refs[0]
    >>> ref
    {'TY': 'JOUR',
     'AU': ['Smith, John', 'Doe, Jane, Jr.'],
     'A2': 'Rivera, Maria',
     'TI': 'Introduction to Atomic Layer Deposition',
     'T2': 'Journal of Materials Science',
     'DA': '2025/03/14/',
     'PY': '2025',
     'AB': 'We review the basic principles of atomic layer deposition.',
     'KW': ['thin films', 'ALD'],
     'VL': '42',
     'IS': '3',
     'SP': '123',
     'EP': '145'}

The ``ref`` dictionary is the starting point for all the helper functions
described below. Note that the example has no ``JO`` or ``JF`` tag and that
the date appears in both ``DA`` and ``PY``, which is a common situation. The helpers
take care of choosing the right tag.

Two general purpose helpers are used throughout the page to read tags for which
there is no dedicated function: ``tag2string`` joins lists with spaces, while ``tag2list`` wraps single values in
a list, so both work regardless of whether the tag appeared once or several times.

.. code-block:: python

    >>> from gris import tag2string, tag2list
    >>> tag2string(ref, 'VL')
    '42'
    >>> tag2list(ref, 'AU')
    ['Smith, John', 'Doe, Jane, Jr.']
    >>> tag2string(ref, 'DO')   # not in the record
    'NA'


Titles
------

The tags: ``T1``, ``TI``, ``CT``, and ``BT`` are assigned
to the primary title of the record, with ``BT`` used only
for Whole Book and Unpublished work references.

The tags: ``T2`` and ``BT`` are used for the secondary titles.
Some journals export the Journal name using ``T2``.

.. code-block:: python

    get_title(ref, strip_newlines=False)

``get_title`` returns the content of the ``TI`` tag, falling back to ``T1``
if ``TI`` is not present (AIP and ACS, for instance, use ``T1``), or ``'NA'``
if neither is present. Some sources wrap long titles over several lines, see
:ref:`line-breaks` for the ``strip_newlines`` option. There is no dedicated
function for secondary titles, which can be read with ``tag2string``:

.. code-block:: python

    >>> get_title(ref)
    'Introduction to Atomic Layer Deposition'
    >>> tag2string(ref, 'T2')
    'Journal of Materials Science'

Authors
-------

The tags: ``A1`` and ``AU`` are used for the primary authors
of a reference, with each tag containing the name of only one
author. The author name is encoded as follows:

.. code-block:: text

    LastName, FirstName, Suffix

Two other tages, ``A2`` and ``ED``, are used to list the
names of Editors.

.. code-block:: python

    get_authors(ref)
    parse_author(v)

``get_authors`` returns the list of authors, using ``AU`` and falling
back to ``A1`` if ``AU`` is not present. It returns an empty list if there
are no authors. ``parse_author`` splits one of those strings into a
``(last name, first name, suffix)`` tuple, using ``None`` for the parts
that are missing. Editors have no dedicated function and can be read
with ``tag2list``:

.. code-block:: python

    >>> authors = get_authors(ref)
    >>> authors
    ['Smith, John', 'Doe, Jane, Jr.']
    >>> [parse_author(a) for a in authors]
    [('Smith', 'John', None), ('Doe', 'Jane', ' Jr.')]
    >>> tag2list(ref, 'A2')
    ['Rivera, Maria']

.. note::

    The suffix returned by ``parse_author`` is not stripped, so it keeps the
    leading space that follows the comma.

Publication date
----------------


The tags ``Y1`` and ``PY`` are used to encode the publication date
information, which should be in the format:

.. code-block:: text

    YYYY/MM/DD/extra info

As of March 2023 some articles exported from WebOfScience use
the ``C6`` tag to describe the month and year of publication as:

.. code-block:: text

    Month YYYY

It is unclear why is this the case and why only some of the publications 
seem to be affected

.. code-block:: python

    get_pubdate(ref)
    get_pubyear(ref)
    parse_pubyear(v)

``get_pubdate`` returns the raw date string, trying ``DA``, ``Y1`` and
``PY`` in that order so that the most detailed date available is returned,
and ``'NA'`` if none of them contains a year. ``get_pubyear`` returns only the four digit
year as a string, trying ``PY``, ``Y1`` and ``DA``, and ``'NA'`` if it cannot be
determined. ``parse_pubyear`` splits a date string into a
``(year, month, day, extra)`` tuple, where the fields that are empty or
cannot be determined are ``None``:

.. code-block:: python

    >>> get_pubdate(ref)
    '2025/03/14/'
    >>> get_pubyear(ref)
    '2025'
    >>> parse_pubyear(get_pubdate(ref))
    ('2025', '03', '14', None)

If the date is free text, as in the ``C6`` tag from WebOfScience, only the year is
extracted:

.. code-block:: python

    >>> parse_pubyear('March 2023')
    ('2023', None, None, None)


Abstracts
---------

Abstracts are captured by either the ``N2`` or ``AB`` tags. Sometimes both.

.. code-block:: python

    get_abstract(ref, strip_newlines=False)

``get_abstract`` returns the content of ``AB`` if present and of ``N2``
otherwise, or ``'NA'`` if neither is present. See :ref:`line-breaks` for
the ``strip_newlines`` option:

.. code-block:: python

    >>> get_abstract(ref)
    'We review the basic principles of atomic layer deposition.'

Journal titles
--------------

The standard establishes ``JF`` and ``JO`` as the tags with the periodical
name, with ``JA`` used to specify the standard journal abbreviation and
``J1`` and ``J2`` used for user-defined abbreviations. In practice, though,
many sources use ``T2`` for the full journal name.

There is a significan lack of consistency on the use of these tags
among publishers. For instance, some use ``JO`` for the abbreviated journal
name instead of the full name, as described in the specification.

.. code-block:: python

    get_journal(ref, strip_newlines=False)

``get_journal`` tries the tags in order of preference: ``JO``, ``T2``,
``JF`` and, as a last resort, the abbreviations ``JA``, ``J2`` and ``J1``.
It returns ``'NA'`` if none is present. See :ref:`line-breaks` for the
``strip_newlines`` option. In the example record there is no ``JO``,
so the journal name is taken from ``T2``:

.. code-block:: python

    >>> get_journal(ref)
    'Journal of Materials Science'

DOI
---

The DOI is stored in the ``DO`` tag, but not every source fills it in, and
many include the DOI in the URL (``UR``) instead, as in
``https://doi.org/10.1021/acsami.1c00649``.

.. code-block:: python

    get_doi(ref)

``get_doi`` returns the bare DOI, without any prefix, or ``'NA'`` if none is
found. It looks first at ``DO`` and then at ``UR`` and the link tags
``L1`` to ``L4``, extracting the DOI from the text so that values such as
``doi:10.1021/acsami.1c00649`` or a ``doi.org`` URL are also handled.
URL encoded characters are decoded, and query strings and fragments are
discarded. Links that do not contain a DOI, such as a ScienceDirect ``pii``
URL, are ignored:

.. code-block:: python

    >>> get_doi({'UR': 'https://doi.org/10.1021/acsami.1c00649'})
    '10.1021/acsami.1c00649'
    >>> get_doi(ref)    # the example record has no DOI
    'NA'

.. _line-breaks:

Line breaks in text fields
--------------------------

Some sources wrap long titles and abstracts over several lines, so the
value read from the file contains embedded line breaks. ACS, for instance,
exports:

.. code-block:: text

    T1  - Intelligent
    Agents for the Optimization of Atomic
    Layer Deposition

By default the helpers return the text exactly as it appears in the file:

.. code-block:: python

    >>> get_title(ref)
    'Intelligent\nAgents for the Optimization of Atomic\nLayer Deposition'

``get_title``, ``get_abstract`` and ``get_journal`` accept a
``strip_newlines`` argument. If it is ``True`` each line break is replaced
by a single space:

.. code-block:: python

    >>> get_title(ref, strip_newlines=True)
    'Intelligent Agents for the Optimization of Atomic Layer Deposition'

The same cleaning is available for any string through ``remove_newlines``,
for instance to clean the output of ``tag2string``:

.. code-block:: python

    >>> from gris import remove_newlines
    >>> remove_newlines('Atomic\n Layer\r\nDeposition')
    'Atomic Layer Deposition'

Whitespace around each line break is collapsed together with it, and leading
and trailing whitespace is removed. Text without line breaks is returned
unchanged.

.. note::

    A word hyphenated across a line break, such as ``deposi-`` followed by
    ``tion``, becomes ``deposi- tion``, since it cannot be told apart from a
    real hyphenated compound.

Volume, Issues, and Pages
-------------------------

``VL`` and ``IS`` are used for volumes and issues.
Start and end page are encoded with the ``SP`` and ``EP`` tags, respectively.

.. code-block:: python

    get_volume(ref)
    get_issue(ref)
    get_startpage(ref)
    get_endpage(ref)

Each function returns the content of the corresponding tag as a string, or
``'NA'`` if it is not present. ``get_startpage`` is also used for the
article number when a journal does not use page ranges:

.. code-block:: python

    >>> get_volume(ref)
    '42'
    >>> get_issue(ref)
    '3'
    >>> get_startpage(ref)
    '123'
    >>> get_endpage(ref)
    '145'
