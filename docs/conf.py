# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import datetime
import os
import sys
sys.path.insert(0, os.path.abspath('../app'))

current_year = datetime.datetime.now().year

# -- Project information -----------------------------------------------------

project = 'BioViewer.AMR'
#title = 'Паспорт модели. Версия 1.0'
author = 'BioME LLC'
copyright = f'2019-{current_year}, {author}'

release = '1.0'
current_date = datetime.datetime.today().strftime('%d.%m.%Y')

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'autodocsumm',
    'myst_parser',
    #'sphinx_markdown_builder',
    'sphinxcontrib.mermaid'
]
# mermaid_cmd = "docker run --rm minlag/mermaid-cli"
# mermaid_cmd_shell = True



myst_enable_extensions = [
    "colon_fence",
 ]

# myst_gfm_only = True

autodoc_default_options = {
    'autosummary': True,
    'private-members': True,
    'inherited-members': True
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', '_html', 'Thumbs.db', '.DS_Store', 'node_modules']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'furo'

## Material theme options (see theme.conf for more information)
# html_theme_options = {
#
#     # Set the name of the project to appear in the navigation.
#     'nav_title': 'BioViewer.AMR',
#
#     # Specify a base_url used to generate sitemap.xml. If not
#     # specified, then no sitemap will be built.
#     'base_url': 'https://gitlab.numedy.com/biome/bioviewer.amr',
#
#     # Set the color and the accent color
#     'color_primary': 'blue',
#     'color_accent': 'light-blue',
#
#     # Set the repo location to get a badge with stats
#     'repo_url': 'https://gitlab.numedy.com/biome/bioviewer.amr',
#     'repo_name': 'BioViewer.AMR',
#
#     # Visible levels of the global TOC; -1 means unlimited
#     'globaltoc_depth': 3,
#     # If False, expand all TOC entries
#     'globaltoc_collapse': True,
#     # If True, show hidden TOC entries
#     'globaltoc_includehidden': False,
# }

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
