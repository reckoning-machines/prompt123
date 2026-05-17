# Implementation Plan: PromptDraft Proofing Substrate

Plan type: first implementation plan (plan-only, no runtime behavior)
Target: a governed PromptDraft proofing and linting substrate
Status: proposed, implementation-ready
Date: 2026-05-17
Governing contract: docs/contracts/PRODUCT_CONTRACT.md

This document is a plan. It defines no runtime behavior, no LLM calls,
no APIs, no execution logic, and no fin123 integration. Implementation
is deferred to later passes, each of which must defer to the product
contract.

## 1. Product Goal

Build the first governed proofing layer that turns a `PromptIntent` into
an explainable `PromptDraft`. The layer inspects raw analyst intent,
records structured findings, and produces a draft artifact that a human
or system can review. It never decides; it only describes.

The intended flow this plan works toward:

```
PromptIntent
  -> lint / proof checks
  -> PromptDraft
  -> human or system review
  -> ApprovedPrompt
  -> ExecutionArtifact
  -> downstream execution system
```

prompt123 owns the first three stages only. Review, approval, and
everything after are owned by downstream systems.

## 2. Non-Goals

The proofing substrate does not, and this plan does not authorize it to:

- execute prompts or call any model
- approve prompts, automatically or by inference
- silently rewrite a prompt and present the result as the original
- act as an agent, workflow runtime, or orchestrator
- call external APIs or tools
- read or mutate downstream execution-system state
- generate hidden behavior or side effects
- maintain conversational memory

Normalization is explicit and recorded. It is not silent rewriting:
the original intent text is always preserved alongside the normalized
text, and every change is named in the findings.

## 3. Ontology Impact

No new canonical nouns. The plan stays within the existing chain:

```
PromptIntent -> PromptDraft -> ApprovedPrompt -> ExecutionArtifact -> Audit
```

The substrate enriches `PromptDraft` so it can carry proofing findings,
normalized text, and the versioning metadata needed for replay. It adds
supporting value objects (a finding record, severity and category
enums) that are not ontology nouns and remain subordinate to it.

## 4. Proposed Artifact Shapes

These are proposed shapes for a future pass. They are not implemented
here. All artifacts are immutable once created.

### 4.1 PromptDraft (enriched)

| Field | Purpose |
|-------|---------|
| draft_id | Stable identifier for this draft artifact. |
| source_intent_hash | Content hash of the originating PromptIntent. |
| original_text | Verbatim intent text, preserved unchanged. |
| normalized_text | Structurally normalized candidate text. |
| findings | Ordered tuple of ProofingFinding records. |
| expected_output_schema | Declared output expectation, or null if absent. |
| allowed_inputs | Declared inputs the prompt may rely on. |
| allowed_tools | Declared tools the prompt may rely on. |
| content_hash | Deterministic hash of normalized_text. |
| semantic_contract_version | Version of the artifact schema itself. |
| proofing_rule_version | Version of the rule set that produced findings. |

A draft is advisory. It is never an approval and never executable.

### 4.2 ProofingFinding

| Field | Purpose |
|-------|---------|
| rule_id | Identifier of the rule that triggered. |
| category | ProofingCategory enum value. |
| severity | ProofingSeverity enum value (error, warning, note). |
| message | Human-readable description of the issue. |
| explanation | What was observed, why it matters, what rule applies. |
| span | Optional location within the prompt text. |

### 4.3 Enums

- ProofingSeverity: error, warning, note.
- ProofingCategory: see rule categories in section 5.

## 5. Proofing Rule Categories

The rule engine is a deterministic, pure inspection of intent text and
declared metadata. Each rule emits zero or more findings. No rule
mutates state and no rule executes anything.

Initial categories:

- structure: unnormalized or unstructured prompt layout.
- ambiguity: ambiguous or unbounded output expectations.
- open_ended: unsupported open-ended instructions with no stopping
  condition.
- missing_schema: no explicit expected output schema.
- hidden_data: hidden assumptions about external or live data.
- hidden_tool: hidden tool or runtime assumptions not declared.
- unsupported_pattern: prompt patterns the substrate does not support.
- mutable_reference: unsafe references to mutable or undated sources.
- nondeterministic_wording: wording that invites nondeterministic
  output.

Each rule has a stable rule_id and belongs to a versioned rule set
(proofing_rule_version). Adding or changing rules bumps that version.

## 6. Explainability

Every finding must be explainable. A finding records:

- what was observed in the intent,
- why it matters under the governance doctrine,
- which rule_id and rule version triggered it.

Where the substrate normalizes text, the normalization is itemized in
the findings so a reviewer can see each change and its reason. There is
no transformation without a recorded explanation. This satisfies the
contract rule that proofing must be explainable.

## 7. Error and Finding Taxonomy

Severity is governance-meaningful, not cosmetic. Downstream systems
read severity to decide review handling.

