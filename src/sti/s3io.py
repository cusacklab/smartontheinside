"""Cached access to the project S3 bucket.

The legacy scripts called ``s3.download_file`` inline, into hard-coded home
directories, re-downloading multi-gigabyte arrays on every run. Here every fetch
goes through a local cache keyed by the S3 key.
"""

from __future__ import annotations

import logging
from pathlib import Path

from sti.config import Config, DEFAULT_CONFIG

log = logging.getLogger(__name__)


def _client(config: Config):
    import boto3  # imported lazily so the package is usable offline

    return boto3.client("s3")


def fetch(key: str, config: Config = DEFAULT_CONFIG, *, force: bool = False) -> Path:
    """Download ``key`` from the project bucket into the local cache.

    Returns the local path. A cached copy is reused unless ``force`` is set.
    """
    dest = config.cache_dir / key
    if dest.exists() and not force:
        log.debug("cache hit: %s", key)
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    log.info("downloading s3://%s/%s -> %s", config.s3_bucket, key, dest)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    _client(config).download_file(config.s3_bucket, key, str(tmp))
    tmp.replace(dest)  # atomic, so an interrupted download never looks cached
    return dest


def exists(key: str, config: Config = DEFAULT_CONFIG) -> bool:
    """Return True if ``key`` is present in the bucket."""
    import botocore.exceptions

    try:
        _client(config).head_object(Bucket=config.s3_bucket, Key=key)
    except botocore.exceptions.ClientError:
        return False
    return True


def upload(local: Path, key: str, config: Config = DEFAULT_CONFIG) -> None:
    """Upload a local file to ``key``.

    Refuses to overwrite an existing key, because uploading each task's
    activations to one non-task-specific key is exactly how the per-task adult
    activation files were lost from the bucket.
    """
    if exists(key, config):
        raise FileExistsError(
            f"s3://{config.s3_bucket}/{key} already exists; refusing to overwrite. "
            "Pass a task/cohort-specific key, or delete the object deliberately."
        )
    log.info("uploading %s -> s3://%s/%s", local, config.s3_bucket, key)
    _client(config).upload_file(str(local), config.s3_bucket, key)
