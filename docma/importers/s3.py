"""Import document content from S3."""

from __future__ import annotations

from functools import lru_cache

import boto3

from docma.exceptions import DocmaImportError
from .__common__ import content_importer


# ------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def s3resource():
    """Get a singleton boto3 S3 resource."""
    return boto3.Session().resource('s3')


# ------------------------------------------------------------------------------
@content_importer('s3')
def s3(url: str, max_size: int = 0) -> bytes:
    """Get an object from S3."""

    bucket, key = url.removeprefix('s3://').split('/', 1)
    s3obj = s3resource().Bucket(bucket).Object(key)
    if max_size and s3obj.content_length > max_size:
        raise DocmaImportError(f'{url}: Too large')
    return s3obj.get()['Body'].read()
