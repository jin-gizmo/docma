"""Content generator for Vega-Lite charts."""

from __future__ import annotations

import json
from enum import Enum
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import Any

import altair as alt
import yaml
from pydantic import BaseModel, ConfigDict, Field, NonNegativeFloat, NonNegativeInt, field_validator

from docma.config import VEGA_PPI
from docma.data_providers import DataSourceSpec, load_data
from docma.exceptions import DocmaInternalError
from docma.jinja import DocmaRenderContext
from docma.lib.misc import dot_dict_set
from .__common__ import content_generator


# ------------------------------------------------------------------------------
class ChartFormatType(Enum):
    """Format type for rendered Vega charts."""

    svg = 'svg'
    png = 'png'


# ------------------------------------------------------------------------------
class VegaOptions(BaseModel):
    """Validator for altair-vega content generator options."""

    model_config = ConfigDict(extra='forbid')

    spec: str  # YAML spec file name
    data: list[str] = Field(default_factory=list)
    format: ChartFormatType = ChartFormatType.svg  # noqa: A003
    ppi: NonNegativeInt = VEGA_PPI
    scale: NonNegativeFloat = 1.0
    params: dict[str, Any] = Field(default_factory=dict)

    @field_validator('params', mode='before')  # noqa
    @classmethod
    def decode_json(cls, value: Any) -> dict[str, Any]:
        """Convert params from JSON to a dict."""
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception as e:
                raise ValueError(f'Bad JSON in vega options: {e}') from e
        if isinstance(value, dict):
            return value
        raise ValueError(f'Unexpected type {type(value)}')

    @field_validator('data', mode='before')  # noqa
    @classmethod
    def listify(cls, v) -> list:  # noqa
        """Ensure data is a list."""
        return v if isinstance(v, list) else [v]


# ------------------------------------------------------------------------------
@content_generator('vega', VegaOptions)
def vega_chart(options: VegaOptions, context: DocmaRenderContext) -> dict[str, Any]:
    """
    Produce a chart using Altair-Vega from a Vega-Lite spec in YAML format.

    Options must contain:
        - spec:     Path to a Vega-Lite spec file in YAML format.

    Options may contain:
        - format:   svg or png
        - data:     A list of data specifications.
        - ppi:      Pixels per inch for the image (png only).
        - scale:    Scale the image by the specified value (png only).
        - params:   Additional parameters made available to the query spec renderer.
    """

    spec = yaml.safe_load(context.render(context.tpkg.read_text(options.spec), options.params))

    # Load our data and attach it into the chart spec
    for data_src_spec in options.data:
        data_src = DataSourceSpec.from_string(data_src_spec)
        target = data_src.target or 'data.values'
        dot_dict_set(spec, target, load_data(data_src, context, params=options.params))
    chart = alt.Chart.from_dict(spec)

    if options.format == ChartFormatType.svg:
        # There is a bug in Altair writer for svg which forces it to be
        # written to a file with a .svg suffix.
        with NamedTemporaryFile('w+b', suffix='.svg') as tfp:
            chart.save(tfp.name)
            return {'string': tfp.read(), 'mime_type': 'image/svg+xml'}

    if options.format == ChartFormatType.png:
        buf = BytesIO()
        chart.save(buf, format='png', ppi=options.ppi, scale_factor=options.scale)
        buf.seek(0)
        return {'string': buf.read(), 'mime_type': 'image/png'}

    raise DocmaInternalError(f'Unsupported chart format: {options.format}')
