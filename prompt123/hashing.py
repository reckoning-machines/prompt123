"""Deterministic prompt hashing.

The product contract requires that prompt hashing be deterministic: the
same prompt content must always produce the same content hash. Version
identity is a separate concept that also incorporates versioning and
approval context, so identical content can still belong to distinct
artifacts. This module covers the content hash only.

This module provides a single small, deterministic helper. It is
intentionally minimal and has no further implementation.
"""

from __future__ import annotations

import hashlib


def prompt_hash(text: str) -> str:
    """Return a deterministic content hash of prompt text.

    The same input text always yields the same hash. This is a content
    hash only; it does not encode versioning or approval context, and so
    it is not a version identity on its own.

    Args:
        text: The prompt text to hash.

    Returns:
        A lowercase hex SHA-256 digest of the UTF-8 encoded text.
    """

    return hashlib.sha256(text.encode("utf-8")).hexdigest()
