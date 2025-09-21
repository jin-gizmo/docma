"""Utils to package files into a collection."""

from __future__ import annotations

import zipfile
from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path
from shutil import copy2
from zipfile import ZipFile

from jinja2 import BaseLoader, TemplateNotFound

from docma.exceptions import DocmaPackageError
from .path import relative_path, walkpath

__author__ = 'Murray Andrews'


# ..............................................................................
# region PackageWriter
# ..............................................................................


# ------------------------------------------------------------------------------
class PackageWriter(ABC):
    """Package files up."""

    def __init__(self, path: Path) -> None:
        """Create packager."""
        self.path = path

    def __enter__(self):
        """Create packager context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa: B027
        """Close the package."""
        pass

    @staticmethod
    def new(path: Path | str) -> PackageWriter:
        """Create a new package writer."""
        if isinstance(path, str):
            path = Path(path)
        if path.suffix.lower() == '.zip':
            return ZipPackageWriter(path)
        return DirPackageWriter(path)

    @abstractmethod
    def write_string(self, content: str, file: Path | str):
        """
        Create a new file in the package with the specified content.

        :param content:     The content to be added.
        :param file:        The name of the file to be created. This must be a
                            relative path.
        :return:            The relative path to the created file.
        """
        raise NotImplementedError('write_string')

    @abstractmethod
    def write_bytes(self, content: bytes, file: Path | str) -> Path:
        """
        Create a new file in the package with the specified content.

        :param content:     The content to be added.
        :param file:        The name of the file to be created. This must be a
                            relative path.
        :return:            The relative path to the created file.
        """
        raise NotImplementedError('write_bytes')

    @abstractmethod
    def add_file(self, src: Path, dst: Path | str):
        """
        Create a new file in the package from the specified file.

        :param src:    The path to the source file.
        :param dst:    The name of the file to be created. This must be a
                        relative path.

        """
        raise NotImplementedError('add_file')

    @abstractmethod
    def exists(self, file: Path | str) -> bool:
        """Check if a file exists in the package."""
        raise NotImplementedError('exists')


# ------------------------------------------------------------------------------
class DirPackageWriter(PackageWriter):
    """Package files into a directory."""

    def __init__(self, path: Path) -> None:
        """Create a directory package writer."""
        super().__init__(path)
        if not path.exists():
            path.mkdir()
        elif not path.is_dir():
            raise ValueError(f'{path} is not a directory.')

    def write_string(self, content: str, file: Path | str) -> Path:
        """Create a new file in the package with the specified content."""
        dst_path = self.path / relative_path(self.path, file)
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        dst_path.write_text(content)
        return dst_path

    def write_bytes(self, content: bytes, file: Path | str) -> Path:
        """Create a new file in the package with the specified content."""
        dst_path = self.path / relative_path(self.path, file)
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        dst_path.write_bytes(content)
        return dst_path

    def add_file(self, src: Path, dst: Path | str) -> Path:
        """Add a file to the package."""
        dst_path = self.path / relative_path(self.path, dst)
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        copy2(src, dst_path)
        return dst_path

    def exists(self, file: Path | str) -> bool:
        """Check if a file exists in the package."""
        return (self.path / file).exists()


# ------------------------------------------------------------------------------
class ZipPackageWriter(PackageWriter):
    """Package files into zip file."""

    def __init__(self, path: Path) -> None:
        """Create a zip packager."""
        super().__init__(path)
        self._zip = ZipFile(self.path, 'w', allowZip64=True)

    def write_string(self, content: str, file: Path | str) -> Path:
        """Create a new file in the ZIP file with the specified content."""
        dst_path = relative_path(self.path, file)
        self._zip.writestr(str(dst_path), content)
        return dst_path

    def write_bytes(self, content: bytes, file: Path | str) -> Path:
        """Create a new file in the ZIP file with the specified content."""
        dst_path = relative_path(self.path, file)
        self._zip.writestr(str(dst_path), content)
        return dst_path

    def add_file(self, src: Path, dst: Path | str) -> Path:
        """Add a file to the zip file."""
        dst_path = relative_path(self.path, dst)
        self._zip.write(src, str(dst_path))
        return dst_path

    def exists(self, file: Path | str) -> bool:
        """Check if a file exists in the package."""
        try:
            self._zip.getinfo(str(file))
            return True
        except KeyError:
            return False

    def close(self):
        """Close the zip file."""
        self._zip.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the zip file."""
        self.close()
        if exc_type:
            self.path.unlink(missing_ok=True)


# ..............................................................................
# endregion PackageWriter
# ..............................................................................

