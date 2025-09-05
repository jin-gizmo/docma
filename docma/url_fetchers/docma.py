"""
Fetch docma:... URLs for WeasyPrint via dynamic content generation.

This is the glue between WeasyPrint and the docma content generator subsystem.

Weasyprint sees a URL of the form `docma:...` and it calls this URL fetcher to
retrieve the content. This fetcher invokes the docma generator specified in the
URL path.

"""

from __future__ import annotations

from typing import Any
from urllib.parse import ParseResult, parse_qs

from docma.exceptions import DocmaUrlFetchError
from docma.generators import content_generator_for_type
from docma.lib.core import DocmaRenderContext
from .__common__ import fetcher


# ------------------------------------------------------------------------------
@fetcher('docma')
def docma_url_fetcher(purl: ParseResult, context: DocmaRenderContext) -> dict[str, Any]:
    """
    Fetch docma:... URLs for WeasyPrint.

    :param purl:    A parsed URL. See urllib.parse.urlparse().
    :param context: Document rendering context.

    :return:        A dict containing the URL content and mime type.
    """

    if purl.netloc:
        raise DocmaUrlFetchError(
            f'{purl.geturl()}: Content generators must be referenced as docma:name?options,'
            f' not docma://name?options'
        )

    gen = content_generator_for_type(purl.path)

    # We need to parse the query params in a way that allows a parameter to have
    # multiple values. Unfortunately, this then forces every value to be
    # reprsented as a list. We don't want that so we collapse single-item lists
    # back to just the value.
    options = dict(parse_qs(purl.query))
    for k, v in options.items():
        if len(v) == 1:
            options[k] = v[0]

    return gen(options=options, context=context)
