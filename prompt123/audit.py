"""Audit - a replayable explanation of prompt provenance.

An Audit links the full canonical chain so any executed prompt can be
traced back to its originating intent. It is the final stage of the
ontology:

    PromptIntent -> PromptDraft -> ApprovedPrompt -> ExecutionArtifact -> Audit

An Audit references artifacts by hash; it does not regenerate prompts.
Historical replay reads Audit and ExecutionArtifact records, never live
prompts.

This module is a placeholder. No audit or replay logic is implemented yet.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Audit:
    """A provenance record linking one execution back to its intent.

    Attributes:
        intent_hash: Content hash of the originating PromptIntent.
        draft_hash: Content hash of the PromptDraft.
        approved_prompt_hash: Content hash of the ApprovedPrompt.
        execution_artifact_hash: Hash of the ExecutionArtifact that was
            executed.
    """

    intent_hash: str
    draft_hash: str
    approved_prompt_hash: str
    execution_artifact_hash: str
