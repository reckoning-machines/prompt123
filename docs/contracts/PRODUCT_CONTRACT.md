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

## LLM-Assisted Proofing

The proofing layer uses two components in sequence: a deterministic
pre-filter and an LLM proofer. They are not interchangeable. Each
has a defined scope.

### Deterministic Pre-Filter

The deterministic pre-filter runs first on every input. It handles
basic, pattern-matchable checks that do not require language
understanding: profanity, disallowed content, formatting violations,
and other simple rules. It is fast, cheap, and requires no model call.
Findings from the pre-filter carry ProofingSource.deterministic.

The pre-filter is foundational. It runs regardless of domain_profile
and cannot be disabled.

### LLM Proofer

The LLM proofer runs after the pre-filter. It is the primary proofing
engine for everything the pre-filter does not cover: ambiguity,
missing schema, hidden assumptions, nondeterministic wording, domain-
specific issues, and intent that requires language understanding to
evaluate. Findings from the LLM proofer carry ProofingSource.llm.

The LLM proofer is scoped to the declared domain_profile of the input.
Each domain_profile has its own proofing prompt. The proofing prompt
instructs the LLM what to flag and how to structure its output.

### Domain Profiles

prompt123 supports domain profiles as a mechanism for scoping the LLM
proofing prompt to a specific field. A domain_profile declaration on
a PromptIntent selects the matching proofing prompt for that domain.

Two profiles are authorized: generic and fin123. generic covers all
inputs regardless of domain. fin123 extends generic with finance-
specific proofing categories. Additional profiles require a contract
amendment.

### Governing Rules

These rules apply to the LLM proofer and are binding:

- The LLM proofer is authorized to make runtime model calls within
  the governed proofing layer only. No other component of prompt123
  may make model calls.
- LLM output is proposals and findings only. It is never a decision.
- Silent rewriting is forbidden. An LLM proposal never replaces the
  original intent text without a recorded, reviewable finding.
- Proofing suggestions must be explainable and attributable. Every
  finding records what it observed, why it matters, and that an LLM
  produced it.
- ApprovedPrompt artifacts still require explicit approval by
  downstream systems. The LLM proofer does not approve anything.
- prompt123 does not gain execution authority by using the LLM proofer.
- PromptDraft artifacts remain reviewable regardless of how their
  findings were produced.

Each LLM-assisted run must persist, at minimum:

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

- external API calls outside the governed LLM proofing layer
- agent behavior
- embeddings or vector databases
- a web UI
- fin123 integration

Runtime LLM calls are authorized within the governed LLM proofing
layer only, under the constraints in the LLM-Assisted Proofing
section above. All other exclusions are part of the contract, not a
temporary state. Any proposal to add them must update this document
first.
