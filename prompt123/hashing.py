"""Deterministic prompt hashing.

The product contract requires that prompt hashing and versioning be
deterministic: the same prompt content must always produce the same hash
and version identity.

This module provides a single small, deterministic helper. It is
intentionally minimal and has no further implementation.
"""

from __future__ import annotations

import hashlib


def prompt_hash(text: str) -> str:
    """Return a deterministic hex hash of prompt text.

    The same input text always yields the same hash. This function is the
    canonical hashing primitive for the ontology stages.

    Args:
        text: The prompt text to hash.

    Returns:
        A lowercase hex SHA-256 digest of the UTF-8 encoded text.
    """

    return hashlib.sha256(text.encode("utf-8")).hexdigest()
