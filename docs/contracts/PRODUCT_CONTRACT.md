# prompt123 Product Contract

This document is the governing contract for prompt123. It defines what the
project is, what it is not, and the rules that constrain its behavior.
Code and design decisions defer to this contract.

## Product Thesis

prompt123 is a governed prompt proofing layer for institutional LLM
execution systems.

It helps transform raw analyst intent into reviewable `PromptDraft`
artifacts. It exists so that prompts entering an execution system are
structured, explained, and traceable before anyone approves them.

prompt123 is NOT:

- an execution engine
- a chat assistant
- an autonomous agent
- a workflow runtime
- a model orchestration system
- a memory system
- a fin123 replacement

prompt123 produces artifacts. It does not run them.

## Purpose: Determinism Without Erasing Intent

prompt123 exists to make LLM prompts as deterministic as possible
without erasing user intent.

Users may express vague, incomplete, or informal intent. prompt123
transforms that intent into a reviewable governed PromptDraft by
identifying ambiguity, missing schema, hidden assumptions,
nondeterministic wording, and unsafe external dependencies.

The goal is not to make prompts more clever. The goal is to make
prompts more deterministic, explainable, reviewable, and replay-safe.

Doctrine:

- User intent may be vague.
- PromptDrafts must make ambiguity explicit.
- prompt123 may propose clarifications or normalized draft language.
- prompt123 must preserve the original intent unchanged.
- prompt123 must never silently decide what the user meant.
- If intent remains ambiguous, the draft carries findings rather than
  inventing certainty.
- LLM-assisted proofing may help detect ambiguity or propose normalized
  language, but it remains advisory.
- Approval remains explicit and downstream.
- Execution remains downstream.

## Canonical Ontology

prompt123 recognizes a single canonical chain. Every concept in the
project maps onto one of these stages.

```
PromptIntent -> PromptDraft -> ApprovedPrompt -> ExecutionArtifact -> Audit
```

Definitions:

- `PromptIntent` is raw human intent. It is whatever the analyst wrote or
  meant, captured without judgment. It is not assumed to be correct,
  complete, or safe.
- `PromptDraft` is a structured, governed candidate prompt derived from a
  `PromptIntent`. It is advisory. It carries the proofing context that
  explains how it was shaped.
- `ApprovedPrompt` is a pinned, reviewed execution prompt. Approval is an
  explicit human or system act. An `ApprovedPrompt` references the
  `PromptDraft` it came from.
- `ExecutionArtifact` is an immutable execution-time snapshot of an
  approved prompt. It is the exact text and metadata used at execution.
  It never changes after creation.
- `Audit` is a replayable explanation of prompt provenance. It links the
  full chain so any executed prompt can be traced back to its intent.

## Governance Doctrine

These rules are binding.

- PromptDrafts are advisory. A draft is a proposal, never a decision.
- Approval must be explicit. No prompt becomes an `ApprovedPrompt` by
  default, by timeout, or by inference.
- Silent prompt rewriting is forbidden. prompt123 may propose changes,
  but it must never alter a prompt and present the result as the
  original.
- Execution systems own execution authority. prompt123 does not execute
  prompts and does not decide when prompts run.
- Historical replay must use immutable prompt artifacts. Replay reads
  `ExecutionArtifact` records, never live or regenerated prompts.
- New prompt versions must not silently replace historical prompts. A
  new version is a new artifact. Prior artifacts remain intact and
  referenceable.
- Prompt hashing and versioning must be deterministic. The same prompt
  content must always produce the same content hash. Version identity is
  distinct from the content hash: it incorporates versioning and approval
  context, so identical content can still belong to more than one
  artifact. A new approval or version produces a distinct artifact even
  when its content hash is unchanged. Both the content hash and the
  version identity must be computed deterministically.
- Prompt proofing must be explainable. Every transformation from intent
  to draft must carry a human-readable account of what changed and why.

## Future Integration Direction

This section documents direction only. None of it is implemented here.

- fin123 may consume `ApprovedPrompt` artifacts later. fin123 would own
  approval and execution; prompt123 would only supply governed drafts
  and the artifacts approval produces.
- YAP may help discuss and clarify prompt intent later, upstream of
  `PromptIntent` capture.
- prompt123 itself does not execute prompts, and this contract does not
  authorize it to.

## Future LLM-Assisted Proofing

This section documents direction only. None of it is implemented here.

prompt123 may eventually use an LLM to assist proofing. The following
doctrine governs that possibility in advance.

- LLM-assisted proofing may propose findings, structural normalization,
  or candidate draft language.
- LLM-assisted proofing is advisory only. It produces proposals, never
  decisions.
- PromptDraft artifacts remain reviewable regardless of how their
  findings were produced.
- Silent rewriting is forbidden. An LLM proposal never replaces the
  original intent text without a recorded, reviewable finding.
- Proofing suggestions must be explainable and attributable. Every
  suggestion records what it proposes, why, and that an LLM produced it.
- ApprovedPrompt artifacts still require explicit approval by downstream
  systems. LLM-assisted proofing does not approve anything.
- prompt123 does not gain execution authority by using LLM-assisted
  proofing.

LLM-assisted proofing is allowed only to improve determinism and
explainability. It may propose findings, clarification questions, or
normalized draft language, but it must not silently resolve ambiguity,
invent missing constraints, approve prompts, execute prompts, or replace
deterministic proofing rules.

Clarifications:

- LLM-assisted proofing is a future, optional subsystem.
- Deterministic, rule-based proofing remains fully valid on its own and
  requires no LLM.
- Any future LLM contribution must itself become replayable governance
  evidence.

A future LLM-assisted proofing pass must persist replay metadata,
including at least:

- model, provider, and model version
- a snapshot of the proofing prompt used
- a config hash for the proofing run
- the semantic contract version
- the proofing rule version

Replay reads this persisted metadata. It never re-queries a current
model.

## Scope Boundaries

The initial repository deliberately excludes:

- runtime LLM calls
- external API calls
- agent behavior
- embeddings or vector databases
- a web UI
- fin123 integration

These exclusions are part of the contract, not a temporary state. Any
proposal to add them must update this document first.
