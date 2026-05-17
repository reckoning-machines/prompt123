"""PromptIntent - raw human intent.

A PromptIntent captures whatever an analyst wrote or meant, without
judgment. It is not assumed to be correct, complete, or safe. It is the
first stage of the canonical ontology and the only stage that is not
governed.

This module is a placeholder. No proofing logic is implemented yet.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptIntent:
    """Raw, ungoverned analyst prompt intent.

    Attributes:
        text: The raw prompt text as the analyst supplied it.
        author: Identifier of the analyst who supplied the intent.
    """

    text: str
    author: str
