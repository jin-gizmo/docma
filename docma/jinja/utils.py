"""Little Jinja2 related utilities."""

from __future__ import annotations

from contextlib import suppress
from typing import Any

import jinja2


__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
def get_context_var(ctx: jinja2.runtime.Context, name) -> Any:
    """Get a variable from the Jinja context in the same way as Jinja would."""
    for container in (ctx.vars, ctx.parent, ctx.environment.globals):
        with suppress(KeyError):
            return container[name]
    return None


# ------------------------------------------------------------------------------
class NoLoader(jinja2.BaseLoader):
    """Jinja2 loader that prevents loading."""

    def get_source(self, environment, template: str):
        """Block template loading."""
        raise Exception('Jinja2 loading prohibited')
