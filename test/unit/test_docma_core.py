"""Tests for docma.docma."""

from __future__ import annotations

import logging
from time import sleep
from urllib.error import URLError

import boto3
import pytest  # noqa
from moto import mock_aws  # noqa

from docma.compilers import content_compiler
from docma.docma_core import *
from docma.exceptions import DocmaPackageError, DocmaUrlFetchError
from docma.jinja import DocmaRenderContext
from docma.lib.packager import PackageReader, PackageWriter
from docma.version import __version__
from utils import squish_html


# ------------------------------------------------------------------------------
def test_template_version_info(tmp_path):

    # It's not a template yet
    with PackageReader.new(tmp_path) as tpkg:
        with pytest.raises(DocmaPackageError, match='Not a compiled docma template package'):
            read_template_version_info(tpkg)

        with pytest.raises(DocmaPackageError, match='Not a compiled docma template package'):
            check_template_version_info(tpkg)

    # Make it a template
    with PackageWriter.new(tmp_path) as tpkg:
        write_template_version_info(tpkg)

    # Check that it is.
    assert (tmp_path / PKG_INFO_FILE).exists()
    with PackageReader.new(tmp_path) as tpkg:
        pkg_info = read_template_version_info(tpkg)
        assert pkg_info['docma_format_version'] == DOCMA_FORMAT_VERSION
        assert pkg_info['docma_compiler_version'] == __version__

        check_template_version_info(tpkg)


# ------------------------------------------------------------------------------
# TODO: There is an annoying caplog race condition in here :-( Need to fix
def test_template_version_info_bad_version(tmp_path, monkeypatch, caplog, capsys):

    import docma.docma_core

    # Make this into a template
    with PackageWriter.new(tmp_path) as tpkg:
        write_template_version_info(tpkg)

    # Now force the version number not to match when we check it.
    monkeypatch.setattr(docma.docma_core, 'DOCMA_FORMAT_VERSION', DOCMA_FORMAT_VERSION + 1)
    logger = logging.getLogger(LOGNAME)
    with caplog.at_level(logging.INFO, logger=LOGNAME):
        with PackageReader.new(tmp_path) as tpkg:
            check_template_version_info(tpkg)
            logger.warning('-- log message push --')
        sleep(0.5)  # Kludge because pytest caplog is craplog (timing issues)
        assert 'may not be compatible with expected version' in caplog.text


# ------------------------------------------------------------------------------
def test_set_weasy_options(dirs):
    with PackageReader.new(dirs.templates / 'test1.src') as tpkg:
        assert not weasyprint.DEFAULT_OPTIONS['stylesheets']

        set_weasy_options({}, tpkg)
        assert not weasyprint.DEFAULT_OPTIONS['stylesheets']

        options = {'stylesheets': ['styles.css']}
        set_weasy_options(options, tpkg)
        assert len(weasyprint.DEFAULT_OPTIONS['stylesheets']) == len(options)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'doc_item, src, scheme, netloc',
    [
        ('plain-file.html', 'plain-file.html', '', ''),
        ({'src': 'dict-form.html', 'if': 'true'}, 'dict-form.html', '', ''),
        ('s3://bucket/prefix/file.html', 's3://bucket/prefix/file.html', 's3', 'bucket'),
        ('http://host/path/file.html', 'http://host/path/file.html', 'http', 'host'),
    ],
)
def test_docspec(doc_item, src, scheme, netloc):

    d = DocSpec(doc_item)
    assert str(d) == d.src == src
    assert d.scheme == scheme
    assert d.netloc == netloc


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'src_file, compare_file',
    [
        ('content/sample.html', 'content/sample.html'),
        ('content/compile-me.md', 'content/compile-me.html'),
    ],
)
def test_copy_file_to_template_ok(src_file, compare_file, dirs, tmp_path):

    src_dir = dirs.templates / 'test1.src'

    with PackageWriter.new(tmp_path) as tpkg:
        copy_file_to_template(src_dir / src_file, Path('x.html'), tpkg)

    with PackageReader.new(tmp_path) as tpkg:
        assert squish_html((src_dir / compare_file).read_text()) == squish_html(
            tpkg.read_text('x.html')
        )


