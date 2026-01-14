.. gris documentation master file, created by
   sphinx-quickstart on Fri Apr 21 01:29:59 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

gris documentation
==================

About
-----

``gris`` is a lightweight parser for RIS files.

The `RIS data format <https://en.wikipedia.org/wiki/RIS_(file_format)>`_
is a standardized format to exchange citation and bibliographic data. It 
is widely used by digital libraries and library catalogs.

This package implements a parser and conversion tools to extract data from
a bibliography and store data in other more common formats, such as ``json``.


Install
-------

Install ``gris`` directly using ``pip``::

   pip install gris

Alternatively, bleeding edge code can be found in `github <https://github.com/anglyan/gris>`_


Usage
-----

The main way of reading RIS files is using ``read_ris``::

   from gris import read_ris

   data = read_ris("myreferences.ris")



Table of contents
-----------------

.. toctree::
   :maxdepth: 1

   tutorial
   specification
   apidocs/documentation



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
