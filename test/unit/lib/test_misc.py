"""Tests for doc.lib.misc."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from zoneinfo import ZoneInfo

import pytest

from docma.lib.misc import *


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'path,patterns,expected',
    [
        ('a/b/c', ['no*', 'nope/*', 'c'], True),
        ('a/b/cupcake', ['nope*', 'c*'], True),
        ('a/b/cupcake', ['nope*', 'fail*'], False),
    ],
)
def test_path_matches(path, patterns, expected) -> None:
    assert path_matches(Path(path), patterns) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's,expected',
    [
        ('abcd', 'abcd'),
        ('a b cd', 'a-b-cd'),
        ('9a b cd', '_9a-b-cd'),
        ('a/()=*&bcd', 'abcd'),
    ],
)
def test_css_id(s, expected):
    assert css_id(s) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'dicts, expected',
    [
        (
            [{'a': 'A'}],
            {'a': 'A'},
        ),
        (
            [{'a': 'A'}, {'b': 'B'}],
            {'a': 'A', 'b': 'B'},
        ),
        (
            [{'a': {'aa': 'A'}}, {'a': 'AA'}, {'b': 'B'}],
            {'a': 'AA', 'b': 'B'},
        ),
        (
            [{}, {'a': {'aa': 'A', 'bb': 'BB'}}, {'a': {'aa': {'aaa': 'AAA'}}}, {'b': 'B'}],
            {'a': {'aa': {'aaa': 'AAA'}, 'bb': 'BB'}, 'b': 'B'},
        ),
    ],
)
def test_deep_update_dict_ok(dicts: Sequence[dict], expected) -> None:
    assert deep_update_dict(*dicts) == expected


@pytest.mark.parametrize(
    'dicts',
    [({'a': 'A'}, 10)],
)
def test_deep_update_dict_fail(dicts: Sequence[dict]) -> None:
    with pytest.raises(TypeError, match='Expected a dictionary'):
        deep_update_dict(*dicts)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'd, key, expected',
    [
        ({'a': {'aa': 'AA'}, 'b': 'B'}, 'a.aa', 'AA'),
        ({'a': {'aa': 'AA'}, 'b': 'B'}, 'b', 'B'),
    ],
)
def test_dot_dict_get_ok(d: dict, key, expected):
    assert dot_dict_get(d, key) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'd, key',
    [
        ({'a': {'aa': 'AA'}, 'b': 'B'}, 'a.x'),
        ({'a': {'aa': 'AA'}, 'b': 'B'}, 'x'),
    ],
)
def test_dot_dict_get_fail(d: dict, key):
    with pytest.raises(KeyError):
        dot_dict_get(d, key)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'd, key, value',
    [
        ({'a': {'aa': 'AA'}, 'b': 'B'}, 'a.aa', 'XX'),
        ({'a': {'aa': 'AA'}, 'b': 'B'}, 'a.cc', 'XX'),
        ({'a': {'aa': 'AA'}, 'b': 'B'}, 'b', 'XX'),
        ({'a': {'aa': 'AA'}, 'b': 'B'}, 'c', 'XX'),
    ],
)
def test_dot_dict_set_ok(d: dict, key, value):
    assert dot_dict_get(dot_dict_set(d, key, value), key) == value


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'd, key, value, error',
    [
        ({'a': {'aa': 'AA'}, 'b': 'B'}, 'c.xx', 'XX', KeyError),
        ({'a': {'aa': 'AA'}, 'b': 'B'}, 'a.aa.xx', 'XX', TypeError),
    ],
)
def test_dot_dict_set_fail(d: dict, key, value, error):
    with pytest.raises(error):
        dot_dict_set(d, key, value)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'dt, expected',
    [
        (
            datetime(1998, 12, 23, 19, 52, 0, tzinfo=ZoneInfo('America/Los_Angeles')),
            "D:19981223195200-08'00'",
        )
    ],
)
def test_datetime_pdf_format_ok(dt: datetime, expected: str):
    assert datetime_pdf_format(dt) == expected


def test_datetime_pdf_format_now():
    assert datetime_pdf_format().startswith(datetime.now(timezone.utc).strftime('D:%Y%m%d%H%M%S'))


def test_datetime_pdf_format_fail() -> None:
    with pytest.raises(ValueError, match='No timezone info'):
        datetime_pdf_format(datetime.now())


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    's,expected',
    [
        (True, True),
        (False, False),
        ('yes', True),
        ('y', True),
        ('t', True),
        ('trUE', True),
        ('1', True),
        ('no', False),
        ('N', False),
        ('f', False),
        ('FALSE', False),
        ('0', False),
    ],
)
def test_str2bool_ok(s, expected):
    assert str2bool(s) == expected


@pytest.mark.parametrize(
    's,exc',
    [
        (21, TypeError),
        ([], TypeError),
        ('no-idea', ValueError),
    ],
)
def test_str2bool_bad(s, exc):
    with pytest.raises(exc):
        str2bool(s)


# ------------------------------------------------------------------------------
def test_html_to_pdf():
    """Do a half-hearted test of HTML to PDF (just make sure it runs.)"""

    pdf = html_to_pdf('<HTML><BODY><H1>Hello World</H1></BODY></HTML>')
    assert len(pdf.pages) == 1
    assert pdf.pages[0].extract_text(0) == 'Hello World'


# ------------------------------------------------------------------------------
def test_env_config(env):
    e = env_config('docma', 'PGLOCAL')
    assert e['user'] == env['PGLOCAL_USER']


# ------------------------------------------------------------------------------
def test_store_name_value_pair(capsys):

    argp = ArgumentParser(add_help=False)
    argp.add_argument('--single', action=StoreNameValuePair)
    argp.add_argument('--multi', action=StoreNameValuePair, nargs='+')

    # Good args
    args = argp.parse_args(['--single', 's1=v1', '--single', 's2=v2', '--multi', 'm1=v3', 'm2=v4'])
    assert args.single == {'s1': 'v1', 's2': 'v2'}
    assert args.multi == {'m1': 'v3', 'm2': 'v4'}

    # Bad args
    with pytest.raises(SystemExit):
        argp.parse_args(['--single', 'bad'])
    assert 'error: argument --single' in capsys.readouterr().err


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'name, size',
    [
        ('Arial', 12),  # WARNING: This may be O/S specific.
        ('Arial', 23),
        ('No-such-font', 8),
        ('No-such-font', 23),
    ],
)
def test_load_font(name: str, size: int) -> None:

    f = load_font(name, size)
    assert f.size == size
    assert f.getname()[1] == 'Regular'