# ------------------------------------------------------------------------------
def test_copy_file_to_template_compile_fail(dirs, tmp_path):
    """Test a failed compilation on copy."""

    @content_compiler('broken')
    def _(src_data: bytes) -> str:
        """Dummy content compiler."""
        raise RuntimeError(f'{src_data.decode("utf-8").strip()}: broken compiler')

    # Create a file that will force broken compiler to act
    broken_file_path = tmp_path / 'uh-oh.broken'
    broken_file_path.write_text('Uh oh')

    with PackageWriter.new(tmp_path / 'pkg') as tpkg:
        with pytest.raises(DocmaPackageError, match='broken compiler'):
            copy_file_to_template(broken_file_path, Path(broken_file_path.name), tpkg)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize('filename', ['README.md', 'images/qr-magenta-hello-world.png'])
def test_import_file_to_template_ok(filename, tmp_path, td, tc):

    src_url = f'http://{tc.web_server.netloc}/data/{filename}'

    with PackageWriter.new(tmp_path) as tpkg:
        compiled_path = import_file_to_template(src_url, Path(filename), tpkg)

        assert (
            import_content(f'http://{tc.web_server.netloc}/data/{filename}')
            == (td / filename).read_bytes()
        )
        assert tpkg.exists(compiled_path)


# ------------------------------------------------------------------------------
def test_import_file_to_template_fail(tmp_path, td, tc):
    """Test a failed compilation on import.."""

    @content_compiler('broken')
    def _(src_data: bytes) -> str:
        """Dummy content compiler."""
        raise RuntimeError(f'{src_data.decode("utf-8").strip()}: broken compiler')

    src_file = 'uh-oh.broken'
    src_url = f'http://{tc.web_server.netloc}/{src_file}'

    with PackageWriter.new(tmp_path) as tpkg:
        with pytest.raises(DocmaPackageError, match='broken compiler'):
            import_file_to_template(src_url, Path(src_file), tpkg)


# ------------------------------------------------------------------------------
def test_compile_template_ok(dirs, tmp_path):
    src_dir = dirs.templates / 'test1.src'
    compile_template(src_dir, str(tmp_path))


# ------------------------------------------------------------------------------
def test_compile_template_nodir_fail(tmp_path):
    with pytest.raises(DocmaPackageError, match='not a directory'):
        compile_template('no-such-dir', str(tmp_path))


# ------------------------------------------------------------------------------
def test_compile_template_no_config_fail(td, tmp_path):
    with pytest.raises(DocmaPackageError, match='No .* configuration file found'):
        compile_template(str(td), str(tmp_path))


# ------------------------------------------------------------------------------
def test_compile_template_malformed_config_fail(dirs, tmp_path):
    src_dir = dirs.templates / 'bad-config-1.src'
    with pytest.raises(DocmaPackageError, match='config.yaml'):
        compile_template(src_dir, str(tmp_path))


# ------------------------------------------------------------------------------
def test_compile_template_missing_document_fail(dirs, tmp_path):
    src_dir = dirs.templates / 'bad-config-2.src'
    with pytest.raises(DocmaPackageError, match='No document source found'):
        compile_template(src_dir, str(tmp_path))


# ------------------------------------------------------------------------------
def test_compile_template_bad_import_fail(dirs, tmp_path):
    src_dir = dirs.templates / 'bad-config-3.src'
    with pytest.raises(DocmaPackageError, match='Bad import'):
        compile_template(src_dir, str(tmp_path))


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "url, mime_type",
    [
        ('http://localhost:8080/data/custard100.csv', 'text/csv'),
        ('file:content/sample.html', 'text/html'),
    ],
)
def test_url_fetcher_ok(url, mime_type, dirs):
    with PackageReader.new(dirs.templates / 'test1.src') as tpkg:
        result = docma_url_fetcher(url, DocmaRenderContext(tpkg))
        assert result['mime_type'] == mime_type


# ------------------------------------------------------------------------------
def test_url_fetcher_fail(dirs, tmp_path):
    bad_url = 'bad-scheme://oh/dear/how/sad'
    with PackageReader.new(dirs.templates / 'test1.src') as tpkg:
        # docma will pass the bad URL to Weasyprint which will eventually pass it to urllib
        with pytest.raises(URLError, match='error unknown url type: bad-scheme'):
            docma_url_fetcher(bad_url, DocmaRenderContext(tpkg))


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "url, error, msg",
    [
        ('http://localhost:8080/no-such-object.xyz', Exception, 'File not found'),
        ('file:no-such-object.xyz', DocmaUrlFetchError, 'No such file'),
    ],
)
def test_url_fetcher_no_such_object_fail(url, error, msg, dirs):
    with PackageReader.new(dirs.templates / 'test1.src') as tpkg:
        with pytest.raises(error, match=msg):
            docma_url_fetcher(url, DocmaRenderContext(tpkg))


