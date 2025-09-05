"""Miscellaneous utilities."""

from __future__ import annotations

import argparse
import os
import re
from collections.abc import Iterable, Iterator
from datetime import datetime, timezone
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Any, Callable

import colorama
import weasyprint
from PIL import ImageFont
from dotenv import dotenv_values
from pypdf import PdfReader
from weasyprint.text.fonts import FontConfiguration

colorama.init()

CHUNK_SIZE = 80


# ------------------------------------------------------------------------------
def path_matches(path: Path, patterns: Iterable[str]) -> bool:
    """Check if a path matches any in list of glob patterns."""
    return any(path.match(p) for p in patterns)


# ------------------------------------------------------------------------------
def deep_update_dict(*d: dict | None) -> dict:
    """
    Deep update dictionaries into the first one.

    :param d:   Dictionaries to merge.
    :return:    The first dict in the sequence containing the merged dictionary.

    """

    def update2(d1: dict, d2: dict):
        """Deep update second dict into the first one."""
        for k2, v2 in d2.items():
            if k2 in d1 and isinstance(d1[k2], dict) and isinstance(v2, dict):
                update2(d1[k2], v2)
            else:
                d1[k2] = v2

    if not all(isinstance(dd, dict) for dd in d if dd):
        raise TypeError('Expected a dictionary')
    for dd in d[1:]:
        if dd:
            update2(d[0], dd)

    return d[0]


# ------------------------------------------------------------------------------
def flatten_iterable(iterable: Iterable) -> list:
    """Flatten a nested iterable into a single level list."""
    result = []
    for item in iterable:
        if isinstance(item, list):
            result.extend(flatten_iterable(item))
        else:
            result.append(item)
    return result


# ------------------------------------------------------------------------------
def dot_dict_get(d: dict[str, Any], key: str) -> Any:
    """
    Access a dict element based on a hierarchical dot separated key.

    All the components of the key must be present in the dict or its a KeyError.

    :param d:   The dict to be accessed.
    :param key: The compound key in the form `a.b.c...`.
    """

    dd = d
    keys = key.split('.')

    for k in keys[:-1]:
        dd = dd[k]

    return dd[keys[-1]]


# ------------------------------------------------------------------------------
def dot_dict_set(d: dict[str, Any], key: str, value: Any) -> dict[str, Any]:
    """
    Set a dict element based on a hierarchical dot separated key.

    All the parent components of the key must be present in the dict or its a
    KeyError.

    :param d:       The dict to be modified
    :param key:     The compound key in the form `a.b.c...`.
    :param value:   The value to set.

    :return:        The dict.
    """

    dd = d
    keys = key.split('.')

    for k in keys[:-1]:
        dd = dd[k]

    dd[keys[-1]] = value
    return d


# ------------------------------------------------------------------------------
def datetime_pdf_format(dt: datetime = None) -> str:
    """
    Convert a timezone aware datetime object into PDF format.

    See: https://www.verypdf.com/pdfinfoeditor/pdf-date-format.htm

    :param dt:  Timezone aware datetime object. Defaults to current time UTC

    """

    if not dt:
        dt = datetime.now(timezone.utc)

    if dt.tzinfo is None:
        raise ValueError(f'No timezone info: {dt}')

    tz = dt.strftime('%z')
    tz_hh, tz_mm = tz[0:3], tz[3:5]

    return f"{dt.strftime('D:%Y%m%d%H%M%S')}{tz_hh}'{tz_mm}'"


# ------------------------------------------------------------------------------
def html_to_pdf(
    html_src: str, url_fetcher: Callable = None, font_config: FontConfiguration = None
) -> PdfReader:
    """
    Convert HTML source to PDF.

    Unfortunately, weasyprint's document construct is fairly opqaue and limited, with no
    real support for document composition or manipulation. So we basically use weasyprint
    to generate a PDF, write it out, then re-read it into a PyPDF PdfReader

    This is all done in memory. Should be ok in the context of this application but
    could add temp files if needed.

    :param html_src:    HTML source to convert (actual HTML -- not a file name).
    :param url_fetcher: Custom URL fetcher for WeasyPrint.
    :param font_config: WeasyPrint font configuration for @font-face rules.

    :return:            PyPDF PDF reader.
    """

    buf = BytesIO()
    parsed_html = weasyprint.HTML(string=html_src, url_fetcher=url_fetcher)
    parsed_html.write_pdf(buf, font_config=font_config)
    buf.seek(0)
    return PdfReader(buf)


