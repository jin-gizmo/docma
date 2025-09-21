"""
Jinja specific PluginResolvers.

Resolvers are used by a PluginRouter to map a plugin name to a callable that
implements it, or None if not known.

Resolvers don't have to worry about cacheing. PluginRouter does that.
"""

from __future__ import annotations

from contextlib import suppress
from datetime import datetime

import jinja2.runtime
from babel.core import get_global  # noqa
from babel.numbers import decimal, format_currency  # noqa
from jinja2 import pass_context

from docma.lib.plugin import PluginResolver, PluginType
from .utils import get_context_var

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
class CurrencyFilterResolver(PluginResolver):
    """
     A resolver that uses Babel to format currencies.

     See https://babel.pocoo.org/en/latest/api/numbers.html#babel.numbers.format_currency.

    There are two separate concepts here:

     1.  The locale for which the currency is being formatted. This controls
         *how* the currency is formatted.
     2.  The target currency. This controls what value is being formatted.

     Often, a currency value is being formatted for the country to which
     that currency pertains (i.e. formatting Australian dollars for viewing in
     Australia). This is not always the case. For example, we may be
     formatting USD for viewing in Swiss French. This will be different to the
     way USD are formatted for America. As another example, in Australia, 10
     Australian dollars would be formatted as $10 but 10 US dollars would be
     formatted as USD10 to avoid ambiguity with AUD10.

     With that in mind, there are two styles of use for the filters provided here:

     1.  `{{ 1234.56 |  currency("AUD") }}`
     2.  `{{ 1234.56 | aud }}`

     The first form provides a thin interface to the underlying Babel
     `format_currency()` API. It preserves the Babel API with the following
     adaptations:

     1.  The value to be formatted is obviously provided using the standard Jinja
         convention for providing a value to a filter (i.e. the  `1234.56 |` bit.

     2.  The locale parameter for the Babel `format_currency()` API can be
         provided, if required, either by specifying it as an argument to the
         filter (e.g. `{{ 1234.56 |  currency("AUD", locale="en_AU") }}`) or by
         reference to the `locale` Jinja rendering parameter.,

     The second form is really just syntactic sugar that combines the `currency()`
     invocation and the target currency into the filter name.
    """

    def resolve(self, name: str) -> PluginType | None:
        """Try to resolve a plugin by name (eg. 'aud')."""

        if name == 'currency':
            return self.generic_currency_filter

        if name.upper() not in get_global('all_currencies'):
            return None

        # If the name is a known currency, make a filter for it.
        # For {{ 123.54 | aud }} type of usages.
        return self.make_named_currency_filter(name.upper())

    # --------------------------------------------------------------------------
    # Decorator order is critical here
    @staticmethod
    @pass_context
    def generic_currency_filter(
        ctx: jinja2.runtime.Context,
        value: str | int | float,
        *args,
        rounding: str = 'half-up',
        default: int | float | str | None = None,
        **kwargs,
    ) -> str:
        """
        Provide a thin pass-thru to babel format_currency.

        This will try to supply locale from the `locale` render variable if it
        is not supplied as an argument to the filter.

        :param ctx:         The Jinja context.
        :param value:       The value to be formatted.
        :param rounding:    How to round the value. This must be one of the
                            rounding modes decimal.ROUND_*, with the `ROUND_`
                            prefix removed. Case insensitive and hyphens become
                            underscores. Defaults to 'half-up' (Excel style
                            rounding), instead of `half-even` (Bankers rounding)
                            which is Python's normal default.
        :param default:     The default value to use for the filter if the value
                            is empty (i.e. None or an empty string). If value
                            is empty and default is a string, the default is used
                            as-is as the return value. If value is empty, and
                            default is not specified, a ValueError is raised.
                            Otherwise, the default is assumed to be numeric and
                            is used as the input to the filter.
        :param args:        Passed to Babel's `format_currency()`.
        :param kwargs:      Passed to Babel's `format_currency()`.
        """

        if value in (None, ''):
            if default is None:
                raise ValueError('Value is empty and no default specified')
            if isinstance(default, str):
                return default
            value = default

        rounding_mode = f'ROUND_{rounding.upper().replace("-", "_")}'
        try:
            r = getattr(decimal, rounding_mode)
        except AttributeError:
            raise ValueError(f'Unknown rounding mode: {rounding}')

        ctx_locale = get_context_var(ctx, 'locale')
        with decimal.localcontext(rounding=r):
            return format_currency(value, *args, **({'locale': ctx_locale} | kwargs))

    # --------------------------------------------------------------------------
    def make_named_currency_filter(self, currency_code) -> PluginType:
        """Create a currency filter named after a given currency code."""

        @pass_context
        def currency_specific_filter(
            ctx: jinja2.runtime.Context, value: str | int | float, *args, **kwargs
        ) -> str:
            """Format currency."""
            return self.generic_currency_filter(
                ctx, value, *args, **(kwargs | {'currency': currency_code})
            )

        return currency_specific_filter


# ------------------------------------------------------------------------------
class DateFormatResolver(PluginResolver):
    """
    A resolver for checking formats on date strings.

    This is a very simple (naive) implementation using strptime to handle
    various component ordering and separation. Needs a more sophisticated
    implementation at some point.
    """

    formats = {
        'dmy': '%d/%m/%Y',
        'ymd': '%Y/%m/%d',
        'mdy': '%m/%d/%Y',  # Nuts.
    }

    # --------------------------------------------------------------------------
    def resolve(self, name: str) -> PluginType | None:
        """Try to resolve a format checker plugin with name date.*."""

        try:
            prefix, fmt = name.split('.', 1)
        except ValueError:
            return None
        if prefix != 'date':
            return None
        try:
            fmt_strptime = self.formats[fmt]
        except KeyError:
            return None

        def date_format_specific_checker(value: str) -> bool:
            """Create a format specific checker."""
            if not isinstance(value, str):
                value = str(value)
            for sep in '', '/', '_', '.', '-':
                with suppress(ValueError):
                    datetime.strptime(value, fmt_strptime.replace('/', sep))
                    return True
            else:
                return False

        return date_format_specific_checker