# ------------------------------------------------------------------------------
def test_get_template_info_ok(dirs, tmp_path):

    compile_template(dirs.templates / 'test1.src', str(tmp_path))
    with PackageReader.new(tmp_path) as tpkg:
        pkg_info = get_template_info(tpkg)
        assert pkg_info['docma_format_version'] == DOCMA_FORMAT_VERSION
        assert pkg_info['docma_compiler_version'] == __version__


# ------------------------------------------------------------------------------
def test_get_template_info_fail(td):

    with PackageReader.new(td) as tpkg:
        with pytest.raises(DocmaPackageError, match='No such file .*/config.yaml'):
            get_template_info(tpkg)


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "src_url, data_docma_embed, min_size, max_size, expected",
    [
        # Embed
        ('http://localhost:8080/data/images/swatch-cyan-100x50.png', None, 1, 1000, True),
        # Too big
        ('http://localhost:8080/data/images/swatch-cyan-100x50.png', None, 1, 2, False),
        # Too small
        ('http://localhost:8080/data/images/swatch-cyan-100x50.png', None, 1000, 2000, False),
        # Has query so no embed
        ('http://localhost:8080/data/images/swatch-cyan-100x50.png?x=20', None, 1, 1000, False),
        # Force embed even though too small
        ('http://localhost:8080/data/images/swatch-cyan-100x50.png', True, 1000, 2000, True),
        # Force embed even though has query
        ('http://localhost:8080/data/images/swatch-cyan-100x50.png?x=20', True, 1, 1000, True),
        # Inhibit embedding even though eligible
        ('http://localhost:8080/data/images/swatch-cyan-100x50.png', False, 1, 1000, False),
        # Already embedded
        ('data:image/png;base64 ...', None, 1, 1000, False),
        # Non http(s) are always embedded
        ('docma:swatch?height=50&width=50', None, 1, 1000, True),
        ('docma:swatch?height=50&width=50', None, 1, 2, True),
        ('docma:swatch?height=50&width=50', None, 1000, 2000, True),
        ('docma:swatch?height=50&width=50', False, 1, 1000, True),
    ],
)
def test_embed_img_ok(src_url, data_docma_embed, expected, min_size, max_size, td):
    context = DocmaRenderContext(PackageReader.new(td))
    url_fetcher = partial(docma_url_fetcher, context=context)
    tag = Tag(name='img', attrs={'src': src_url})
    if data_docma_embed is not None:
        tag['data-docma-embed'] = str(data_docma_embed)
    result = embed_img(tag, url_fetcher, min_size=min_size, max_size=max_size)
    assert result == expected
    if result:
        assert tag['src'].startswith('data:image/png;base64')


# ------------------------------------------------------------------------------
def test_embed_img_bad_data_docma_embed_fail(td):
    context = DocmaRenderContext(PackageReader.new(td))
    url_fetcher = partial(docma_url_fetcher, context=context)
    tag = Tag(name='img', attrs={'src': 'http://whatever', 'data-docma-embed': '**BAD**'})
    with pytest.raises(DocmaPackageError, match=f'Bad data-docma-embed value'):
        embed_img(tag, url_fetcher)


# ------------------------------------------------------------------------------
def test_embed_img_no_src_embed_fail(td):
    context = DocmaRenderContext(PackageReader.new(td))
    url_fetcher = partial(docma_url_fetcher, context=context)
    tag = Tag(name='img')
    with pytest.raises(DocmaPackageError, match=f'Missing or empty "src" attribute'):
        embed_img(tag, url_fetcher)


