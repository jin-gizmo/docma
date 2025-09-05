"""Test S3 importer."""

from __future__ import annotations

import boto3
import pytest
from moto import mock_aws

from docma.importers import import_content
from docma.exceptions import DocmaImportError


# ------------------------------------------------------------------------------
@mock_aws()
def test_import_s3_ok(aws_mock_creds):
    content = b'Hello world'
    bucket_name = 'test-bucket'
    filename = 'test.txt'

    s3rsc = boto3.resource('s3')
    bucket = s3rsc.Bucket(bucket_name)
    bucket.create()

    with pytest.raises(DocmaImportError, match='does not exist'):
        import_content(f's3://{bucket_name}/{filename}')

    obj = bucket.Object(filename)
    obj.put(Body=content)

    assert import_content(f's3://{bucket_name}/{filename}') == content

    with pytest.raises(DocmaImportError, match='Too large'):
        import_content(f's3://{bucket_name}/{filename}', max_size=1)
