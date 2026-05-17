# Implementation Plan: PromptDraft Proofing Substrate

Plan type: first implementation plan (plan-only, no runtime behavior)
Target: a governed PromptDraft proofing and linting substrate
Status: proposed
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
- read or mutate fin123 state
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
| findings | Ordered list of ProofingFinding records. |
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

## 7. Determinism Doctrine

Four distinct identities must not be conflated:

- content hash: deterministic hash of prompt text only. Equal content
  yields an equal content hash. It is not an identity for an artifact.
- version identity: content hash plus semantic_contract_version plus
  proofing_rule_version. Identifies a draft as produced under a specific
  schema and rule set. Equal content under a newer rule set is a
  distinct version identity.
- approval identity: identifies an ApprovedPrompt. Adds the approver and
  the approval act to the version identity. Approval is always explicit.
- execution artifact identity: identifies an ExecutionArtifact. Adds the
  execution-time snapshot context. Owned by the downstream execution
  system, not by prompt123.

All four must be computed deterministically. A new rule version or a new
approval produces a distinct artifact even when the content hash is
unchanged.

## 8. Replay and Governance Doctrine

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

## 9. Scope Boundaries (Forbidden Behaviors)

The proofing substrate must never:

- perform live execution of any prompt,
- autonomously rewrite a prompt without a recorded, reviewable finding,
- spawn or act as an agent,
- call external tools, models, or APIs,
- mutate historical prompts, drafts, or artifacts,
- approve prompts or imply approval,
- read or modify fin123 state.

Any proposal to relax these boundaries must first amend
docs/contracts/PRODUCT_CONTRACT.md.

## 10. Future Implementation Phases

Each phase is a separate, reviewable pass. Phases are ordered so that
governance primitives land before any rule logic.

- Phase 1: enums and value-object models (ProofingSeverity,
  ProofingCategory, ProofingFinding). Models only.
- Phase 2: deterministic hashing extended for version identity, kept
  distinct from the content hash.
- Phase 3: enriched PromptDraft model with the fields in section 4.1.
- Phase 4: append-only governance store interface (in-memory or file,
  no database, no network).
- Phase 5: proofing rule engine: pure, deterministic, one category at a
  time.
- Phase 6: approval linkage: ApprovedPrompt references a specific draft
  version identity. Approval input remains external and explicit.
- Phase 7: execution artifact shape, as a description only. Generation
  and execution remain owned by downstream systems.

Phases 5 onward should not begin until the audit of the prior phase
passes.

## 11. Open Questions

- Where should drafts persist: flat files, or a simple append-only log?
  Deferred to Phase 4; must remain dependency-free.
- Should normalization be opt-in per rule, or always recorded and never
  applied automatically? Leaning toward record-only, apply-never.
- How is span located in free text without a parser? May start as a line
  or character range only.
- Should rule sets be data-defined or code-defined? Affects how
  proofing_rule_version is computed.
- Who assigns draft_id, and is it derived or random? Must stay
  deterministic if derived.

## 12. Final Recommendation

Proceed with Phase 1 as the next implementation pass: enums and
value-object models only, with placeholder tests. It is the smallest
governance-safe step, introduces no runtime behavior, and unblocks the
later phases without committing to rule logic. Each subsequent phase
should be gated by its own contract audit.
