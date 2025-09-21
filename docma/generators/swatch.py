"""Sample content generator producing a solid block of color."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from PIL import Image, ImageDraw
from pydantic import BaseModel, ConfigDict, PositiveInt

from docma.jinja import DocmaRenderContext
from docma.lib.misc import load_font
from .__common__ import content_generator


# ------------------------------------------------------------------------------
class SwatchOptions(BaseModel):
    """Validator for swatch content generator options."""

    model_config = ConfigDict(extra='forbid')

    width: PositiveInt
    height: PositiveInt
    color: str = '#eeeeee'
    text: str = None
    text_color: str = '#000000'
    font: str = 'Arial'
    font_size: PositiveInt = 18


# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
@content_generator('swatch', SwatchOptions)
def swatch(options: SwatchOptions, context: DocmaRenderContext) -> dict[str, Any]:
    """
    Produce a PNG colour swatch of a specified size and colour.

    Options must contain:
        - width
        - height

    Options may contain:
        - color
        - text
        - text_color
        - font
        - font_size
    """

    img = Image.new('RGB', size=(options.width, options.height), color=options.color)

    if options.text:
        draw = ImageDraw.Draw(img)
        font = load_font(options.font, options.font_size)
        text_box = draw.textbbox((0, 0), options.text, font=font)
        text_width, text_height = text_box[2] - text_box[0], text_box[3] - text_box[1]
        text_x, text_y = (options.width - text_width) / 2, (options.height - text_height) / 2
        draw.text((text_x, text_y), options.text, fill=options.text_color, font=font)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return {'string': buf.read(), 'mime_type': 'image/png'}
