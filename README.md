# README


## About gris


`gris` is a minimalistic tool to read, parse, and
write reference data in
[Refman RIS format](https://en.wikipedia.org/wiki/RIS_(file_format)).

RIS format codifies bibliographic data using a series of tags. There
are variations among publishers: this module supports
both the original standard and the RIS output by Web of Knowledge.

This module has been updated and tested in Python 3.7+. The documentation
can be found in [readthedocs](https://gris.readthedocs.io/en/latest/index.html).

## Install

Install ``gris`` directly using ``pip``:

```
pip install gris
```

## How to use it

### From the command line:

```
python -m gris myrefs.ris AB
```

retrieves and prints out the contents of the tag `AB` (usually used for
abstracts) for all the publications in a reference file.

### From a script or Python program

```
from gris import read_ris

refs = read_ris("myrefs.ris")
```


## Background


`gris` was developed by AYG during his personal time, as a way of transforming
bibliographic data into more machine-readable formats and preserving
all bibliographic data. It eventually found its way to various publications where the work required processing large amounts of bibliographic data.

`gris` imports RIS files with multiple references into a list of dictionaries.


## License


Copyright (C) 2013 Angel Yanguas-Gil

This program is free software, licensed under GPLv2 or later.
A copy of the GPLv2 license is provided in the root directory of the source code.