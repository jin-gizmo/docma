"""Test S3 URL fetcher."""

from __future__ import annotations

from urllib.parse import urlparse

import boto3
import pytest
from moto import mock_aws

import docma.url_fetchers.s3
from docma.exceptions import DocmaUrlFetchError
from docma.lib.core import DocmaRenderContext
from docma.lib.packager import PackageReader
from docma.url_fetchers import get_url_fetcher_for_scheme


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filename,mime_type',
    [
        ('custard100.csv', 'text/csv'),
        ('images/swatch-cyan-100x50.png', 'image/png'),
    ],
)
@mock_aws()
def test_s3_url_fetcher_ok(filename: str, mime_type: str, td, aws_mock_creds):
    # Upload our content to (mock) S3
    bucket_name = 'test-bucket'
    s3rsc = boto3.resource('s3')
    bucket = s3rsc.Bucket(bucket_name)
    bucket.create()
    obj = bucket.Object(filename)
    obj.put(Body=(td / filename).read_bytes())

    # Import it back
    purl = urlparse(f's3://{bucket_name}/{filename}')
    fetcher = get_url_fetcher_for_scheme(purl.scheme)
    url_info = fetcher(purl, DocmaRenderContext(PackageReader.new(td)))
    assert url_info['string'] == (td / filename).read_bytes()
    assert url_info['mime_type'] == mime_type


# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'filename,mime_type',
    [
        ('custard100.csv', 'text/csv'),
    ],
)
@mock_aws()
def test_s3_url_fetcher_too_big(filename: str, mime_type: str, td, aws_mock_creds, monkeypatch):
    # Upload our content to (mock) S3
    bucket_name = 'test-bucket'
    s3rsc = boto3.resource('s3')
    bucket = s3rsc.Bucket(bucket_name)
    bucket.create()
    obj = bucket.Object(filename)
    obj.put(Body=(td / filename).read_bytes())

    monkeypatch.setattr(docma.url_fetchers.s3, 'IMPORT_MAX_SIZE', 1)
    # Import it back
    purl = urlparse(f's3://{bucket_name}/{filename}')
    fetcher = get_url_fetcher_for_scheme(purl.scheme)
    with pytest.raises(DocmaUrlFetchError, match='Too large'):
        fetcher(purl, DocmaRenderContext(PackageReader.new(td)))


# ------------------------------------------------------------------------------
@mock_aws()
def test_s3_url_fetcher_fail(td, aws_mock_creds):

    bucket_name = 'test-bucket'
    filename = 'no-such-file.txt'
    s3rsc = boto3.resource('s3')
    bucket = s3rsc.Bucket(bucket_name)
    bucket.create()

    purl = urlparse(f's3://{bucket_name}/{filename}')
    fetcher = get_url_fetcher_for_scheme(purl.scheme)
    with pytest.raises(DocmaUrlFetchError, match='Not Found'):
        fetcher(purl, DocmaRenderContext(PackageReader.new(td)))
