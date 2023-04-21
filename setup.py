#Copyright (C) 2013 Angel Yanguas-Gil
#This program is free software, licensed under GPLv2 or later.
#A copy of the GPLv2 license is provided in the root directory of
#the source code.

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name = 'gris',
    description = "parser of RIS and WOK bibliography file format",
    version = '0.7.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author = "Angel Yanguas-Gil",
    author_email = "angel.yanguas@gmail.com",
    url = "https://github.com/anglyan/gris.git",
    packages=find_packages(),
    python_requires=">=3",
    classifiers = ["Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Topic :: Utilities"]
)
