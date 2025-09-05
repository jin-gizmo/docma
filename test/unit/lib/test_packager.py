"""Tests for docma.lib.packager."""

from __future__ import annotations

import subprocess

import pytest
from jinja2 import Environment

from docma.lib.packager import *


# ------------------------------------------------------------------------------
def test_dir_package_reader(td):
    """Use our data directory as a dir package."""

    with PackageReader.new(td) as pkg:
        assert pkg.exists('README.md')
        assert not pkg.exists('No this file does not exist')
        assert pkg.read_text('README.md') == (td / 'README.md').read_text()
        assert pkg.read_bytes('README.md') == (td / 'README.md').read_bytes()
        assert not pkg.is_dir('README.md')
        assert not pkg.is_dir('none-such')
        assert Path('README.md') in pkg.namelist()

        # get_source allows Jinja to use the pkg as a custom loader
        content, path, _ = pkg.get_source(Environment(), 'README.md')
        assert content == (td / 'README.md').read_text()
        assert path == td
        with pytest.raises(TemplateNotFound, match='none-such'):
            pkg.get_source(Environment(), 'none-such')

    with pytest.raises(DocmaPackageError):
        PackageReader.new('none-such')


# ------------------------------------------------------------------------------
def test_dir_package_reader_no_a_directory(tmp_path):
    """Use our data directory as a dir package."""

    (tmp_path / 'file').write_text('not-a-directory')

    with pytest.raises(ValueError, match='not a directory'):
        DirPackageReader(tmp_path / 'file')


# ------------------------------------------------------------------------------
def test_zip_package_reader(td, tmp_path):

    # First create a zip file we can play with.
    pkg_path = tmp_path / 'pkg.zip'
    subprocess.run(['zip', '-r', str(pkg_path), '.'], cwd=str(td), check=True)

    with PackageReader.new(pkg_path) as pkg:
        assert pkg.exists('README.md')
        assert not pkg.exists('No this file does not exist')
        assert pkg.read_text('README.md') == (td / 'README.md').read_text()
        assert pkg.read_bytes('README.md') == (td / 'README.md').read_bytes()
        assert not pkg.is_dir('README.md')
        assert not pkg.is_dir('none-such')
        assert Path('README.md') in pkg.namelist()

    with PackageReader.new(str(pkg_path)) as pkg:
        assert pkg.exists('README.md')


# ------------------------------------------------------------------------------
def test_dir_package_writer(td, tmp_path):

    # Target path as a Path()
    p1 = tmp_path / 'p1'
    with PackageWriter.new(p1) as pkg:
        assert not pkg.exists('string.txt')
        pkg.write_string('hello world', 'string.txt')
        assert pkg.exists('string.txt')
        pkg.write_bytes(b'Hello world', 'byte.me')
        assert pkg.exists('byte.me')
        pkg.add_file(td / 'README.md', 'README.md')
        assert pkg.exists('README.md')
    assert p1.is_dir()

    # Target path as a string
    p2 = tmp_path / 'p2'
    with PackageWriter.new(str(p2)) as pkg:
        assert not pkg.exists('string.txt')
        pkg.write_string('hello world', 'string.txt')
        assert pkg.exists('string.txt')
    assert p2.is_dir()

    # ZIP package
    z1 = tmp_path / 'z1.zip'
    with PackageWriter.new(z1) as pkg:
        assert not pkg.exists('string.txt')
        pkg.write_string('hello world', 'string.txt')
        assert pkg.exists('string.txt')
        pkg.write_bytes(b'Hello world', 'byte.me')
        assert pkg.exists('byte.me')
        pkg.add_file(td / 'README.md', 'README.md')
        assert pkg.exists('README.md')
    assert z1.exists and not z1.is_dir()

    # Make sure zip file gets deleted if exception occurs
    z2 = tmp_path / 'z2.zip'
    with pytest.raises(Exception, match='Exception during ZipPackageWriter'):
        with PackageWriter.new(z2) as pkg:
            pkg.write_string('hello world', 'string.txt')
            raise Exception('Exception during ZipPackageWriter')
    assert not z2.exists()

    # Not allowed to specify an existing file for a PackageWriter.
    f1 = tmp_path / 'f1.txt'
    f1.write_text('I store data therefore I am')
    with pytest.raises(ValueError, match='not a directory'):
        PackageWriter.new(f1)
