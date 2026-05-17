"""ApprovedPrompt - a pinned, reviewed execution prompt.

Approval is an explicit act. No PromptDraft becomes an ApprovedPrompt by
default, by timeout, or by inference. An ApprovedPrompt references the
PromptDraft it came from so provenance stays intact.

This module is a placeholder. No approval logic is implemented yet.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ApprovedPrompt:
    """A reviewed prompt explicitly cleared for downstream execution.

    Attributes:
        text: The approved prompt text.
        source_draft_hash: Deterministic hash of the originating
            PromptDraft.
        approved_by: Identifier of the human or system that approved it.
    """

    text: str
    source_draft_hash: str
    approved_by: str