# ------------------------------------------------------------------------------
def test_embed_images_ok(td, caplog, monkeypatch):

    # Because we're messing with logger config here we need a dedicated logger
    # otherwise this config will get stomped on by another test.
    logname = 'test_embed_images_ok'
    test_logger = logging.getLogger(logname)
    test_logger.handlers.clear()
    test_logger.setLevel(logging.DEBUG)

    import docma.docma_core

    monkeypatch.setattr(docma.docma_core, 'LOG', test_logger)

    context = DocmaRenderContext(PackageReader.new(td))
    url_fetcher = partial(docma_url_fetcher, context=context)
    html = """
        <BODY>
            Yes
            <IMG src="http://localhost:8080/data/images/swatch-cyan-100x50.png"/>
            Yes
            <IMG src="docma:swatch?height=50&width=50"/>
            No
            <IMG src="http://localhost:8080/data/images/swatch-cyan-100x50.png?x=20"/>
        </BODY>
    """
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger=logname):
        docma.docma_core.embed_images(html, url_fetcher)
        assert 'Embedded 2 images out of 3' in caplog.text

    html = '<BODY>No images</BODY>'

    with caplog.at_level(logging.DEBUG, logger=logname):
        embed_images(html, url_fetcher)
        assert 'No image tags found' in caplog.text


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'path, params, expected',
    [
        ('a', {}, 'a'),
        ('/a/b', {}, '/a/b'),
        ('{{ a }}/b', {'a': 'A'}, 'A/b'),
    ],
)
def test_safe_render_path_ok(path, params, expected, tmp_path):
    with PackageReader.new(tmp_path) as tpkg:
        assert safe_render_path(path, DocmaRenderContext(tpkg, params)) == expected


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'path, params, bad_component',
    [
        ('{{ a }}/b', {'a': 'A/AA'}, '{{ a }}'),
        ('b/{{ a }}', {'a': 'A/AA'}, '{{ a }}'),
        ('b/{{ a }}', {'a': 'A"AA'}, '{{ a }}'),
        ('b/{{ a }}', {'a': "A'AA"}, '{{ a }}'),
        ('b/{{ a }}', {'a': '..'}, '{{ a }}'),
    ],
)
def test_safe_render_path_fail(path, params, bad_component, tmp_path):
    with PackageReader.new(tmp_path) as tpkg:
        with pytest.raises(ValueError, match=bad_component):
            safe_render_path(path, DocmaRenderContext(tpkg, params))


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'doc_name, compare_file',
    # compare_file is relative to test base dir
    [
        ('content/hello-world.html', 'templates/test1.src/content/hello-world.html'),
        ('http://localhost:8080/index.html', 'services/web/www.d/index.html'),
    ],
)
def test_get_document_content_ok(doc_name, compare_file, dirs, tmp_path):
    compile_template(dirs.templates / 'test1.src', str(tmp_path))

    with PackageReader.new(tmp_path) as tpkg:
        content = get_document_content(doc_name, DocmaRenderContext(tpkg))
        assert content == Path(dirs.test / compare_file).read_bytes()


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'doc_name',
    # compare_file is relative to test base dir
    [
        'no-such-file.html',
        'http://localhost:8080/no-such-file.html',
    ],
)
def test_get_document_content_fail(doc_name, dirs, tmp_path):
    compile_template(dirs.templates / 'test1.src', str(tmp_path))

    with PackageReader.new(tmp_path) as tpkg:
        with pytest.raises(DocmaPackageError, match=doc_name):
            get_document_content(doc_name, DocmaRenderContext(tpkg))


# ------------------------------------------------------------------------------
def test_render_document_to_pdf_ok(dirs, tmp_path):
    test_text = 'I watched C-beams glitter in the dark off the Tannhauser Gate'
    compile_template(dirs.templates / 'test1.src', str(tmp_path))
    with PackageReader.new(tmp_path) as tpkg:
        context = DocmaRenderContext(tpkg, {'test': {'text': test_text}})
        # First try a HTML doc
        pdf = document_to_pdf('content/hello-world.html', context)
        assert len(pdf.pages) == 1
        assert test_text in pdf.pages[0].extract_text(0)

        # PDFs should pass straight through
        pdf = document_to_pdf('content/hello-world.pdf', context)
        assert len(pdf.pages) == 1
        assert 'Hello world' in pdf.pages[0].extract_text(0)


# ------------------------------------------------------------------------------
def test_render_document_to_pdf_no_such_doc_fail(dirs, tmp_path):
    compile_template(dirs.templates / 'test1.src', str(tmp_path))
    with PackageReader.new(tmp_path) as tpkg:
        with pytest.raises(DocmaPackageError, match='Not found'):
            document_to_pdf('content/no-such-file.html', DocmaRenderContext(tpkg))