- ERROR: the draft cannot be approved downstream without remediation.
  An error marks a governance defect: a missing schema, a hidden
  execution assumption, or an unsupported pattern. A draft with one or
  more open errors is not approvable as-is.
- WARNING: the reviewer must explicitly acknowledge the finding before
  approval. A warning does not block approval, but approval must not
  proceed silently past it.
- NOTE: informational only. It requires no acknowledgement and does not
  affect approvability.

Rules:

- Severity is assigned by the rule, deterministically, from the same
  input.
- prompt123 records severity; it never clears or downgrades a finding.
- Remediation produces a new draft (append-only), not an edit of the
  finding.
- A draft's approvability is derived from its findings, never stored as
  a separate mutable flag.

## 8. Determinism, Version, and Hash Invariants

Four distinct identities must not be conflated:

- content_hash: deterministic hash of prompt text only. Equal text
  yields an equal content_hash. It is text-only and is not an identity
  for an artifact.
- version_identity: content_hash plus semantic_contract_version plus
  proofing_rule_version. Identifies a draft as produced under a specific
  schema and rule set. Equal text under a newer rule set is a distinct
  version_identity.
- approval_identity: version_identity plus the approval context
  (approver and the explicit approval act). Identifies an
  ApprovedPrompt. Approval is always explicit.
- execution_artifact_identity: the identity of an ExecutionArtifact,
  adding the execution-time snapshot context. It belongs to the
  downstream execution system and is out of scope for prompt123.

Invariants:

- All identities prompt123 owns are computed deterministically from
  their inputs.
- content_hash never includes schema or rule version; those belong to
  version_identity.
- A new rule version or a new approval produces a distinct artifact even
  when content_hash is unchanged.
- Identity inputs are ordered deterministically before hashing so the
  same logical artifact always yields the same identity.

## 9. Normalization Policy

- original_text is always preserved, verbatim, on the draft.
- normalized_text is never presented as the original and never
  overwrites original_text.
- Every normalization produces a finding describing what changed and
  why.
- For v0, normalization is record-only: the substrate describes the
  normalization it would apply but does not apply it automatically.
  Applying a normalization is a later, separately gated decision.
- A draft with no findings has normalized_text equal to original_text.

## 10. Data Model Invariants

All artifact and value-object types must satisfy:

- frozen dataclasses: every type is `@dataclass(frozen=True)`. No field
  is reassigned after construction.
- no mutable default fields: no list, dict, or set defaults. Collections
  are tuples. Defaults are immutable or absent.
- deterministic ordering: findings and any other collections are stored
  in a defined, stable order. The same inputs always yield the same
  order.
- no silent mutation: there are no in-place setters. A change is a new
  artifact that references its predecessor.
- no execution behavior: models carry data and pure derived properties
  only. No model performs I/O, network calls, or prompt execution.

## 11. Replay and Governance Doctrine

- Proofed drafts are replayable artifacts. A PromptDraft records the rule
  version and schema version used, so it can be re-read exactly as it was
  produced.
- Drafts and downstream artifacts are append-only. A revision is a new
  artifact that references its predecessor; prior artifacts are never
  edited or deleted.
- Execution systems pin immutable snapshots. Replay reads pinned
  ExecutionArtifact records, never live drafts and never regenerated
  prompts.
- Replay never silently upgrades. Re-running proofing under a newer rule
  set produces a new draft with a new proofing_rule_version; it does not
  overwrite or supersede the historical draft in place.
- Approval stays explicit. Nothing in the proofing layer marks a draft
  approved.

## 12. Scope Boundaries (Forbidden Behaviors)

The proofing substrate must never:

- perform live execution of any prompt,
- autonomously rewrite a prompt without a recorded, reviewable finding,
- spawn or act as an agent,
- call external tools, models, or APIs,
- mutate historical prompts, drafts, or artifacts,
- approve prompts or imply approval,
- read or modify downstream execution-system state.

Any proposal to relax these boundaries must first amend
docs/contracts/PRODUCT_CONTRACT.md.

## 13. Implementation Phases

Each phase is a separate, reviewable pass. Phases are ordered so that
governance primitives land before any rule logic. Each phase lists its
deliverable, acceptance criteria, and exact test requirements.

### Phase 1: Enums and Value Objects

Deliverable: ProofingSeverity, ProofingCategory, and ProofingFinding as
frozen value objects. Models only, no rule logic.

Acceptance criteria:

- ProofingSeverity has exactly error, warning, note.
- ProofingCategory has the categories listed in section 5.
- ProofingFinding is a frozen dataclass with the fields in section 4.2.
- All section 10 data model invariants hold.

Test requirements:

- construct each enum value and assert membership and count.
- construct a ProofingFinding and assert field values.
- assert ProofingFinding is frozen: attribute assignment raises.
- assert no mutable default fields exist on ProofingFinding.

### Phase 2: Deterministic Hashing and Identity

