"""Jinja utilities, filters etc."""

from __future__ import annotations

import calendar
import datetime
import re
from decimal import Decimal, ROUND_HALF_UP
from pprint import pformat
from types import SimpleNamespace
from typing import Any

import jinja2
from jinja2 import nodes
from jinja2.exceptions import TemplateSyntaxError
from jinja2.ext import Context, Extension
from jinja2.parser import Parser

from .misc import css_id

filters = {}

# Some extra useful functions
docma_extras = {
    'calendar': calendar,
    'datetime': datetime,
}

docma_extensions: list[type[Extension] | str] = ['jinja2.ext.debug', 'jinja2.ext.loopcontrols']


# ------------------------------------------------------------------------------
class JinjaEnvironment(jinja2.Environment):
    """Jinja2 environment with some docma add-ons."""

    def __init__(self, *args, **kwargs):
        """Prep a Jinja2 environment for use in docma."""

        super().__init__(*args, extensions=docma_extensions, **kwargs)
        self.filters.update(filters)


# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
class NoLoader(jinja2.BaseLoader):
    """Jinja2 loader that prevents loading."""

    def get_source(self, environment, template: str):
        """Block template loading."""
        raise Exception('Jinja2 loading prohibited')


# ------------------------------------------------------------------------------
def jfilter(*names: str):
    """Register Jinja filters."""

    def decorate(func):
        """Register the filter function."""
        for name in names:
            filters[name] = func
        return func

    return decorate


# ------------------------------------------------------------------------------
def jfunc(name: str):
    """Register Jinja extra functions."""

    def decorate(func):
        """Register the function."""
        docma_extras[name] = func
        return func

    return decorate


# ------------------------------------------------------------------------------
def jext(cls: type[Extension]) -> type[Extension]:
    """Register Jinja extensions."""

    docma_extensions.append(cls)
    return cls


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
@jfilter('require')
def _require(value: Any, message: str):
    """Ensure a value is specified."""

    if not value:
        raise Exception(message)
    return value


# ------------------------------------------------------------------------------
@jfilter('dollars')
def _dollars(value: str | int | float, precision: int = 2, symbol: str = '$') -> str:
    """Format dollars using round up not bankers rounding."""

    rounded = Decimal(str(value)).quantize(Decimal(f'0.{precision * "0"}'), ROUND_HALF_UP)
    return f'{symbol or ""}{rounded:,}'


# ------------------------------------------------------------------------------
@jfilter('abn', 'ABN')
def _abn(value: str) -> str:
    """Format an ABN."""

    v = value.replace(' ', '')
    if len(v) != 11:
        raise ValueError(f'Bad ABN: {value}')
    return ' '.join([v[:2]] + [v[n : n + 3] for n in range(2, 11, 3)])


# ------------------------------------------------------------------------------
@jfilter('acn', 'ACN')
def _acn(value: str) -> str:
    """Format an ACN."""
    v = value.replace(' ', '')
    if len(v) != 9:
        raise ValueError(f'Bad ACN: {value}')
    return ' '.join(v[n : n + 3] for n in range(0, 9, 3))


# ------------------------------------------------------------------------------
@jfilter('css_id')
def _css_id(value: str) -> str:
    """Sanitise a string to be a valid CSS identifier."""

    return css_id(value)


# ------------------------------------------------------------------------------
@jfilter('sql_safe')
def _sql_safe(value: str) -> str:
    """
    Ensure a string is a safe SQL identifier.

    We accept "name" and "name.name" forms so it will also work on basic numbers
    where needed.

    This takes a very restrictive view on what is safe and will rule out some
    valid names but what is allowed is safe.
    """

    if not re.match(r'^\w+(\.\w+)?$', value):
        raise ValueError(f'Bad SQL name: {value}')

    return value


