#!/usr/bin/env python3

"""
Docma internal API for compiling and rendering document templates.

.. warning::

   DO NOT use components from this module directly. Use only the components
   available via `import docma`.

   I really mean it. There is no guarantee of interface stability here.

"""  # noqa: D208

from __future__ import annotations

import os
import re
from base64 import b64encode
from collections.abc import Sequence
from contextlib import suppress
from datetime import datetime, timezone
from functools import partial
from io import BytesIO
from logging import getLogger
from pathlib import Path
from typing import Any, Callable, NoReturn
from urllib.parse import urlparse, urlunparse

import altair as alt
import jsonschema
import weasyprint
import yaml
from bs4 import BeautifulSoup, Tag  # noqa
from jinja2 import Template
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from weasyprint.text.fonts import FontConfiguration

from docma.compilers import compiler_for_file
from docma.config import (
    EMBED_IMG_MAX_SIZE,
    EMBED_IMG_MIN_SIZE,
    IMPORT_MAX_SIZE,
    LOGNAME,
    RECTANGLE_FUZZ_PDF_UNITS,
    WEASYPRINT_OPTIONS,
)
from docma.data_providers import DataSourceSpec, load_data
from docma.exceptions import DocmaPackageError, DocmaUrlFetchError
from docma.importers import import_content
from docma.jinja import DOCMA_JINJA_EXTRAS, DocmaJinjaEnvironment, DocmaRenderContext
from docma.lib.html import html_append
from docma.lib.jsonschema import FORMAT_CHECKER
from docma.lib.metadata import DocumentMetadata
from docma.lib.misc import (
    chunks,
    datetime_pdf_format,
    deep_update_dict,
    dot_dict_set,
    html_to_pdf,
    path_matches,
    str2bool,
)
from docma.lib.packager import PackageReader, PackageWriter
from docma.url_fetchers import get_url_fetcher_for_scheme
from docma.validators import validate_content
from docma.version import __version__

__author__ = 'Murray Andrews'

LOG = getLogger(LOGNAME)

PKG_CONFIG_FILE = 'config.yaml'
PKG_INFO_FILE = '.docma.yaml'
DOCMA_FORMAT_VERSION = int(__version__.split('.')[0])
PKG_IGNORE_FILES = ('.*',)  # Glob patterns for source files to exclude from template

SAFE_PATH_SYMBOLS = r'-_+=;:@%\w'  # Chars allowed in a path component
SAFE_PATH_COMPONENT_RE = re.compile(fr'^[{SAFE_PATH_SYMBOLS}][{SAFE_PATH_SYMBOLS}.]*$')
DOC_CREATOR = {
    'html': ' '.join(
        [
            f'docma {__version__}',
            f'Altair {alt.__version__}',
            f'Vega-lite {alt.SCHEMA_VERSION.replace("v", "")}',
        ]
    ),
    'pdf': ' '.join(
        [
            f'docma {__version__}',
            f'WeasyPrint {weasyprint.__version__}',
            f'Altair {alt.__version__}',
            f'Vega-lite {alt.SCHEMA_VERSION.replace("v", "")}',
        ]
    ),
}

# This is used when embedding an image as Base64 data in HTML.
IMG_SRC_TEMPLATE = Template(
    """data:{{ img_type }};base64,
{% for line in img %}{{ line | string }}
{% endfor %}
""",
    autoescape=True,
)


