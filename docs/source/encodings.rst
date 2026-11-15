Character encodings
===================

The encoding of text files has evolved tremendously over the years. `gris` provides tools
to read text files using different encodings. This is particularly important
for non-ASCII characters. This page summarizes how `gris` deals with this challenge.


Background
----------

There is nothing in a plain text file that declares the type of encoding that
it uses. For modern files, `UTF-8`_ is a common standard. For instance,
Zotero's RIS export has a character encoding option whose default is UTF-8, and the Web of
Knowledge export is UTF-8 with a `byte order mark`_. 
A commmon approach used by older reference managers and publisher exports was to
use the encoding of the system that created them. This means that old files
can use `ASCII`_, `Windows-1252`_ or `Mac Roman`_ depending on the OS.

Some older encodings are subsets of more modern ones: for instance, 
pure ASCII files are valid UTF-8. However, files with accented characters in one of the 8-bit
encodings are not valid UTF-8. Choosing the wrong 8-bit encoding does not always
raise an error: `Latin-1`_ accepts any byte, and other encodings accept many
files, so the result can be garbled text. This is a common problem with
Mac Roman files read as Latin-1 or Windows-1252.

Byte order marks (BOM) are a second rabbit hole: some files using the UTF-8 encoding
start with byte order mark (BOM, the three bytes
``EF BB BF``). If the file is decoded as plain ``utf-8``, the BOM becomes an
invisible character, ``﻿``, at the start of the first line. The practical
consequence is that the first
tag reads ``﻿TY  -`` and no longer matches a standard RIS tag, which may trip
the parser.

A third potential issue are line endings: the RIS specification uses ``\r\n`` line endings,
and Zotero writes them as well. However, files created on Unix systems use ``\n``.

Finally, `Unicode`_ can represent an accented letter as one character or as a letter
followed by a combining accent. The main consequence is that text from different sources may therefore
look identical but not compare as equal.


Python's current approach to encodings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a side note, in Python, ``open(filename)`` without an ``encoding`` argument uses the
locale's preferred encoding. This means that, on most Linux and macOS systems,
the encoding used is UTF-8. On Windows, it is a legacy code page such as ``cp1252``.
There are other exotic cases where it defaults to ASCII.

This OS-specific behavior can lead to errors popping up when files created in one OS are read
in another. For instance, under an ASCII locale, 
reading the name Müller would raise a
``UnicodeEncodeError``. In some cases, such as reading a UTF-8 file with a
single-byte default encoding, the result is gabled text.


How ``gris`` approaches encodings
---------------------------------

Reading RIS files
~~~~~~~~~~~~~~~~~

The signature of ``read_ris`` is:

.. code-block:: python

   read_ris(filename, wok=False, allow_truncated=True, encoding='utf-8-sig')


The optional argument ``encoding`` specificies the expected encoding of the RIS
file. The default behavior is opening files as UTF-8 with the ``utf-8-sig`` codec, 
regardless of the system locale. This ensures consistent behavior across OS and
Python versions. 

With the default ``encoding`` in ``read_ris``:


- Plain UTF-8 files are read correctly.
- The leading BOM is removed if present, so files from Web of Knowledge or other sources
  that write one parse correctly.
- Both ``\n`` and ``\r\n`` line endings are handled, because Python silently converts
  them when reading text files.
- Zotero, most current tools that use default UTF-8 with BOM, and Web of Knowledge should be read correctly
- Legacy pure ASCII files, as a subset of UTF-8, can be read.

The ``encoding`` argument of ``read_ris`` can be used to read files in other
encodings (see Limitations). ``load_json`` also reads with ``utf-8-sig``.

Choosing the encoding
^^^^^^^^^^^^^^^^^^^^^

There are a number of cases that are not covered by the default encoding.

- Old Windows export: Use the ``cp1252`` encoding. This encoding can be recognized by its curly
  quotes and dashes.

- `ISO 8859-1`_ files: Use the ``latin-1`` encoding. Note that this accepts any byte, so it will never
  raise an error.

- Old Mac files: Use ``mac_roman``. This is often mistaken for ``cp1252``.

- Old DOS exports (`Code page 850`_): Could use the ``cp850`` or ``cp437`` encodings.

- `UTF-16`_: Use ``utf-16`.

If you do not know the encoding, the ``file``
command (``file -I`` on macOS) or the ``chardet`` and ``charset-normalizer``
Python packages can suggest one. Check
that the accented characters in the output look right.


Other IO operations
~~~~~~~~~~~~~~~~~~~

``write_ris`` writes UTF-8 without a BOM, the same encoding Zotero uses by
  default. Its function signature:


  .. code-block:: python

     write_ris(filename, entries, native_newlines=False)

Implements using ``\r\n`` line endings on every platform by default, as
required by the RIS specification. However, using ``native_newlines=True``
you can write files using the local platform's line endings 
(``\r\n`` on Windows, ``\n`` elsewhere).

``write_json`` and ``load_json`` do not take an ``encoding`` argument.
``write_json`` writes UTF-8 and keeps non-ASCII characters as they are
(``ensure_ascii=False``). ``load_json`` reads files with the ``utf-8-sig`` codec,


.. _UTF-8: https://en.wikipedia.org/wiki/UTF-8
.. _UTF-16: https://en.wikipedia.org/wiki/UTF-16
.. _ASCII: https://en.wikipedia.org/wiki/ASCII
.. _Latin-1: https://en.wikipedia.org/wiki/ISO/IEC_8859-1
.. _ISO 8859-1: https://en.wikipedia.org/wiki/ISO/IEC_8859-1
.. _Windows-1252: https://en.wikipedia.org/wiki/Windows-1252
.. _Mac Roman: https://en.wikipedia.org/wiki/Mac_OS_Roman
.. _Code page 850: https://en.wikipedia.org/wiki/Code_page_850
.. _byte order mark: https://en.wikipedia.org/wiki/Byte_order_mark
.. _Unicode: https://en.wikipedia.org/wiki/Unicode
