RIS file format specification
=============================

The `RIS data format <https://en.wikipedia.org/wiki/RIS_(file_format)>`_ is
a tag based file format containing one or more citations. A sample file
is shown here:

.. code-block:: ignore

    TY  - JOUR
    AU  - Spitz, François
    AU  - Furlong, Eileen E. M.
    PY  - 2012
    DA  - 2012/09/01
    TI  - Transcription factors: from enhancer binding to developmental control
    JO  - Nature Reviews Genetics
    SP  - 613
    EP  - 626
    VL  - 13
    IS  - 9
    AB  - Genetic studies during the past decades have revealed tightly regulated transcriptional networks that control robust developmental programs. However, this deterministic view of development contrasts with recent genomic studies that suggest that the multiple steps of transcription are by themselves rather leaky.Although any single transcription factor (TF) can typically bind to thousands of sites throughout the genome, cis-regulatory activity at enhancers requires the concerted action of multiple binding events (which can be homotypic or heterotypic).TFs bind to enhancers in a combinatorial manner, which is facilitated through direct and indirect cooperative mechanisms. The combinatorial nature of enhancer occupancy allows genes to be regulated in complex patterns in both space and time.DNA and proteins can act together as a scaffold to cooperatively recruit TFs to enhancers.Enhancers undergo progressive changes during development, in which their occupancy by TFs, and the position of nucleosomes with or without post-translational modifications, reflect their inactive, poised or active state.Pioneer TFs recruit chromatin-remodelling factors to reposition nucleosomes, thus facilitating the occupancy of other TFs at subsequent developmental stages.Enhancer priming can occur through many different mechanisms. For example, some TF binding events may serve as placeholders to prevent nucleosome repositioning.Partially redundant enhancers can act to buffer changes in environmental conditions to ensure robust developmental progression.Multiple elements regulating the same gene seem to assemble in a three-dimensional structure with the promoter, and can have synergistic or repressive influences on each other.
    SN  - 1471-0064
    UR  - https://doi.org/10.1038/nrg3207
    DO  - 10.1038/nrg3207
    ID  - Spitz2012
    ER  - 

Tag format
----------

Tags are six-character long, with the following structure:

.. code-block:: ignore

    XXss-s

where ``X`` represents and alphanumeric character, ``s`` a space, and 
``-`` is a dash.

Each new tag must start in a new line. However, the content from a tag can
extend to multiple lines. Tags can be repeated, for instance to describe
multiple authors or keywords in a reference.

Bibliographic record format
---------------------------

A bibliographic record must start with a ``TY`` tag followed by the publication
type. Publication types in the standard implementation include:

.. code-block:: ignore

    ABST, ADVS, ART, BILL, BOOK, CASE, CHAP, COMP, 
    CONF, CTLG, DATA, ELEC, GEN, HEAR, ICOMM, INPR, JFULL,
    JOUR, MAP, MGZN, MPCT, MUSIC, NEWS, PAMP, PAT, PCOMM, RPTR,
    SER, SLIDE, SOUND, STAT, UNBIL, UNPB, VIDEO

A record must end with an ``ER`` tag. The rest of the tags can be
in any order.

Extensions to the standard
~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to the publication types listed above, other publication types
that can be found include:

.. code-block:: ignore

    CLSWK, EBOOK, ECHAP, EJOUR

Bibtex-compatible publication types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The set of publication types covered by the RIS format is larger than
that of BibTeX. The subset of types that have a clear BibTeX counterpart
include:

.. code-block:: ignore

    BOOK, CHAP, CLSWK, CONF, CPAPER, EBOOK, ECHAP, EJOUR,
    ELEC, GEN, JOUR, MGZN, RPRT, SER, THES, UNPB

Standard tags
-------------