# ------------------------------------------------------------------------------
def write_template_version_info(tpkg: PackageWriter) -> None:
    """Write version information into a magic file in a compiled template package."""

    info = {
        'docma_format_version': DOCMA_FORMAT_VERSION,
        'docma_compiler_version': __version__,
        'created': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    tpkg.write_string(yaml.safe_dump(info, default_flow_style=False), PKG_INFO_FILE)


# ------------------------------------------------------------------------------
def read_template_version_info(tpkg: PackageReader) -> dict[str, Any]:
    """Read version information from a magic file in a compiled template package."""

    if not tpkg.exists(PKG_INFO_FILE):
        raise DocmaPackageError('Not a compiled docma template package')
    return yaml.safe_load(tpkg.read_text(PKG_INFO_FILE))


# ------------------------------------------------------------------------------
def check_template_version_info(tpkg: PackageReader) -> None:
    """Check version information in a compiled template package."""

    try:
        template_info = read_template_version_info(tpkg)
    except Exception as e:
        raise DocmaPackageError(f'{tpkg.path}: {e}')

    if (v := template_info.get('docma_format_version')) != DOCMA_FORMAT_VERSION:
        LOG.warning(
            '%s has template version %s which may not be compatible with expected version %s',
            tpkg.path,
            v,
            DOCMA_FORMAT_VERSION,
        )


# ------------------------------------------------------------------------------
def set_weasy_options(
    options: dict[str, Any],
    pkg_reader: PackageReader,
    url_fetcher: Callable = None,
    font_config: FontConfiguration = None,
) -> None:
    """
    Load and validate weasyprint options for a template package.

    This sets the Weasyprint `DEFAULT_OPTIONS`.

    :param options:     The `options` content from the template config.
    :param pkg_reader:  The document template package reader.
    :param url_fetcher: Custom URL fetcher for WeasyPrint.
    :param font_config: WeasyPrint font configuration for @font-face rules.
    """

    weasyprint.DEFAULT_OPTIONS.update(WEASYPRINT_OPTIONS)
    if not options:
        return

    weasyprint.DEFAULT_OPTIONS.update(options)
    with suppress(KeyError):
        weasyprint.DEFAULT_OPTIONS['stylesheets'] = [
            weasyprint.CSS(
                string=(pkg_reader.read_text(s)), url_fetcher=url_fetcher, font_config=font_config
            )
            for s in options['stylesheets']
        ]


# ------------------------------------------------------------------------------
class DocSpec:
    """
    Convert an element in the documents list into a canonical form.

    Each element in a document list can be either a string or a dict containing,
    among other things, the `src` key specifying the file.

    :param doc_item:   A string doc name or a dict containing a 'src' key and
                        possibly an 'if' key.
    """

    def __init__(self, doc_item: str | dict[str, Any]):
        """Create a DocSpec."""

        if isinstance(doc_item, str):
            self.src = doc_item
            self.if_condition = None
        else:
            self.src = doc_item['src']
            self.if_condition = doc_item.get('if')

        self._purl = urlparse(self.src)

    def __str__(self) -> str:
        """Generate string form."""
        return self.src

    def __getattr__(self, attr):
        """Defer unknown attributes to urlparse attributes."""
        return getattr(self._purl, attr)


# ------------------------------------------------------------------------------
def copy_file_to_template(src: Path, dst: Path, tpkg: PackageWriter) -> Path:
    """
    Copy a file into the template, compiling as required.

    :param src:     Source path.
    :param dst:     Path within the package for the (pre-compiled) comtent.
                    Compiled versions always end in .html.
    :param tpkg:    The document template package.

    :return:        The path in the package of the final content (after any
                    compilation).
    """

    raw_content = src.read_bytes()
    validate_content(src, raw_content)
    LOG.info(f'Copying {src}')
    tpkg.write_bytes(raw_content, dst)

    # Compile files to HTML as needed.
    try:
        compiler = compiler_for_file(src)
    except KeyError:
        # No compilation required
        return dst

    dst_compiled = dst.with_suffix('.html')
    LOG.info(f'Compiling {src} to {dst_compiled}')
    try:
        tpkg.write_string(compiler(raw_content), dst_compiled)
    except Exception as e:
        raise DocmaPackageError(f'Error compiling {src}: {e}')
    return dst_compiled


# ------------------------------------------------------------------------------
def import_file_to_template(src: str, dst: Path, tpkg: PackageWriter) -> Path:
    """
    Import a file into the template, compiling as required.

    :param src:     Source file URL. There needs to be an importer that knows
                    how to handle this.
    :param dst:     Path within the package for the (pre-compiled) comtent.
                    Compiled versions always end in .html.
    :param tpkg:    The document template package.

    :return:        The path in the package of the final imported content
                    (after any compilation).
    """

    imported_content = import_content(src, max_size=IMPORT_MAX_SIZE)
    validate_content(dst, imported_content)
    LOG.info('Importing %s as %s', src, dst)
    tpkg.write_bytes(imported_content, dst)

    # Compile files to HTML as needed.
    try:
        compiler = compiler_for_file(Path(src))
    except KeyError:
        # No compilation required
        return dst

    dst_compiled = dst.with_suffix('.html')
    LOG.info(f'Compiling {dst} to {dst_compiled}')
    try:
        tpkg.write_string(compiler(imported_content), dst_compiled)
    except Exception as e:
        raise DocmaPackageError(f'Error compiling {src}: {e}')
    return dst_compiled


# ------------------------------------------------------------------------------
def compile_template(src_dir: str, tpkg: str) -> None:
    """
    Compile a document source directory into a docma template package.

    :param src_dir: Source directory.
    :param tpkg:    Location of the compiled document template package.
    """

    src_dir = Path(src_dir)
    if not src_dir.is_dir():
        raise DocmaPackageError(f'{src_dir} is not a directory.')

    try:
        config = yaml.safe_load((src_dir / PKG_CONFIG_FILE).read_text())
    except FileNotFoundError:
        raise DocmaPackageError(f'No {PKG_CONFIG_FILE} configuration file found in {src_dir}')
    except Exception as e:
        raise DocmaPackageError(f'{src_dir / PKG_CONFIG_FILE}: {e}')

    # Only check documents local to the package for existance
    missing_docs = {
        Path(dd.path) for dd in (DocSpec(d) for d in config.get('documents', [])) if not dd.scheme
    }

    with PackageWriter.new(tpkg) as pkg:
        # Process local files from the source dir first.
        for root, _dirs, files in os.walk(src_dir):
            root_path = Path(root)
            if path_matches(root_path, PKG_IGNORE_FILES):
                LOG.debug('Ignoring directory %s', root_path)
                continue
            for f in (Path(f) for f in files):
                if path_matches(f, PKG_IGNORE_FILES):
                    LOG.debug('Ignoring file %s', f)
                    continue
                src = root_path / f
                missing_docs.discard(copy_file_to_template(src, src.relative_to(src_dir), pkg))

        # Process imports.
        for imp in config.get('imports', []):
            if isinstance(imp, str):
                src, dst = imp, imp.rsplit('/', 1)[-1]
            else:
                src, dst = imp['src'], imp['as']
            if not all((src, dst)):
                raise DocmaPackageError(f'Bad import: {imp}')
            missing_docs.discard(import_file_to_template(src, Path(dst), pkg))

        # Check that a source file is produced for each document
        if missing_docs:
            raise DocmaPackageError(
                f'No document source found for documents: {", ".join(str(s) for s in missing_docs)}'
            )

        # Add metadata about the compiled template.
        write_template_version_info(pkg)


# ------------------------------------------------------------------------------
def docma_url_fetcher(url: str, context: DocmaRenderContext, *args, **kwargs) -> dict[str, Any]:
    """
    Fetch URL content for Weasyprint.

    See also: The url_fetchers package.

    :param url:     The URL to fetch. If we don't have a custom fetcher
    :param context: Document rendering context.
    :param args:    Passed to the weasyprint default url fetcher.
    :param kwargs:  Passed to the weasyprint default url fetcher.

    :return:        A dict containing the URL content and mime type.
    """

    purl = urlparse(url)

    try:
        fetcher = get_url_fetcher_for_scheme(purl.scheme)
    except KeyError:
        # No special fetcher available -- use WeasyPrint default.
        return weasyprint.default_url_fetcher(url, *args, **kwargs)

    try:
        return fetcher(purl, context)
    except Exception as e:
        # We log here as well as raise because Weasyprint suppresses errors
        LOG.error(f'{url}: {e}')
        raise DocmaUrlFetchError(f'{url}: {e}') from e


# ------------------------------------------------------------------------------
def get_template_info(tpkg: PackageReader) -> dict[str, Any]:
    """Get information about a document template package."""

    try:
        config = yaml.safe_load(tpkg.read_text(PKG_CONFIG_FILE))
        info = read_template_version_info(tpkg)
        for k in ('description', 'owner', 'version', 'documents'):
            info[k] = config.get(k)
        return info
    except Exception as e:
        raise DocmaPackageError(f'{tpkg.path}: {e}')


# ------------------------------------------------------------------------------
def embed_img(
    img_tag: Tag,
    url_fetcher=Callable[[], dict],
    min_size: int = EMBED_IMG_MIN_SIZE,
    max_size: int = EMBED_IMG_MAX_SIZE,
) -> bool:
    """
    Generate HTML fragment to embed an image from a specified src.

    :param img_tag:     Image tag object.
    :param url_fetcher: A callable to fetch URL content.
    :param min_size:    Only embed images with at least this many bytes.
    :param max_size:    Only embed images with at most this many bytes.

    :return:        True if an image was embedded, False otherwise.
    """

    src = img_tag.get('src')
    if not src:
        raise DocmaPackageError(
            f'Missing or empty "src" attribute for IMG tag on line {img_tag.sourceline}'
            f' (alt="{img_tag.get("alt", "")}")'
        )

    if src.startswith('data:image/'):
        LOG.debug(
            'Found embedded image on line %s (alt="%s")', img_tag.sourceline, img_tag.get('alt')
        )
        return False

    src_purl = urlparse(src)
    content = None
    # For images accessible via http(s), we embed them if they:
    #   - are not too big and not too small
    #   - don't have an override preventing embedding
    #   - don't have query parameters in the URL.
    # Embed override can be:
    #   - None (unspecified) -- Just use the heuristics listed above
    #   - False -- Do not embed
    #   - True -- Force embedding
    if src_purl.scheme in ('http', 'https'):
        try:
            embed_override = str2bool(img_tag['data-docma-embed'])
        except KeyError:
            embed_override = None
        except Exception as e:
            raise DocmaPackageError(
                f'Bad data-docma-embed value for IMG tag on line {img_tag.sourceline}: {e}'
            )
        if embed_override is False:
            LOG.debug('Image tag on line %s has embed disabled (%s)', img_tag.sourceline, src)
            return False

        if not embed_override and src_purl.query:
            # Don't embed where there is a query in URL by default
            LOG.debug(
                'Image tag on line %s won\'t be embedded due to query (%s)', img_tag.sourceline, src
            )
            return False

        # This is a candidate for embedding. Get image size
        content = url_fetcher(img_tag['src'])
        if not embed_override and not min_size <= len(content['string']) <= max_size:
            LOG.debug(
                'Image tag on line %s outside embeddable size range (%s)', img_tag.sourceline, src
            )
            return False
    LOG.debug('Image tag on line %s will be embedded (%s)', img_tag.sourceline, src)

    if not content:
        content = url_fetcher(img_tag['src'])

    img_tag['src'] = IMG_SRC_TEMPLATE.render(
        img_type=content['mime_type'],
        img=(s.decode('utf-8') for s in chunks(b64encode(content['string']))),
    )
    return True


# ------------------------------------------------------------------------------
def embed_images(
    html: str,
    url_fetcher: Callable[[], dict],
    min_size: int = EMBED_IMG_MIN_SIZE,
    max_size: int = EMBED_IMG_MAX_SIZE,
) -> str:
    """
    Embed images into HTML.

    :param html:        HTML.
    :param url_fetcher: A callable to fetch URL content.
    :param min_size:    Only embed images with at least this many bytes.
    :param max_size:    Only embed images with at most this many bytes.
    :return:            HTML with embedded images.
    """

    parsed_html = BeautifulSoup(html, 'html.parser')
    image_tags = parsed_html.find_all('img')
    if not image_tags:
        LOG.debug('No image tags found.')
        return html

    embedded_count = 0
    for img_tag in image_tags:
        embedded_count += bool(
            embed_img(img_tag, url_fetcher, min_size=min_size, max_size=max_size)
        )

    LOG.info('Embedded %d images out of %s image tags found', embedded_count, len(image_tags))

    return parsed_html.prettify()


# ------------------------------------------------------------------------------
def safe_render_path(path: str, context: DocmaRenderContext, *args: dict[str, Any]) -> str:
    """
    Safely render a file path.

    Safety here means that each path component is individually rendered and we
    are very restrictive about what characters the rendered component can
    contain.

    :param path:        A file path string (e.g. /a/b/c)
    :param context:     Document rendering context.
    :param args:        Additional rendering params.
    :return:            A rendered file path.

    :raise ValueError:  If the path contains any invalid characters.
    """

    rendered_path = []
    params = deep_update_dict({}, context.params, *args)
    for path_component in path.split('/'):
        s = context.env.from_string(path_component).render(**params)
        if s and not SAFE_PATH_COMPONENT_RE.match(s):
            raise ValueError(f'Bad path component: {path_component}')
        rendered_path.append(s)

    return '/'.join(rendered_path)


# ------------------------------------------------------------------------------
def get_document_content(doc_name: str, context: DocmaRenderContext) -> bytes:
    """
    Get the content of a component document.

    :param doc_name:        Document name. This may be a local path (relative to
                            the template root) or a URL handled by the content
                            importer interface.
    :param context:         Document rendering context.
    :return:                The document content.
    """

    purl = urlparse(doc_name)
    if not purl.scheme:
        # Doc is part of the template.
        if not context.tpkg.exists(doc_name):
            raise DocmaPackageError(f'Document {doc_name}: Not found')
        return context.tpkg.read_bytes(doc_name)

    # Jinja render the path ... safely
    LOG.debug('Rendering document name: %s', doc_name)
    doc_name = urlunparse(
        (
            purl.scheme,
            purl.netloc,
            safe_render_path(purl.path, context),
            purl.params,
            purl.query,
            purl.fragment,
        )
    )
    LOG.debug('Rendering result is: %s', doc_name)

    try:
        return import_content(doc_name, max_size=IMPORT_MAX_SIZE)
    except Exception as e:
        raise DocmaPackageError(f'Document {doc_name}: {e}') from e


# ------------------------------------------------------------------------------
def document_to_pdf(
    doc_name: str,
    context: DocmaRenderContext,
    font_config: FontConfiguration = None,
) -> PdfReader:
    """
    Render a single document to PDF.

    :param doc_name:        Document name. This may be a filename relative to the
                            template package or a URL.
    :param context:         Document rendering context.
    :param font_config:     WeasyPrint font configuration for @font-face rules.
    :return:                A PdfReader containing the document content.
    """

    doc_content = get_document_content(doc_name, context)

    if doc_name.lower().endswith(('.html', '.htm')):
        # Render HTML docs
        try:
            return html_to_pdf(
                context.render(doc_content.decode('utf-8')),
                url_fetcher=partial(docma_url_fetcher, context=context),
                font_config=font_config,
            )
        except Exception as e:
            raise Exception(f'Error rendering {doc_name}: {e}')

    if doc_name.lower().endswith('.pdf'):
        return PdfReader(BytesIO(doc_content))

    raise DocmaPackageError(f'Document {doc_name}: Unknown type')


# ------------------------------------------------------------------------------
def document_to_html(doc_name: str, context: DocmaRenderContext) -> BeautifulSoup:
    """
    Render a single document to HTML.

    :param doc_name:        Document name. This may be a filename relative to the
                            template package or a URL.
    :param context:         Document rendering context.
    :return:                A parsed HTML document.
    """

    if not doc_name.lower().endswith(('.html', '.htm')):
        raise DocmaPackageError(f'Document {doc_name}: Not a HTML file')

    doc_content = get_document_content(doc_name, context)
    html = context.render(doc_content.decode('utf-8'))
    return BeautifulSoup(
        embed_images(html, url_fetcher=partial(docma_url_fetcher, context=context)), 'html.parser'
    )


# ------------------------------------------------------------------------------
def rectangles_approx_equal(
    r1: RectangleObject, r2: RectangleObject, tolerance: float = RECTANGLE_FUZZ_PDF_UNITS
) -> bool:
    """
    Compare the size of two rectangles for size equality.

    :param r1:          Rectangle 1.
    :param r2:          Rectangle 2.
    :param tolerance:   Allowed size difference per axis in PDF units (1/72 inch).
    :return:
    """

    return all(abs(v1 - v2) < tolerance for v1, v2 in zip(tuple(r1), tuple(r2)))


# ------------------------------------------------------------------------------
def apply_overlay(
    pdf: PdfWriter,
    overlay_id: str,
    config: dict[str, Any],
    context: DocmaRenderContext,
    font_config: FontConfiguration = None,
    over=False,
) -> None:
    """
    Find the first overlay in a document sequence that matches the sample geometry.

    :param pdf:         Target PDF to which the overlay should be applied.
                        find a matching overlay.
    :param overlay_id:  Overlay ID within config file.
    :param config:      Template configuration.
    :param context:     Document rendering context.
    :param font_config: WeasyPrint font configuration for @font-face rules.
    :param over:        Whether to apply the overlay on top (stamp) or underneath
                        (watermark).
    :raise Exception:   If no overlay with matching geometry is found.
    """

    if not pdf.pages:
        raise Exception('Cannot apply overlay to empty PDF')

    try:
        overlay_docs = config['overlays'][overlay_id]
    except KeyError:
        raise DocmaPackageError(f'{overlay_id}: Unknown overlay')

    if isinstance(overlay_docs, str):
        overlay_docs = [overlay_docs]

    # Render all overlay docs and index them by page geometry
    overlay_pages = []
    context.params['docma']['template']['overlay_id'] = overlay_id
    for d in overlay_docs:
        LOG.debug('Rendering overlay %s', d)
        context.params['docma']['template']['overlay'] = d
        context.params['docma']['template']['overlay_path'] = Path(urlparse(d).path)
        overlay_pdf = document_to_pdf(doc_name=d, context=context, font_config=font_config)
        if not overlay_pdf.pages:
            LOG.warning('Overlay %s is empty', d)
            continue
        overlay_pages.append(overlay_pdf.pages[0])

    for page_num, page in enumerate(pdf.pages, 1):
        for overlay_page in overlay_pages:
            if rectangles_approx_equal(overlay_page.mediabox, page.mediabox):
                page.merge_page(overlay_page, over=over)
                break
        else:
            raise Exception(f'No overlay found for page {page_num} with geometry {page.mediabox}')
    # Cleanup changes made to render params
    for k in ('overlay_id', 'overlay', 'overlay_path'):
        del context.params['docma']['template'][k]


# ------------------------------------------------------------------------------
def set_metadata_pdf(pdf: PdfWriter, metadata: DocumentMetadata, context: DocmaRenderContext):
    """Set the metadata in a HTML doc."""

    pdf.add_metadata({k: context.render(v) for k, v in metadata.as_dict('pdf').items()})


# ------------------------------------------------------------------------------
def coalesce_docma_render_params(config, *d: dict[str, Any]) -> dict[str, Any]:
    """
    Coalesce the template config parameter defaults with docma params and dynamic params.

    :param config:  The docma template config.
    :param d:       Dynamic parameters.
    :return:        A unified rendering parameter dictionary.
    """

    # noinspection PyUnusedLocal
    def no_docma_data_here(*args, **kwargs) -> NoReturn:
        """Create a place holder for docma.data()."""
        raise DocmaPackageError('docma.data() cannot be used here')

    return deep_update_dict(
        {},
        config.get('parameters', {}).get('defaults', {}),
        *d,
        {'docma': DOCMA_JINJA_EXTRAS},
        {
            'docma': {
                'data': no_docma_data_here,
                'template': {
                    'id': config['id'],
                    'description': config['description'],
                    'owner': config['owner'],
                    'version': config['version'],
                },
                'version': __version__,
            }
        },
    )


# ------------------------------------------------------------------------------
def render_template_to_pdf(
    template_pkg_name: str,
    render_params: dict[str, Any],
    watermark: Sequence[str] = None,
    stamp: Sequence[str] = None,
    compression: int = 0,
) -> PdfWriter:
    """
    Generate PDF output from a document template package.

    :param template_pkg_name:   Name of the ZIP file / direectory containing the
                                compiled template package.
    :param render_params:       Rendering parameters.
    :param watermark:           A sequence of IDs of overlay documents to apply
                                under the PDF.
    :param stamp:               A sequence of IDs of overlay documents to apply
                                over the PDF.
    :param compression:         Compression level for PDF output 0..9.
    :return:                    PDF output file as a PyPDF PdfWriter instance.
    """

    # ----------------------------------------
    def docma_data(
        src_type: str, location: str, query: str = None, params: dict[str, Any] = None
    ) -> list[dict[str, Any]]:
        """Provide the Jinja renderer with access to the data providers subsystem."""
        if not render_params:
            raise DocmaPackageError('docma.data cannot be used here')
        data_src = DataSourceSpec(src_type, location, query)
        return load_data(data_src, context, params=params)

    # ----------------------------------------
    output_pdf = PdfWriter()
    font_config = FontConfiguration()

    with PackageReader.new(template_pkg_name) as tpkg:
        check_template_version_info(tpkg)

        # Load template config and prep our Jinja renderer
        config = yaml.safe_load(tpkg.read_text(PKG_CONFIG_FILE))
        render_params = coalesce_docma_render_params(config, render_params)
        dot_dict_set(render_params, 'docma.data', docma_data)
        dot_dict_set(render_params, 'docma.format', 'PDF')
        LOG.debug('Render parameters: %s', render_params)
        context = DocmaRenderContext(
            tpkg=tpkg,
            env=DocmaJinjaEnvironment(loader=tpkg, autoescape=True),
            params=render_params,
        )

        set_weasy_options(
            config.get('options'),
            tpkg,
            url_fetcher=partial(docma_url_fetcher, context=context),
            font_config=font_config,
        )

        # If the config included a schema for params, use that to validate them.
        if params_schema := config.get('parameters', {}).get('schema'):
            LOG.info('Validating parameters')
            jsonschema.validate(context.params, params_schema, format_checker=FORMAT_CHECKER)

        # Process the document files
        doc_no = 0
        for doc in (DocSpec(d) for d in config['documents']):
            # Check if this doc gets included
            if doc.if_condition and not str2bool(context.render(doc.if_condition)):
                LOG.info('Skipping %s', doc)
                continue

            doc_no += 1
            LOG.info(f'Processing {doc}')
            context.params['docma']['template']['document'] = doc.src
            context.params['docma']['template']['document_path'] = Path(doc.path)
            context.params['docma']['template']['page'] = len(output_pdf.pages) + 1
            context.params['docma']['template']['doc_no'] = doc_no
            output_pdf.append_pages_from_reader(
                document_to_pdf(doc.src, context, font_config=font_config)
            )

        if not doc_no:
            # No documents were selected!
            raise DocmaPackageError('No documents were selected')

        if not output_pdf.pages:
            raise DocmaPackageError('Generated PDF contained no pages')

        # Clean up document specific params before we move on to overlays.
        for k in ('document', 'page', 'doc_no'):
            del context.params['docma']['template'][k]

        # Process watermarks / stamps
        for overlay_id in watermark or []:
            LOG.info(f'Applying watermark {overlay_id}')
            apply_overlay(output_pdf, overlay_id, config, context, font_config=font_config)

        for overlay_id in stamp or []:
            LOG.info(f'Applying stamp {overlay_id}')
            apply_overlay(
                output_pdf, overlay_id, config, context, font_config=font_config, over=True
            )

    if compression:
        LOG.debug('Compressing PDF')
        for page in output_pdf.pages:
            page.compress_content_streams(compression)

    # Add metadata
    metadata = DocumentMetadata(**config.get('metadata', {}))
    # TODO: The Metadata class should handle this formatting weirdness
    metadata['creation_date'] = datetime_pdf_format()
    metadata['creator'] = (
        f'{Path(template_pkg_name).stem} {config["version"]} ({DOC_CREATOR["pdf"]})'
    )
    set_metadata_pdf(output_pdf, metadata, context)

    return output_pdf


# ------------------------------------------------------------------------------
def set_metadata_html(html: BeautifulSoup, metadata: DocumentMetadata, context: DocmaRenderContext):
    """Set the metadata in a HTML doc."""

    if not html.head:
        head = html.new_tag('head')
        html.html.insert(0, head)

    for k, v in metadata.as_dict('html').items():
        for t in html.find_all('meta', attrs={'name': k}):
            LOG.debug('Deleting existing tag %s', t)
            t.decompose()

        html.head.append(html.new_tag('meta', attrs={'name': k, 'content': context.render(v)}))
        LOG.debug('Adding meta tag %s=%s', k, v)


# ------------------------------------------------------------------------------
def render_template_to_html(
    template_pkg_name: str,
    render_params: dict[str, Any],
) -> BeautifulSoup:
    """
    Render a template to self contained HTML.

    :param template_pkg_name:   Name of the ZIP file / direectory containing the
                                compiled template package.
    :param render_params:       Rendering parameters.
    :return:                    A BeautifulSoup HTML structure.
    """

    # ----------------------------------------
    def docma_data(
        src_type: str, location: str, query: str = None, params: dict[str, Any] = None
    ) -> list[dict[str, Any]]:
        """Provide the Jinja renderer with access to the data providers subsystem."""
        if not render_params:
            raise DocmaPackageError('docma.data cannot be used here')
        data_src = DataSourceSpec(src_type, location, query)
        return load_data(data_src, context, params=params)

    # ----------------------------------------
    with PackageReader.new(template_pkg_name) as tpkg:
        check_template_version_info(tpkg)

        # Load template config and prep our Jinja renderer
        config = yaml.safe_load(tpkg.read_text(PKG_CONFIG_FILE))
        render_params = coalesce_docma_render_params(config, render_params)
        dot_dict_set(render_params, 'docma.data', docma_data)
        dot_dict_set(render_params, 'docma.format', 'HTML')
        LOG.debug('Render parameters: %s', render_params)
        context = DocmaRenderContext(
            tpkg=tpkg,
            env=DocmaJinjaEnvironment(loader=tpkg, autoescape=True),
            params=render_params,
        )

        # If the config included a schema for params, use that to validate them.
        if params_schema := config.get('parameters', {}).get('schema'):
            LOG.info('Validating parameters')
            jsonschema.validate(context.params, params_schema, format_checker=FORMAT_CHECKER)

        # Process the document files
        doc_no = 0
        html_soup = None
        for doc in (DocSpec(d) for d in config['documents']):
            # Check if this doc gets included
            if doc.if_condition and not str2bool(context.render(doc.if_condition)):
                LOG.info('Skipping %s', doc)
                continue

            doc_no += 1
            LOG.info(f'Processing {doc}')
            context.params['docma']['template']['document'] = doc.src
            context.params['docma']['template']['document_path'] = Path(doc.path)
            context.params['docma']['template']['doc_no'] = doc_no
            if not html_soup:
                html_soup = document_to_html(doc.src, context)
            else:
                html_append(html_soup, document_to_html(doc.src, context))

        if not doc_no:
            # No documents were selected!
            raise DocmaPackageError('No documents were selected')

        # Add metadata
        metadata = DocumentMetadata(**config.get('metadata', {}))
        metadata['creation_date'] = datetime.now(timezone.utc).isoformat()
        metadata['creator'] = (
            f'{Path(template_pkg_name).stem} {config["version"]} ({DOC_CREATOR["html"]})'
        )
        set_metadata_html(html_soup, metadata, context)

        return html_soup
