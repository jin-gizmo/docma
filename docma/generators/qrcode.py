"""Content generator for QR codes."""

from __future__ import annotations

from io import BytesIO
from typing import Any

import qrcode
from pydantic import BaseModel, ConfigDict, PositiveInt, conint

from docma.jinja import DocmaRenderContext
from .__common__ import content_generator


# ------------------------------------------------------------------------------
class QrCodeOptions(BaseModel):
    """Validator for QR code content generator options."""

    model_config = ConfigDict(extra='forbid')

    text: str
    box: PositiveInt = 10
    border: conint(ge=4) = 4
    fg: str = 'black'
    bg: str = 'white'


# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
@content_generator('qrcode', QrCodeOptions)
def qrc(options: QrCodeOptions, context: DocmaRenderContext) -> dict[str, Any]:
    """
    Produce a QR Code.

    Options must contain:
        - text

    Options may contain:
        - box:  Number of pixels for each box in the QR code.
        - border: Number of boxes thick for the border (minimum 4).
        - fg: Foreground colour of the QR code (e.g. `blue` or `#0000ff`).
        - bg: Background colour of the QR code.
    """

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=options.box,
        border=options.border,
    )
    qr.add_data(options.text)
    qr.make(fit=True)
    img = qr.make_image(fill_color=options.fg, back_color=options.bg)
    buf = BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    return {'string': buf.read(), 'mime_type': 'image/png'}