# ------------------------------------------------------------------------------
def str2bool(s: str | bool) -> bool:
    """
    Convert a string to a boolean.

    This is a (case insensitive) semantic conversion.

        'true', 't', 'yes', 'y', non-zero int as str --> True
        'false', 'f', 'no', 'n', zero as str --> False

    :param s:       A boolean or a string representing a boolean. Whitespace is
                    stripped. Boolean values are passed back unchanged.

    :return:        A boolean derived from the input value.

    :raise ValueError:  If the value cannot be converted.

    """

    if isinstance(s, bool):
        return s

    if not isinstance(s, str):
        raise TypeError(f'Expected str, got {type(s)}')

    t = s.lower().strip()

    if t in ('true', 't', 'yes', 'y'):
        return True

    if t in ('false', 'f', 'no', 'n', ''):
        return False

    try:
        t = int(t)
    except ValueError:
        pass
    else:
        return bool(t)

    raise ValueError(f'Cannot convert string to bool: {s}')


# ------------------------------------------------------------------------------
def css_id(s: str) -> str:
    """Convert a string to a valid CSS identifier (e.g. for clases or IDs)."""

    # Delete invalid characters
    s = re.sub('[^A-Za-z0-9_:. -]', '', s)

    # Must start with alpha or underscore. Strictly speaking digits are allowed
    # but I don't like that.
    if not re.match('[A-Za-z_]', s):
        s = '_' + s
    # Replaces spaces with hyphen
    return re.sub(r'\s+', '-', s)


# ------------------------------------------------------------------------------
@lru_cache
def env_config(prefix: str, group: str) -> dict[str, str]:
    """
    Read configuration from environment variables and dotenv.

    This will return a dictionary of all values `<prefix>_<group>_*` read from
    the environment plus all values `<group>_*` read from .env. Environment
    vars take precedence. The `<prefix>`/`<group>` components are removed from
    the names. All keys are converted to lowercase.

    :param prefix:  A prefix for values read from environment variables. An
                    underscore is added. This is not used for variables read
                    from .env.
    :param group:   A prefix the identifies a group of variables to be fetched.

    :return:        A dictionary of values read from environment variables.

    """

    config = {
        k.removeprefix(f'{group}_').lower(): v
        for k, v in dotenv_values().items()
        if k.startswith(f'{group}_')
    }
    config.update(
        {
            k.removeprefix(f'{prefix}_{group}_').lower(): v
            for k, v in os.environ.items()
            if k.startswith(f'{prefix}_{group}_')
        }
    )
    return config


# ------------------------------------------------------------------------------
class StoreNameValuePair(argparse.Action):
    """
    Store argpare values from options of the form --option name=value.

    The destination (self.dest) will be created as a dict {name: value}. This
    allows multiple name-value pairs to be set for the same option.

    Usage is:

        argparser.add_argument('-x', metavar='key=value', action=StoreNameValuePair)

    or
        argparser.add_argument('-x', metavar='key=value ...', action=StoreNameValuePair,
                               nargs='+')

    """

    # --------------------------------------------------------------------------
    def __call__(self, parser, namespace, values, option_string=None):
        """Handle name=value option."""

        if not hasattr(namespace, self.dest) or not getattr(namespace, self.dest):
            setattr(namespace, self.dest, {})
        argdict = getattr(namespace, self.dest)

        if not isinstance(values, list):
            values = [values]
        for val in values:
            try:
                n, v = val.split('=', 1)
            except ValueError as e:
                raise argparse.ArgumentError(self, str(e))
            argdict[n] = v


# ------------------------------------------------------------------------------
@lru_cache
def load_font(name: str, size: int) -> ImageFont:
    """Load a truetype font or the default font."""

    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default(size)


# ------------------------------------------------------------------------------
def chunks(s: str | bytes, size: int = CHUNK_SIZE) -> Iterator[str | bytes]:
    """Yield successive chunks from a string."""

    for i in range(0, len(s), size):
        yield s[i : i + size]
