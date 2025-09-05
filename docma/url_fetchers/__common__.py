"""Common components for WeayPrint URL fetchers."""

from __future__ import annotations

from typing import Callable

_URL_FETCHERS = {}


# ------------------------------------------------------------------------------
def fetcher(*schemes: str) -> Callable:
    """Register URL fetcher for the specified URL schemes."""

    def decorate(func: Callable) -> Callable:
        """Register the handler function."""
        for scheme in schemes:
            _URL_FETCHERS[scheme] = func
        return func

    return decorate


# ------------------------------------------------------------------------------
def get_url_fetcher_for_scheme(scheme: str) -> Callable:
    """Get URL fetcher for the specified URL scheme."""

    return _URL_FETCHERS[scheme]
