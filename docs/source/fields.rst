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


Titles
------

The tags: ``T1``, ``TI``, ``CT``, and ``BT`` are assigned
to the primary title of the record, with ``BT`` used only
for Whole Book and Unpublished work references.

The tags: ``T2`` and ``BT`` are used for the secondary titles.
Some journals export the Journal name using ``T2``.

Authors
-------

The tags: ``A1`` and ``AU`` are used for the primary authors
of a reference, with each tag containing the name of only one
author. The author name is encoded as follows:

.. code-block:: text

    LastName, FirstName, Suffix

Two other tages, ``A2`` and ``ED``, are used to list the
names of Editors.

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


Abstracts
---------

Abstracts are captured by either the ``N2`` or ``AB`` tags. Sometimes both.

Journal titles
--------------

The standard establishes ``JF`` and ``JO`` as the tags with the periodical
name, with ``JA`` used to specify the standard journal abbreviation and
``J1`` and ``J2`` used for user-defined abbreviations. In practice, though,
many sources use ``T2`` for the full journal name.

There is a significan lack of consistency on the use of these tags
among publishers. For instance, some use ``JO`` for the abbreviated journal
name instead of the full name, as described in the specification.

Volume, Issues, and Pages
-------------------------

``VL`` and ``IS`` are used for volumes and issues.
Start and end page are encoded with the ``SP`` and ``EP`` tags, respectively.



