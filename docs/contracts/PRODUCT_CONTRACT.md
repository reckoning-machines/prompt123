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
  content must always produce the same hash and version identity.
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
