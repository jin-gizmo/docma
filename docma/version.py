"""Version information for docma."""

from __future__ import annotations

from pathlib import Path

__version__ = (Path(__file__).parent / 'VERSION').read_text().strip()
