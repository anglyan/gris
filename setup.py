#Copyright (C) 2013 Angel Yanguas-Gil
#This program is free software, licensed under GPLv2 or later.
#A copy of the GPLv2 license is provided in the root directory of
#the source code.

from distutils.core import setup
setup(name = 'gris',
    description = "parser of RIS and WOK bibliography file format",
    version = '0.5.0',
    author = "Angel Yanguas-Gil",
    author_email = "angel.yanguas@gmail.com",
    download_url = "https://github.com/anglyan/gris/tarball/0.5.0",
    url = "https://github.com/anglyan/gris.git",
    py_modules = ['gris'],
    package_dir = {'' : 'gris'},
    classifiers = ["Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Topic :: Utilities"]
)

