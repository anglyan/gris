Tutorial
========

This tutorial will guide you through using ``gris`` to read, process, and work with RIS-formatted bibliographic data.

What is RIS?
------------

RIS (Research Information Systems) is a standardized tag-based file format for bibliographic citations.
It is widely supported by reference management software and digital libraries. RIS files contain bibliographic records,
with each record consisting of tags (two-letter codes) followed by content.

Scientific publishers often use RIS as an output format for references. In fact, Nature publishing only exports RIS files.
One of the challenges, though, is that publishers get creative and modify the output format in ways that were not
in the original standard. For instance, AIP adds some metadata at the beginning of the file that trips parsers.


How gris Works
--------------

``gris`` transforms references in RIS format into Python dictionaries. Each bibliographic record becomes a dictionary where:

- **Keys** are the two-letter RIS tags (e.g., ``TY``, ``AU``, ``TI``)
- **Values** contain the corresponding bibliographic data:

  - Single-occurrence tags are stored as strings
  - Multi-occurrence tags (like multiple authors) are stored as lists of strings

Basic Usage: Reading RIS Files
-------------------------------

The primary function for reading RIS files is ``read_ris()``. Here's a simple example:

.. code-block:: python

   from gris import read_ris

   # Read a RIS file
   references = read_ris("myreferences.ris")

   # references is now a list of dictionaries
   print(f"Found {len(references)} references")

Understanding the Output Format
--------------------------------

Example RIS Input
~~~~~~~~~~~~~~~~~

Here's what a typical RIS file looks like:

.. code-block:: text

   TY  - JOUR
   AU  - Smith, John
   AU  - Doe, Jane
   PY  - 2025
   TI  - Introduction to Atomic Layer Deposition
   JO  - Journal of Materials Science
   VL  - 42
   IS  - 3
   SP  - 123
   EP  - 145
   DO  - 10.1234/example.doi
   ER  -

Python Dictionary Output
~~~~~~~~~~~~~~~~~~~~~~~~~

After reading with ``gris``, this becomes:

.. code-block:: python

   {
       'TY': 'JOUR',
       'AU': ['Smith, John', 'Doe, Jane'],  # Multiple authors as a list
       'PY': '2025',
       'TI': 'Introduction to Atomic Layer Deposition',
       'JO': 'Journal of Materials Science',
       'VL': '42',
       'IS': '3',
       'SP': '123',
       'EP': '145',
       'DO': '10.1234/example.doi'
   }

Working with References
-----------------------

Accessing Data
~~~~~~~~~~~~~~

Once you've read a RIS file, you can access and process the data:

.. code-block:: python

   from gris import read_ris

   references = read_ris("myreferences.ris")

   for ref in references:
       # Access single-value fields
       title = ref.get('TI', 'No title')
       year = ref.get('PY', 'Unknown year')
       doi = ref.get('DO', 'No DOI')

       # Access multi-value fields (like authors)
       authors = ref.get('AU', [])

       print(f"Title: {title}")
       print(f"Year: {year}")
       print(f"Authors: {', '.join(authors)}")
       print(f"DOI: {doi}")
       print("-" * 50)

Filtering References
~~~~~~~~~~~~~~~~~~~~

You can filter references based on criteria:

.. code-block:: python

   from gris import read_ris

   references = read_ris("myreferences.ris")

   # Find all journal articles from 2025
   articles_2025 = [ref for ref in references
                    if ref.get('TY') == 'JOUR' and ref.get('PY') == '2025']

   # Find all references with a specific author
   smith_papers = [ref for ref in references
                   if 'AU' in ref and any('Smith' in author for author in ref['AU'])]

Common RIS Tags
---------------

Here are some frequently used RIS tags:

========  ===================================
Tag       Meaning
========  ===================================
TY        Type of reference (e.g., JOUR, BOOK)
AU        Author(s)
TI        Title
JO        Journal name
PY        Publication year
VL        Volume
IS        Issue
SP        Start page
EP        End page
AB        Abstract
DO        DOI (Digital Object Identifier)
UR        URL
ER        End of reference (marker)
========  ===================================

Advanced Usage
--------------

Web of Knowledge Format
~~~~~~~~~~~~~~~~~~~~~~~

``gris`` also supports the older Web of Knowledge format using the ``wok`` parameter:

.. code-block:: python

   from gris import read_ris

   # Read Web of Knowledge formatted files
   references = read_ris("wok_export.txt", wok=True)

Converting to JSON
~~~~~~~~~~~~~~~~~~

You can save references as JSON for use with other tools:

.. code-block:: python

   from gris import read_ris, write_json

   # Read RIS file
   references = read_ris("myreferences.ris")

   # Save as JSON
   write_json("myreferences.json", references)

Writing RIS Files
~~~~~~~~~~~~~~~~~

You can also write references back to RIS format:

.. code-block:: python

   from gris import read_ris, write_ris

   # Read references
   references = read_ris("input.ris")

   # Modify references (e.g., filter or update)
   filtered_refs = [ref for ref in references if ref.get('PY') == '2025']

   # Write back to RIS format
   write_ris("output.ris", filtered_refs)

Error Handling
--------------

``gris`` will raise an ``IOError`` if it encounters malformed RIS files:

.. code-block:: python

   from gris import read_ris

   try:
       references = read_ris("myfile.ris")
   except IOError as e:
       print(f"Error reading RIS file: {e}")

Common errors include:

- Missing start or end tags
- Invalid tag format
- Empty files with no valid RIS content

Next Steps
----------

- Explore the :doc:`specification` for details on the RIS format
- Check the :doc:`apidocs/documentation` for complete API reference
- Examine the ``examples/`` directory in the source code for more usage examples
