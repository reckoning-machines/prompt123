"""PromptDraft - a structured, governed candidate prompt.

A PromptDraft is derived from a PromptIntent. It is advisory: a proposal,
never a decision. It carries proofing context that explains how it was
shaped, in keeping with the explainability rule in the product contract.

This module is a placeholder. No proofing logic is implemented yet.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptDraft:
    """A governed candidate prompt awaiting explicit approval.

    Attributes:
        text: The structured candidate prompt text.
        source_intent_hash: Deterministic hash of the originating
            PromptIntent.
        explanation: Human-readable account of what changed and why.
    """

    text: str
    source_intent_hash: str
    explanation: str
