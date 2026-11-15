# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Make the package importable for autodoc even when it is not pip-installed
# (e.g. on Read the Docs, which only installs docs/requirements.txt).
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------

project = 'gris'
copyright = '2013-2026, Angel Yanguas-Gil'
author = 'Angel Yanguas-Gil'
release = '0.9.1'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_copybutton',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = 'furo'
html_title = 'gris'
html_theme_options = {
    'source_repository': 'https://github.com/anglyan/gris/',
    'source_branch': 'master',
    'source_directory': 'docs/source/',
}
