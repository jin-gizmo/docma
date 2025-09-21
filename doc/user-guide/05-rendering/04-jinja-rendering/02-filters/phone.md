#### Jinja Filter: phone

Format phone numbers. If a number cannot be formatted, the unmodified input is
returned.

This is a [locale-aware](#locale-in-docma-templates) filter.

The underlying process is implemented using the excellent Python
[phonenumbers](https://github.com/daviddrysdale/python-phonenumbers) package,
which is itself a port of
[Google's libphonenumber library](https://github.com/google/libphonenumber).

Phone number formatting varies substantially internationally. Hence, the filter
needs to determine the relevant region for each phone number. It can do that in
one of 3 ways (highest precedence to lowest)

1.  An international code in the source phone number.

2.  An explicit region code argument to the phone filter (expressed as a
    two-character ISO country code).

3.  By assuming the phone number is associated with the effective locale setting
    For example, a locale setting of `en_AU` would imply the number is part of the
    Australian phone numbering plan.

The filter signature is:

```python
phone(number: str, region: str = None, *, format: str = None)
```
| Parameter | Description |
|-|-|
| number | The phone number input to the filter. Phone numbers are always strings, never integers. Ever. |
| region | The region to which the phone number belongs as a 2 character ISO country code. Ignored if the phone number includes an international code. If not specified, the country code from the current effective locale is used. |
| format | See below. |

Phone numbers can be formatted in different ways. The following values of the `format` parameter are supported:

| Format        | Description                                                                                                                                            |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| E164          | E.164 is the standard International Telecommunication Union (ITU) format for worldwide telephone numbers. e.g. `+61491570006`                          |
| INTERNATIONAL | The full international phone number, formatted as per national conventions. e.g. `+61 491 570 006`                                                     |
| NATIONAL      | The national number component of the phone number without the international code component, formatted as per national conventions. e.g. `0491 570 006` |
| RFC3966       | The URI format for phone numbers. This will typically generate one-touch call links in on-line content. e.g. `tel:+61-491-570-006`                     |

If not specified, `NATIONAL` is used if the region for the phone number matches
that for the current locale and `INTERNATIONAL` otherwise.

Examples (assuming locale is set to `en_AU`):

```jinja
{{ '0491 570 006' | phone }} --> 0491 570 006 (Locale will provide "AU" as region)
{{ '+61 491 570 006' | phone }} --> 0491 570 006 (Region comes from the number)
{{ '4155550132' | phone('US') }} --> +1 415-555-0132
{{ '4155550132'| phone('US', format='NATIONAL') }} --> (415) 555-0132
{{ '4155550132'| phone('US', format='RFC3966') }} --> tel:+1-415-555-0132
{{ 'bad-to-the-phone' }} --> bad-to-the-phone (If all else fails, return the input)
```