A list of the standard tags with basic definitions are provided here::

    ris_tags_ref = {
        'TY': "Type of reference - first tag in a record",
        'A1': "Primary Authors - usually mapped to AU",
        'A2': "Secondary Authors - normally used for Editors",
        'A3': "Tertiary Authors",
        'A4': "Subsidiary Authors",
        'AB': "Notes - usually used for abstract and mapped to N2",
        'AD': "Author Address",
        'AN': "Accession Number",
        'AU': "Author",
        'AV': "Location in Archives",
        'BT': "This field maps to T2 except for Whole Book and Unpublished Work references",
        'C1': "Custom 1",
        'C2': "Custom 2",
        'C3': "Custom 3",
        'C4': "Custom 4",
        'C5': 'Custom 5',
        'C6': "Custom 6 - As of 2023 some references in WoS use this for Year + Month info",
        'C7': "Custom 7",
        'C8': 'Custom 8',
        'CA': "Caption",
        'CN': "Call Number",
        'CP': "Misc",
        'CT': "Title of unpublished reference",
        'CY': "Place Published",
        'DA': "Date",
        'DB': "Name of Database",
        'DO': "DOI",
        'DP': "Database Provider",
        'ED': "Editor",
        'EP': "End Page",
        'ET': "Edition",
        'ID': "Reference ID",
        'IS': "Issue number",
        'J1': "Periodical name: user abbreviation",
        'J2': "Alternate Title - Journal name for journals",
        'JA': "Periodical name: standard abbreviation",
        'JF': "Journal/Periodical name: full format",
        'JO': "Journal/Periodical name: full format",
        'KW': "Keywords",
        'L1': "Link to PDF",
        'L2': "Link to Full-text.",
        'L3': "Related Records",
        'L4': "Image(s)",
        'LA': "Language",
        'LB': "Label",
        'LK': "Website Link",
        'M1': "Number",
        'M2': "Miscellaneous 2",
        'M3': "Type of Work",
        'N1': "Notes",
        'N2': "Abstract",
        'NV': "Number of Volumes",
        'OP': "Original Publication",
        'PB': "Publisher",
        'PP': "Publishing Place",
        'PY': "Publication year",
        'RI': "Reviewed Item",
        'RN': "Research Notes",
        'RP': "Reprint Edition",
        'SE': "Section",
        'SN': "ISBN/ISSN",
        'SP': "Start Page",
        'ST': "Short Title",
        'T1': "Primary Title",
        'T2': "Secondary Title (journal title, if applicable)",
        'T3': "Title series",
        'TA': "Translated Author",
        'TI': "Title",
        'TT': "Translated Title",
        'U1': "User definable 1",
        'U3': "User definable 3",
        'U4': "User definable 4",
        'U5': "User definable 5",
        'UR': "URL",
        'VL': "Volume number",
        'VO': "Published Standard number",
        'Y1': "Primary Date",
        'Y2': "Access Date",
        'ER': "End tag in a record"
    }

This list is included in ``gris`` for reference purposes.

Specific fields information
---------------------------

One of the challenges of the RIS format is that there is not
one way of describing key fields used for references. In fact,
both publishers and digital libraries use different tags
for the same fields, including in some cases their own
extensions to the standard.


Titles
~~~~~~

The tags: ``T1``, ``TI``, ``CT``, and ``BT`` are assigned
to the primary title of the record, with ``BT`` used only
for Whole Book and Unpublished work references.

The tags: ``T2`` and ``BT`` are used for the secondary titles.
Some journals export the Journal name using ``T2``.

Authors
~~~~~~~

The tags: ``A1`` and ``AU`` are used for the primary authors
of a reference, with each tag containing the name of only one
author. The author name is encoded as follows:

.. code-block:: ignore

    LastName, FirstName, Suffix

Two other tages, ``A2`` and ``ED``, are used to list the
names of Editors.

Publication date
~~~~~~~~~~~~~~~~

The tags ``Y1`` and ``PY`` are used to encode the publication date
information, which should be in the format:

.. code-block:: ignore

    YYYY/MM/DD/extra info

As of March 2023 some articles exported from WebOfScience use
the ``C6`` tag to describe the month and year of publication as:

.. code-block:: ignore

    Month YYYY

It is unclear why is this the case and why only some of the publications 
seem to be affected


Abstracts
~~~~~~~~~

Abstracts are captured by either the ``N2`` or ``AB`` tags. Sometimes both.

Journal titles
~~~~~~~~~~~~~~

The standard establishes ``JF`` and ``JO`` as the tags with the periodical
name, with ``JA`` used to specify the standard journal abbreviation and
``J1`` and ``J2`` used for user-defined abbreviations. In practice, though,
many sources use ``T2`` for the full journal name.

There is a significan lack of consistency on the use of these tags
among publishers. For instance, some use ``JO`` for the abbreviated journal
name instead of the full name, as described in the specification.

Volume, Issues, and Pages
~~~~~~~~~~~~~~~~~~~~~~~~~

``VL`` and ``IS`` are used for volumes and issues.
Start and end page are encoded with the ``SP`` and ``EP`` tags, respectively.



