# prompt123 Product Contract

This document is the governing contract for prompt123. It defines what the
project is, what it is not, and the rules that constrain its behavior.
Code and design decisions defer to this contract.

## Product Thesis

prompt123 is a governed prompt proofing and optimization system.

It helps domain experts create better AI prompts without requiring
expertise in prompt engineering.

prompt123 transforms raw user intent into proofing findings and
reviewable `PromptDraft` artifacts by identifying defects, ambiguity,
missing constraints, hidden assumptions, and opportunities for
improvement.

A successful proofing result improves the likelihood of producing the
user's intended outcome while preserving the user's intent.

prompt123 produces artifacts. It does not execute them.

prompt123 is NOT:

- an execution engine
- a chat assistant
- an autonomous agent
- a workflow runtime
- a model orchestration system
- a memory system
- a prompt-generation system
- a fin123 replacement

Users remain the source of intent. prompt123 critiques, explains, and
improves prompts; it does not replace the author's intent with its own.

## Question and Method Doctrine

Most users are not trying to author prompts. They are trying to:

- ask a Question
- optionally provide a Method

Definitions:

- Question: what should be produced.
- Method: how reasoning should occur.

Question and Method may exist independently.

Method remains optional.

Question and Method are conceptual components of `PromptIntent`, not
separate canonical artifacts in prompt123. A `PromptIntent` may contain
a Question, a Method, or both.

prompt123 helps transform Questions and optional Methods into
reviewable `PromptDraft` artifacts.

prompt123 does not require Methods. Many valid prompts consist only of
a Question.

## Optimization Doctrine

Optimization means improving prompt quality while preserving the
author's intended objective.

Optimization may include:

- stronger output specifications,
- clearer instructions,
- reduced ambiguity,
- improved determinism,
- better prompt structure,
- improved model comprehension.

Optimization must not alter the author's intended objective.

## Findings Doctrine

Findings are the primary output of prompt123.

prompt123 returns:

- Findings
- Suggested Improvements
- Suggested PromptDrafts

while preserving the original intent.

A finding explains:

- what was observed,
- why it matters,
- how it may affect prompt quality,
- and, when appropriate, how it may be improved.

Findings may identify:

- ambiguity,
- missing constraints,
- missing output specifications,
- hidden assumptions,
- prompt-engineering weaknesses,
- optimization opportunities,
- mixing of Question and Method responsibilities.

Findings are advisory. They do not modify intent. They do not approve
prompts.

Optimization findings identify improvements that may make a prompt more
effective without changing the author's intended objective. For
example, an optimization finding may suggest an explicit output schema,
clearer instruction order, stronger constraints, or wording that is
easier for a model to interpret.

## Purpose: Determinism Without Erasing Intent

prompt123 exists to make LLM prompts as deterministic as possible
without erasing user intent.

Users may express vague, incomplete, or informal intent. prompt123
transforms that intent into findings and a reviewable governed
PromptDraft by identifying ambiguity, missing schema, hidden
assumptions, nondeterministic wording, and unsafe external dependencies.

The goal is not to make prompts more clever. The goal is to make
prompts more deterministic, explainable, reviewable, and replay-safe.
The goal is not to teach users prompt engineering. The goal is to help
users obtain better AI outputs while preserving their intent.

prompt123 identifies defects and opportunities for improvement so
users can focus on domain expertise rather than prompt construction.

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
  explains how it was shaped. A suggested `PromptDraft` is a proposal
  for review, not a statement of correctness.
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
- prompt123 must distinguish between what should be produced and how
  reasoning should occur. When these concepts are mixed, prompt123 may
  surface findings and suggest improvements, but it must not silently
  separate or rewrite them.

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

Deterministic, rule-based proofing is foundational and remains valid on
its own. It is, however, expected to be insufficient by itself for
understanding vague, informal, or underspecified human intent.
Deterministic rules can detect known patterns; they cannot reliably
interpret intent that was never stated clearly. For that reason
prompt123 is likely to require LLM-assisted proofing in the future. The
following doctrine governs that direction in advance.

Deterministic rule-based proofing remains foundational. LLM-assisted
proofing is additive: it extends the deterministic substrate and never
replaces it.

LLM-assisted proofing may help to:

- identify ambiguity in analyst intent,
- suggest output schemas,
- identify hidden assumptions and execution expectations,
- identify prompt-engineering weaknesses,
- suggest improved prompt structure,
- suggest stronger output specifications,
- propose normalized draft language,
- propose optimized wording while preserving intent,
- suggest clarification questions.

LLM-assisted proofing must not:

- silently rewrite prompts,
- approve prompts,
- execute prompts,
- resolve ambiguity silently,
- invent missing constraints and present them as truth,
- replace deterministic proofing rules.

Governing rules:

- LLM-assisted proofing is advisory, not authoritative. It produces
  proposals, never decisions.
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

Any future LLM-assisted proofing contribution must itself become
replayable governance evidence. Each LLM-assisted run must persist, at
least:

- the proofing prompt snapshot,
- the provider, model, and model version,
- a config hash for the proofing run,
- the semantic contract version,
- the proofing rule version,
- the generated findings.

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
