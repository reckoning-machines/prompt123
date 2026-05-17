"""Minimal placeholder tests for the prompt123 scaffold.

These tests confirm the package imports and that the canonical ontology
dataclasses construct. They contain no execution logic.
"""

from prompt123 import __version__
from prompt123.approval import ApprovedPrompt
from prompt123.draft import PromptDraft
from prompt123.execution_artifact import ExecutionArtifact
from prompt123.hashing import prompt_hash
from prompt123.intent import PromptIntent
from prompt123.validation import is_non_empty


def test_version_present():
    assert __version__


def test_ontology_dataclasses_construct():
    intent = PromptIntent(text="summarize the portfolio", author="analyst")
    draft = PromptDraft(
        text="Summarize the portfolio as of the stated as-of date.",
        source_intent_hash=prompt_hash(intent.text),
        explanation="Added an explicit as-of constraint.",
    )
    approved = ApprovedPrompt(
        text=draft.text,
        source_draft_hash=prompt_hash(draft.text),
        approved_by="reviewer",
    )
    artifact = ExecutionArtifact(
        text=approved.text,
        approved_prompt_hash=prompt_hash(approved.text),
        artifact_hash=prompt_hash(approved.text),
    )
    assert artifact.text == intent.text or artifact.text == draft.text


def test_prompt_hash_is_deterministic():
    assert prompt_hash("same text") == prompt_hash("same text")
    assert prompt_hash("a") != prompt_hash("b")


def test_is_non_empty_placeholder():
    assert is_non_empty("text")
    assert not is_non_empty("   ")
