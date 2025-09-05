"""File path based utilities."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from zipfile import Path as ZipPath


# ------------------------------------------------------------------------------
def walkpath(path: Path | ZipPath) -> Iterator[Path | ZipPath]:
    """Walk a directory and yield all files in it."""
    for item in path.iterdir():
        if item.is_dir():
            yield from walkpath(item)
        else:
            yield item


# ------------------------------------------------------------------------------
def relative_path(root: Path, path: Path | str) -> Path:
    """
    Ensure a relative path is contained within a root path.

    This is a bit crude but is intented to make sure a path doesn't stray outside
    a given root using relative path trickery.

    :param root:        Root path.
    :param path:        A relative path.
    :return:            A resolved relative path with respect to root.

    :raises ValueError: If path is not a relative path or not contained
                        within root.
    """

    if Path(path).is_absolute():
        raise ValueError(f'{path} is not a relative path')

    return (root / path).resolve().relative_to(root.resolve())