# ------------------------------------------------------------------------------
def test_render_document_to_pdf_render_fail(dirs, tmp_path):
    compile_template(dirs.templates / 'test1.src', str(tmp_path))
    with PackageReader.new(tmp_path) as tpkg:
        with pytest.raises(Exception, match='Error rendering'):
            # Template requires the `test` var to be set
            document_to_pdf('content/hello-world.html', DocmaRenderContext(tpkg))


# ------------------------------------------------------------------------------
def test_render_document_to_pdf_unknown_type_fail(dirs, tmp_path):
    compile_template(dirs.templates / 'test1.src', str(tmp_path))
    with PackageReader.new(tmp_path) as tpkg:
        with pytest.raises(DocmaPackageError, match='Unknown type'):
            document_to_pdf('content/compile-me.md', DocmaRenderContext(tpkg))


# ------------------------------------------------------------------------------
def test_render_template_to_pdf_ok(dirs, tmp_path):
    compile_template(dirs.templates / 'test1.src', str(tmp_path))
    test_text = 'Welcome to docma!'

    pdf = render_template_to_pdf(str(tmp_path), {})
    assert test_text in pdf.pages[0].extract_text(0)

    # Let's try with some overlays
    pdf = render_template_to_pdf(str(tmp_path), {}, watermark=['grid'])
    assert test_text in pdf.pages[0].extract_text(0)

    pdf = render_template_to_pdf(str(tmp_path), {}, stamp=['grid'])
    assert test_text in pdf.pages[0].extract_text(0)

    # Try compression
    pdf = render_template_to_pdf(str(tmp_path), {}, compression=True)
    assert test_text in pdf.pages[0].extract_text(0)


# ------------------------------------------------------------------------------
def test_render_document_to_html_ok(dirs, tmp_path):
    test_text = 'I watched C-beams glitter in the dark off the Tannhauser Gate'
    compile_template(dirs.templates / 'test1.src', str(tmp_path))
    with PackageReader.new(tmp_path) as tpkg:
        context = DocmaRenderContext(tpkg, {'test': {'text': test_text}})
        # First try a HTML doc
        html = document_to_html('content/hello-world.html', context)
        assert test_text in html.text


# ------------------------------------------------------------------------------
def test_render_document_to_html_no_such_doc_fail(dirs, tmp_path):
    compile_template(dirs.templates / 'test1.src', str(tmp_path))
    with PackageReader.new(tmp_path) as tpkg:
        with pytest.raises(DocmaPackageError, match='Not found'):
            document_to_html('content/no-such-file.html', DocmaRenderContext(tpkg))


# ------------------------------------------------------------------------------
def test_render_document_to_html_unknown_type_fail(dirs, tmp_path):
    compile_template(dirs.templates / 'test1.src', str(tmp_path))
    with PackageReader.new(tmp_path) as tpkg:
        with pytest.raises(DocmaPackageError, match='Not a HTML file'):
            document_to_html('content/compile-me.md', DocmaRenderContext(tpkg))


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'doc_location',
    ['local', 'http'],
)
def test_render_template_to_pdf_remote_content_ok(doc_location, dirs, tmp_path):
    compile_template(dirs.templates / 'test2.src', str(tmp_path))
    pdf = render_template_to_pdf(str(tmp_path), {'doc_location': doc_location})

    assert len(pdf.pages) == 1
    assert f'This document is from {doc_location}' in pdf.pages[0].extract_text(0)


# ------------------------------------------------------------------------------
@mock_aws
def test_render_template_to_pdf_s3_content_ok(aws_mock_creds, dirs, tmp_path):
    # Create a dummy html file in S3. This is referenced in the template config.yaml
    bucket_name = 'test-bucket'
    filename = 's3.html'
    body_text = 'This document is from S3'
    s3rsc = boto3.resource('s3')
    bucket = s3rsc.Bucket(bucket_name)
    bucket.create()
    bucket.Object(filename).put(Body=f'<HTML><BODY>{body_text}</BODY></HTML>'.encode('UTF-8'))

    compile_template(dirs.templates / 'test2.src', str(tmp_path))
    pdf = render_template_to_pdf(str(tmp_path), {'doc_location': 's3'})

    assert len(pdf.pages) == 1
    assert body_text in pdf.pages[0].extract_text(0)


