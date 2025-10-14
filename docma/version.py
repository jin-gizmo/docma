"""Version information for docma."""

from importlib.resources import files

import docma

__version__ = files(docma).joinpath('VERSION').read_text().strip()