# ------------------------------------------------------------------------------
@jext
class StoreGlobalsExtension(Extension):
    """
    Jinja2 extension to store "global" variables in a "globals" namespace.

    The syntax to store items is:

    .. code:: jinja

        {% store x=10, y='hello' %}

    The can be retrieved using:

    .. code:: jinja

        {{ globals.x }}

    """

    tags = {'global'}

    # --------------------------------------------------------------------------
    def __init__(self, environment: jinja2.Environment):
        """Initialise the extension."""
        super().__init__(environment)
        self.namespace = SimpleNamespace()
        environment.globals['globals'] = self.namespace

    # --------------------------------------------------------------------------
    def parse(self, parser: Parser):
        """Parse global assignment tag."""
        # Get the tag token for error reporting
        token = next(parser.stream)
        lineno = token.lineno
        assignments = []

        try:
            # Parse first assignment
            if parser.stream.current.type == 'block_end':
                raise TemplateSyntaxError(f'Expected at least one assignment in {token}', lineno)

            # Keep parsing assignments until we hit the block end
            while True:
                # Parse variable name
                if parser.stream.current.type != 'name':
                    raise TemplateSyntaxError(
                        f'Expected variable name in {token}, got "{parser.stream.current.value}"',
                        parser.stream.current.lineno,
                    )

                target = parser.parse_assign_target()

                # Check for equals sign
                if parser.stream.current.type != 'assign':
                    raise TemplateSyntaxError(
                        f'Expected "=" in {token}, got "{parser.stream.current.value}"',
                        parser.stream.current.lineno,
                    )
                next(parser.stream)

                try:
                    expr = parser.parse_expression()
                except Exception as e:
                    raise TemplateSyntaxError(
                        f'Invalid expression after "{target.name}=" in {token}',
                        parser.stream.current.lineno,
                    ) from e

                assignments.append((target.name, expr))

                # Check if we're at the end or have a comma
                if parser.stream.current.type == 'block_end':
                    break
                if parser.stream.current.type != 'comma':
                    raise TemplateSyntaxError(
                        f'Expected "," or end of block in {token},'
                        f' got "{parser.stream.current.value}"',
                        parser.stream.current.lineno,
                    )
                next(parser.stream)  # Skip comma

                # Check for trailing comma
                if parser.stream.current.type == 'block_end':
                    raise TemplateSyntaxError(
                        f'Unexpected trailing comma in {token}', parser.stream.current.lineno
                    )
        except TemplateSyntaxError:
            raise
        except Exception as e:
            raise TemplateSyntaxError(f'Invalid syntax in {token} tag: {e}', lineno) from e

        # Create assignment nodes
        assignment_nodes = []
        for name, expr in assignments:
            assignment_nodes.append(nodes.Tuple([nodes.Const(name), expr], token))

        # Create a method call node with all assignments
        call = self.call_method(
            '_store_multiple',
            [
                nodes.List(assignment_nodes),
                nodes.Const(lineno),  # Pass line number to _store_multiple
            ],
        )
        return nodes.CallBlock(call, [], [], []).set_lineno(lineno)

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def _store_multiple(self, assignments, lineno, caller):
        """Store multiple values in the globals namespace."""

        try:
            for name, value in assignments:
                if not isinstance(name, str):
                    raise TypeError(f'Global name must be a string, got {type(name)}')
                if not name.isidentifier():
                    raise ValueError(f'Global name "{name}" is not a valid Python identifier')
                setattr(self.namespace, name, value)
        except Exception as e:
            raise TemplateSyntaxError(f'Error storing global values: {e}', lineno) from e
        return ''


# ------------------------------------------------------------------------------
@jext
class AbortExtension(Extension):
    """
    Abort tag to raise exceptions with custom messages.

    Usage:

    .. code:: jinja

        {% abort 'error message' %}

    """

    tags = {'abort'}

    # --------------------------------------------------------------------------
    def __init__(self, environment: jinja2.Environment):
        """Initialise the extension."""
        super().__init__(environment)

    # --------------------------------------------------------------------------
    def parse(self, parser: Parser) -> nodes.Node:
        """Parse the abort tag."""

        lineno = next(parser.stream).lineno

        # Check if there are any tokens before the end of block
        if parser.stream.current.type == 'block_end':
            raise TemplateSyntaxError('abort tag requires a message argument', lineno=lineno)

        # Parse the message argument
        try:
            args = [parser.parse_expression()]
        except Exception:
            raise TemplateSyntaxError('abort tag requires a valid string message', lineno=lineno)

        return nodes.CallBlock(
            self.call_method('_abort', args),
            [],  # argument list
            [],  # keyword arguments
            [],  # body
            lineno=lineno,
        )

    # --------------------------------------------------------------------------
    def _abort(self, message: str, caller: Any) -> str:
        """Raise an exception with the provided message."""
        raise RuntimeError(message)


# ------------------------------------------------------------------------------
@jext
class DumpParamsExtension(Extension):
    """
    Dump rendering parameters to assist with debugging.

    This is a variant based on the standard Jinja debug extension.

    Typical usage would be:

    .. code:: html

        <pre>{% dump_params %}</pre>

    """

    tags = {'dump_params'}

    def parse(self, parser: Parser) -> nodes.Output:
        """Parse the extension tag."""
        lineno = parser.stream.expect('name:dump_params').lineno
        context = nodes.ContextReference()
        result = self.call_method('_render', [context], lineno=lineno)
        return nodes.Output([result], lineno=lineno)

    @staticmethod
    def _render(context: Context) -> str:
        """Pretty format the parameters."""

        return pformat(context.get_all())