# ------------------------------------------------------------------------------
def test_render_template_to_pdf_no_docs_fail(dirs, tmp_path):
    compile_template(dirs.templates / 'test2.src', str(tmp_path))
    with pytest.raises(DocmaPackageError, match='No documents were selected'):
        render_template_to_pdf(str(tmp_path), {'doc_location': 'no-docs-selected'})


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'doc_location',
    ['local', 'http'],
)
def test_render_template_to_html_remote_content_ok(doc_location, dirs, tmp_path):
    compile_template(dirs.templates / 'test2.src', str(tmp_path))
    html = render_template_to_html(str(tmp_path), {'doc_location': doc_location})

    assert f'This document is from {doc_location}' in html.text


# ------------------------------------------------------------------------------
@mock_aws
def test_render_template_to_html_s3_content_ok(aws_mock_creds, dirs, tmp_path):
    # Create a dummy html file in S3. This is referenced in the template config.yaml
    bucket_name = 'test-bucket'
    filename = 's3.html'
    body_text = 'This document is from S3'
    s3rsc = boto3.resource('s3')
    bucket = s3rsc.Bucket(bucket_name)
    bucket.create()
    bucket.Object(filename).put(Body=f'<HTML><BODY>{body_text}</BODY></HTML>'.encode('UTF-8'))

    compile_template(dirs.templates / 'test2.src', str(tmp_path))
    html = render_template_to_html(str(tmp_path), {'doc_location': 's3'})

    assert body_text in html.text


# ------------------------------------------------------------------------------
def test_render_template_to_html_ok(dirs, tmp_path):
    compile_template(dirs.templates / 'test1.src', str(tmp_path))
    html = render_template_to_html(str(tmp_path), {'doc_location': 's3'})
    assert html.head.title.text.strip() == 'Welcome to docma!'


# ------------------------------------------------------------------------------
def test_render_template_to_html_no_docs_fail(dirs, tmp_path):
    compile_template(dirs.templates / 'test2.src', str(tmp_path))
    with pytest.raises(DocmaPackageError, match='No documents were selected'):
        render_template_to_html(str(tmp_path), {'doc_location': 'no-docs-selected'})


# ------------------------------------------------------------------------------
def test_set_metadata_html_ok(td):
    soup = BeautifulSoup(
        '<html><head><meta name="title" content="---"></head></html>', 'html.parser'
    )
    context = DocmaRenderContext(PackageReader.new(td), params={'title': 'Title'})

    metadata = DocumentMetadata(title='{{ title }}', description='Description')
    set_metadata_html(soup, metadata, context)
    html = """<html>
 <head>
  <meta content="Title" name="title"/>
  <meta content="Description" name="description"/>
 </head>
</html>
"""
    assert soup.prettify() == html


# ------------------------------------------------------------------------------
def test_set_metadata_html_no_head_ok(td):
    soup = BeautifulSoup('<html><body></body></html>', 'html.parser')
    context = DocmaRenderContext(PackageReader.new(td), params={'title': 'Title'})

    metadata = DocumentMetadata(title='{{ title }}', description='Description')
    set_metadata_html(soup, metadata, context)
    html = """<html>
 <head>
  <meta content="Title" name="title"/>
  <meta content="Description" name="description"/>
 </head>
 <body>
 </body>
</html>
"""
    assert soup.prettify() == html


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "width_1, height_1, width_2, height_2, are_similar",
    [
        (210, 297, 210, 297, True),
        (208, 300, 210, 297, True),
        (210, 297, 212, 295, True),
        (210, 297, 297, 210, False),
    ],
)
def test_rectangles_approx_equal(width_1, height_1, width_2, height_2, are_similar):

    def mm_to_pdfu(mm: int | float) -> float:
        """Convert mm to PDF units (1/72")."""
        return mm / 25.4 * 72

    assert (
        rectangles_approx_equal(
            RectangleObject((0, 0, mm_to_pdfu(width_1), mm_to_pdfu(height_1))),
            RectangleObject((0, 0, mm_to_pdfu(width_2), mm_to_pdfu(height_2))),
        )
        == are_similar
    )
