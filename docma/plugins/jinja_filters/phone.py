"""
Jinja filter for phone numbers.

This handles the following formats:
    *   `{{ +61 491 570 006 | phone }}`
    *   `{% set locale='en_AU' %}{{ 0491 570 006 | phone }}`
    *   `{{ 0491 570 006 | phone('AU') }}`
    *   `{{ 0491 570 006 | phone('AU') }}`
    *   `{{ 0491 570 006 | phone('AU', format='INTERNATIONAL') }}`

The process needs to determine the relevant region for each phone number. It can
do that in one of 3 ways (highest precedence to lowest)

1.  An international code in the source phone number.
2.  An explicit region code argument to the phone filter (expressed as a
    two-character ISO country code).
3.  A `locale` rendering parameter.

The output format can be set explicitly using a `format` keyword argument to the
filter with one of the values `INTERNATIONAL`, `NATIONAL`, `E164` or `RFC3966`.
Case is not significant. If the format is not specified, `NATIONAL` is used if
the region associated with the number is the same as the region determined as
described above, and `INTERNATIONAL` is used otherwise. i.e. Local numbers
appear *local*, and international numbers appear *international*.

"""

__author__ = 'Murray Andrews'

import jinja2.runtime
from jinja2 import pass_context
from phonenumbers import (
    PhoneNumberFormat,
    SUPPORTED_REGIONS,
    format_number,
    parse,
    region_code_for_number,
)
from phonenumbers.phonenumberutil import UNKNOWN_REGION

from docma.jinja.utils import get_context_var
from docma.lib.plugin import jfilter

PHONE_NUMBER_FORMATS: dict[str, int] = {
    name: value for name, value in vars(PhoneNumberFormat).items() if name.isupper()
}


# ------------------------------------------------------------------------------
# noinspection PyShadowingBuiltins
@jfilter('phone')
@pass_context
def phone(
    ctx: jinja2.runtime.Context,
    number: str,
    region: str = None,
    *,
    format: str = None,  # noqa A002
):
    """
    Format a phone number.

    :param ctx:     Jinja rendering context. This is needed to get the locale.
    :param number:  Phone number.
    :param region:  Phone region. Typically a 2 character ISO country code. If
                    the phone number has an international country code, this is
                    ignored. If needed and not specified, the current locale is
                    used, if possible. A region must be determinable from one of
                    these mechanisms.
    :param format:  The output format to use. This must be a string naming
                    one of the values in phonenumbers.PhoneNumberFormat. Case
                    is ignored, If not specified, NATIONAL is used if the
                    country code of the phone number matches the region and
                    INTERNATIONAL otherwise.

    :return:        A formatted phone number, if possible. Otherwise, the original
                    number is returned.

    :raises ValueError: If region or format are invalid.
    """

    if not isinstance(number, str):
        number = str(number)

    # If the caller has specified a region it has to be valid, even if we
    # ultimately don't need it.
    if region and region not in SUPPORTED_REGIONS:
        raise ValueError(f'Unsupported phone number region: {region}')

    # Same for format
    phone_number_format = get_phone_number_format(format) if format else None

    # From this point on we will always produce something

    # noinspection PyBroadException
    try:
        return _phone(ctx, number, region=region, phone_number_format=phone_number_format)
    except Exception:
        return number


# ------------------------------------------------------------------------------
def _phone(
    ctx: jinja2.runtime.Context, number: str, region: str = None, *, phone_number_format: int = None
):
    """Format a phone number."""

    if not region or region == UNKNOWN_REGION:
        # Try to get a region from the locale
        locale = get_context_var(ctx, 'locale')
        if locale:
            region = locale.split('_')[-1]

    # We may or may not have a region at this point and that may or may not be
    # a problem. If the number has an international code we don't need region.
    parsed = parse(number, region)

    if phone_number_format is not None:
        return format_number(parsed, phone_number_format)

    return format_number(
        parsed,
        (
            PhoneNumberFormat.NATIONAL
            if region_code_for_number(parsed) == region
            else PhoneNumberFormat.INTERNATIONAL
        ),
    )


# ------------------------------------------------------------------------------
def get_phone_number_format(s: str) -> int:
    """Convert a string phone number format to a known PhoneNumberFormat."""

    try:
        return PHONE_NUMBER_FORMATS[s.upper()]
    except KeyError:
        raise ValueError(f'Unknown phone number format: {s}')
