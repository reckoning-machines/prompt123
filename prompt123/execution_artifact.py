"""ExecutionArtifact - an immutable execution-time prompt snapshot.

An ExecutionArtifact is the exact text and metadata used at execution
time. It never changes after creation. Historical replay reads these
artifacts; it never regenerates prompts. New prompt versions create new
artifacts and never replace prior ones.

prompt123 does not execute prompts. It only describes the artifact shape
that an execution system would record.

This module is a placeholder. No execution logic is implemented here.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionArtifact:
    """An immutable snapshot of an approved prompt at execution time.

    Attributes:
        text: The exact prompt text used at execution.
        approved_prompt_hash: Deterministic hash of the ApprovedPrompt.
        artifact_hash: Deterministic hash of this artifact's contents.
    """

    text: str
    approved_prompt_hash: str
    artifact_hash: str