# ..............................................................................
# region PackageReader
# ..............................................................................


# ------------------------------------------------------------------------------
class PackageReader(ABC, BaseLoader):
    """Access package files."""

    def __init__(self, path: Path) -> None:
        """Create package reader."""
        self.path = path

    def __enter__(self):
        """Create package reader context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa: B027
        """Close the package."""
        pass

    @staticmethod
    def new(path: Path | str) -> PackageReader:
        """Create a new package reader."""
        if isinstance(path, str):
            path = Path(path)
        if path.is_dir():
            return DirPackageReader(path)
        if path.suffix.lower() == '.zip':
            return ZipPackageReader(path)

        raise DocmaPackageError(f'{path} is not a ZIP file or directory.')

    @abstractmethod
    def read_text(self, file: Path | str) -> str:
        """
        Read a text file from the package.

        :param file:    The path of the file to be read, relative to the package root.
        :return:        The content of the file.
        """
        raise NotImplementedError('readf_text')

    @abstractmethod
    def read_bytes(self, file: Path | str) -> bytes:
        """
        Read a binary file from the package.

        :param file:    The path of the file to be read, relative to the package root.
        :return:        The content of the file.
        """
        raise NotImplementedError('read_bytes')

    @abstractmethod
    def namelist(self, base: Path | str = None) -> Iterator[Path]:
        """Get an iterator over file names under the specified base directory."""
        raise NotImplementedError('namelist')

    @abstractmethod
    def exists(self, file: Path | str) -> bool:
        """Check if a file exists in the package."""
        raise NotImplementedError('exists')

    @abstractmethod
    def is_dir(self, file: Path | str) -> bool:
        """Check if path is a directory."""
        raise NotImplementedError('is_dir')

    def get_source(self, environment, template: str):
        """Allow jinja2 to use this class as a custom loader."""
        try:
            template_source = self.read_text(template)
        except Exception:
            raise TemplateNotFound(template)

        return template_source, self.path, lambda: True


# ------------------------------------------------------------------------------
class DirPackageReader(PackageReader):
    """Create a directory package reader."""

    def __init__(self, path: Path) -> None:
        """Create a directory package reader."""
        if not path.is_dir():
            raise ValueError(f'{path} is not a directory')
        super().__init__(path)

    def read_text(self, file: Path | str) -> str:
        """Read a text file from the package."""
        src_path = self.path / relative_path(self.path, file)
        return src_path.read_text()

    def read_bytes(self, file: Path | str) -> bytes:
        """Read a binary file from the package."""
        src_path = self.path / relative_path(self.path, file)
        return src_path.read_bytes()

    def namelist(self, base: Path | str = None) -> Iterator[Path]:
        """Get an iterator over file names under the specified base directory."""
        root = self.path / relative_path(self.path, base) if base else self.path
        for p in walkpath(root):
            yield p.relative_to(self.path)

    def exists(self, file: Path | str) -> bool:
        """Check if a file exists in the package."""
        src_path = self.path / relative_path(self.path, file)
        return src_path.exists()

    def is_dir(self, file: Path | str) -> bool:
        """Check if path is a directory."""
        src_path = self.path / relative_path(self.path, file)
        return src_path.is_dir()


# ------------------------------------------------------------------------------
class ZipPackageReader(PackageReader):
    """Create a ZIP package reader."""

    def __init__(self, path: Path) -> None:
        """Create a ZIP package reader."""
        super().__init__(path)
        self._zip = ZipFile(self.path, 'r')

    def read_text(self, file: Path | str) -> str:
        """Read a text file from the package."""
        return self._zip.read(str(file)).decode('utf-8')

    def read_bytes(self, file: Path | str) -> bytes:
        """Read a binary file from the package."""

        return self._zip.read(str(file))

    def namelist(self, base: Path | str = None) -> Iterator[Path]:
        """Get an iterator over file names under the specified base directory."""
        base_path = zipfile.Path(self._zip, str(base or '').rstrip('/') + '/')
        for p in walkpath(base_path):
            yield Path(p.at)  # noqa

    def exists(self, file: Path | str) -> bool:
        """Check if a file exists in the package."""
        try:
            self._zip.getinfo(str(file))
            return True
        except KeyError:
            return False

    def is_dir(self, file: Path | str) -> bool:
        """Check if path is a directory."""
        try:
            info = self._zip.getinfo(str(file))
            return info.is_dir()
        except KeyError:
            return False

    def close(self):
        """Close the zip file."""
        self._zip.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the zip file."""
        self.close()


# ..............................................................................
# endregion PackageReader
# ..............................................................................