Deliverable: content_hash retained as text-only, plus a version_identity
helper combining content_hash, semantic_contract_version, and
proofing_rule_version.

Acceptance criteria:

- content_hash depends on text only; schema and rule version do not
  change it.
- version_identity changes when rule or schema version changes, with
  text held constant.
- both functions are deterministic and pure.

Test requirements:

- assert content_hash is stable across repeated calls.
- assert content_hash ignores schema and rule version.
- assert version_identity differs when proofing_rule_version differs.
- assert version_identity is stable for identical inputs.

### Phase 3: Enriched PromptDraft Model

Deliverable: the PromptDraft model with the fields in section 4.1.

Acceptance criteria:

- PromptDraft is a frozen dataclass; findings is a tuple.
- original_text is preserved; normalized_text is a separate field.
- a draft with no findings has normalized_text equal to original_text.
- content_hash on the draft is computed from normalized_text.

Test requirements:

- construct a PromptDraft and assert field values.
- assert PromptDraft is frozen and findings is an immutable tuple.
- assert original_text is never equal-by-identity to normalized_text
  unless content is identical.
- assert approvability derives from findings (error present => not
  approvable).

### Phase 4: Append-Only Governance Store Interface

Deliverable: an interface for storing drafts append-only. In-memory or
flat-file only. No database, no network.

Acceptance criteria:

- writing a draft never edits or deletes a prior draft.
- a revision is stored as a new entry referencing its predecessor.
- read order is deterministic.

Test requirements:

- store two drafts and assert both remain readable.
- assert a revision does not remove its predecessor.
- assert iteration order is stable across runs.

### Phase 5: Proofing Rule Engine

Deliverable: a pure, deterministic rule engine. One category at a time,
each rule emitting zero or more findings.

Acceptance criteria:

- rules are pure: same input yields same findings.
- rules emit findings only; they never mutate input or execute anything.
- findings are returned in deterministic order.
- each rule belongs to a versioned rule set.

Test requirements:

- per rule: an input that triggers it and an input that does not.
- assert finding order is deterministic for a fixed input.
- assert running the engine does not mutate the input intent.
- assert the rule set version is recorded on the produced findings.

### Phase 6: Approval Linkage

Deliverable: ApprovedPrompt referencing a specific draft version
identity. Approval input remains external and explicit.

Acceptance criteria:

- ApprovedPrompt references a draft by version_identity.
- approval_identity includes approval context per section 8.
- no code path approves a draft automatically.

Test requirements:

- construct an ApprovedPrompt from a draft and assert the reference.
- assert approval_identity differs from version_identity.
- assert a draft with an open ERROR cannot form an ApprovedPrompt.

### Phase 7: Execution Artifact Shape

Deliverable: the ExecutionArtifact shape as a description only.
Generation and execution remain owned by downstream systems.

Acceptance criteria:

- ExecutionArtifact is a frozen, immutable description.
- it references an ApprovedPrompt.
- prompt123 contains no code that executes the artifact.

Test requirements:

- construct an ExecutionArtifact and assert immutability.
- assert it references an ApprovedPrompt identity.
- assert no execution entry point exists in the package.

## 14. Phase Gates

Gates are mandatory. A phase may not begin until the prior gate passes.

- No rule engine (Phase 5) before the models and hash/identity work
  (Phases 1 to 3) pass their audits.
- No approval linkage (Phase 6) before a draft version_identity exists
  and is tested (Phase 2 and Phase 3).
- No execution artifact work (Phase 7) before ApprovedPrompt linkage
  exists (Phase 6).
- No LLM calls, model clients, or external API calls in any phase of
  this plan. Introducing them requires amending the product contract
  first.

## 15. Audit and Report Requirements

Every implementation phase must:

- write a phase report under docs/audits/, named for the phase, stating
  scope, findings, and a HOLD / WARNING / NOTE table and verdict;
- update docs/unified_diff.md with a dated change-log entry;
- run pytest, git diff --check, and the ASCII markdown check, and record
  the results in the phase report;
- keep all markdown ASCII-only.

A phase is not complete until its report is written and its validation
results are recorded.

## 16. Open Questions

- Where should drafts persist: flat files, or a simple append-only log?
  Deferred to Phase 4; must remain dependency-free.
- Should normalization stay record-only beyond v0, or become opt-in
  apply per rule? Current policy is record-only for v0 (section 9).
- How is span located in free text without a parser? May start as a line
  or character range only.
- Should rule sets be data-defined or code-defined? Affects how
  proofing_rule_version is computed.
- Who assigns draft_id, and is it derived or random? Must stay
  deterministic if derived.

## 17. Final Recommendation

Proceed with Phase 1 as the next implementation pass: enums and
value-object models only, with the tests listed under Phase 1. It is the
smallest governance-safe step, introduces no runtime behavior, and
unblocks the later phases without committing to rule logic. Each
subsequent phase is gated by section 14 and closed by a report under
section 15.
