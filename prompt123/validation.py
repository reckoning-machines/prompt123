"""Prompt validation - placeholder.

Validation in prompt123 is about governance, not optimization. It checks
that artifacts are well-formed and that the chain from intent to artifact
stays explainable. It never silently rewrites a prompt.

This module is a placeholder. No validation rules are implemented yet.
"""

from __future__ import annotations


def is_non_empty(text: str) -> bool:
    """Return True if prompt text is present and not blank.

    This is a placeholder check. Real governance validation is not
    implemented in the initial scaffold.

    Args:
        text: The prompt text to check.

    Returns:
        True if the text contains non-whitespace characters.
    """

    return bool(text and text.strip())
