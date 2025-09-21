"""Jinja utilities, filters etc."""

from __future__ import annotations

import calendar
import datetime
from collections.abc import Iterable
from dataclasses import dataclass, field
from functools import singledispatchmethod
from typing import Any

import jinja2

from docma.lib.misc import deep_update_dict
from docma.lib.packager import PackageReader
from docma.lib.plugin import (
    MappingResolver,
    PLUGIN_JINJA_FILTER,
    PLUGIN_JINJA_TEST,
    PackageResolver,
    PluginRouter,
)
from .extensions import custom_extensions
from .resolvers import CurrencyFilterResolver, DateFormatResolver

__author__ = 'Murray Andrews'

filters = {}

# Some extra useful functions
DOCMA_JINJA_EXTRAS = {
    'calendar': calendar,
    'datetime': datetime,
}


# ------------------------------------------------------------------------------
def jfunc(name: str):
    """Register Jinja extra functions."""

    def decorate(func):
        """Register the function."""
        DOCMA_JINJA_EXTRAS[name] = func
        return func

    return decorate


# ------------------------------------------------------------------------------
@jfunc('abort')
def _abort(message: str):
    """
    Throw an exception to force abort the Jinja renderer.

    .. deprecated:: 1.10.0
        Use the abort extension instead. (e.g. `{% abort 'message' %}`)
    """

    raise Exception(message)


# ------------------------------------------------------------------------------
class DocmaJinjaEnvironment(jinja2.Environment):
    """Jinja2 environment with some docma add-ons."""

    def __init__(self, *args, **kwargs):
        """Prep a Jinja2 environment for use in docma."""

        super().__init__(
            *args,
            extensions=['jinja2.ext.debug', 'jinja2.ext.loopcontrols', *custom_extensions],
            **kwargs,
        )
        self.filters = PluginRouter(
            [
                MappingResolver(self.filters),
                CurrencyFilterResolver(),
                PackageResolver('docma.plugins.jinja_filters', PLUGIN_JINJA_FILTER),
            ]
        )
        self.tests = PluginRouter(
            [
                MappingResolver(self.tests),
                PackageResolver('docma.plugins.jinja_tests', PLUGIN_JINJA_FILTER),
                # Format checkers work as both JSONschema formats and Jinja teats.
                DateFormatResolver(),
                PackageResolver('docma.plugins.format_checkers', PLUGIN_JINJA_TEST),
            ]
        )


# ------------------------------------------------------------------------------
@dataclass
class DocmaRenderContext:
    """Simple grouping construct for essential bits involved in rendering."""

    tpkg: PackageReader
    params: dict[str, Any] = field(default_factory=dict)
    env: DocmaJinjaEnvironment = None

    # --------------------------------------------------------------------------
    def __post_init__(self):
        """Create a default JinjaEnvironment if required."""
        if self.env is None:
            self.env = DocmaJinjaEnvironment(loader=self.tpkg, autoescape=True)

    # --------------------------------------------------------------------------
    @singledispatchmethod
    def render(self, v, *args, **kwargs):
        """Raise exception on unhandled types."""
        raise TypeError(f'Cannot render type {type(v)}')

    @render.register
    def _(self, s: str, *args: dict[str, Any], **kwargs) -> str:
        """
        Render a string using the context.

        :param s:       The string to render
        :param args:    Additional dictionaries of parameters for rendering.
        :param kwargs:  Additional keyword parameters for rendering.
        """

        params = (
            deep_update_dict({}, self.params, *args, kwargs) if any((args, kwargs)) else self.params
        )
        return self.env.from_string(s).render(**params)

    @render.register
    def _(self, v: Iterable, *args: dict[str, Any], **kwargs) -> list[str]:
        """
        Render each element of an iterable to produce a list of strings.

        :param v:       The iterable to render.
        :param args:    Additional dictionaries of parameters for rendering.
        :param kwargs:  Additional keyword parameters for rendering.
        """

        params = (
            deep_update_dict({}, self.params, *args, kwargs) if any((args, kwargs)) else self.params
        )
        return [self.env.from_string(s).render(**params) for s in v]
