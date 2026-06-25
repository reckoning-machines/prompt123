# Implementation Plan: PromptDraft Proofing Substrate

Plan type: first implementation plan (plan-only, no runtime behavior)
Target: a governed proofing and optimization layer for AI prompts
Status: proposed, implementation-ready
Date: 2026-05-17
Governing contract: docs/contracts/PRODUCT_CONTRACT.md

This document is a plan. It defines no runtime behavior, no LLM calls,
no APIs, no execution logic, and no fin123 integration. Implementation
is deferred to later passes, each of which must defer to the product
contract.

## 1. Product Goal

Build the first proofing and optimization layer for AI prompts.

Users provide:

- a Question
- an optional Method

prompt123 analyzes that intent and produces:

- Findings
- Suggested Improvements
- a Suggested PromptDraft

The product helps domain experts improve the probability that a model
produces the author's intended result without requiring expertise in
prompt engineering.

prompt123 critiques, explains, and proposes.

It never approves.

It never executes.

It never silently rewrites user intent.

The intended product flow is:

```
Question
  + optional Method
  -> PromptIntent
  -> Analysis (internal)
  -> Observations (internal)
  -> Proofing
  -> Findings
  -> Suggestions
  -> Draft
  -> Downstream approval
```

prompt123 owns intent capture, analysis, proofing findings,
suggested improvements, and suggested PromptDraft artifacts. Downstream
systems own review, approval, execution snapshots, and execution.

## 2. Proofing Philosophy

prompt123 assumes:

- users know their domain,
- users do not necessarily know prompt engineering,
- model-result reliability can improve without changing user intent,
- unresolved ambiguity should be exposed rather than silently resolved.

prompt123 bridges the gap between domain expertise and effective AI
communication. Its job is to identify communication problems, explain
those problems, and propose improvements.

It does not replace the user's intent with its own. It preserves the
original text, explains every proposed change, and keeps every suggested
draft advisory until a downstream reviewer approves it.

## 3. Analysis

Analysis is distinct from proofing. Analysis observes what the user
wrote before the system decides whether anything is unclear, missing,
risky, or improvable.

Analysis answers questions such as:

- Is there a Question?
- Is there a Method?
- Are Question and Method mixed?
- Is the Method reusable?
- Is the Question complete enough to evaluate?
- Is the requested output identifiable?
- Are output format, constraints, inputs, or tools declared?

These are observations, not findings. A missing Method may be valid. A
Question-only prompt may be complete. Proofing turns analysis
observations into findings only when those observations matter for
prompt quality, determinism, or governance.

Separating analysis from proofing gives deterministic rules and future
LLM-assisted analysis the same conceptual boundary: first understand the
intent, then critique it.

Internal architecture analogy: prompt123 should behave like a compiler
for prompts, but should not market itself that way. `PromptIntent` is
source input, Analysis is parse and semantic analysis, Proofing
Findings are diagnostics, Suggested Improvements are repairs, and
Suggested PromptDraft is the reviewable output artifact. This analogy is
useful because it keeps analysis, diagnostics, and output generation as
separate responsibilities.

## 4. Prompt Quality

Prompt quality means the likelihood that a model will produce the
author's intended result from the author's stated intent. Prompt quality
improves when:

- ambiguity decreases,
- output expectations become clearer,
- constraints become explicit,
- hidden assumptions are surfaced,
- Question and Method responsibilities are easier to distinguish,
- reasoning instructions become easier to interpret,
- determinism increases,
- user intent remains preserved.

Optimization is the act of improving communication between human intent
and AI systems without changing the author's intended objective.
Optimization is advisory: it may produce suggested improvements or
suggested PromptDraft fragments, but it does not modify the original
PromptIntent.

## 5. Non-Goals

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
the original intent text is always preserved alongside any suggested or
normalized draft text, and every change is named in findings.

## 6. Ontology Impact

No new canonical nouns. The plan stays within the existing canonical
chain:

```
PromptIntent -> PromptDraft -> ApprovedPrompt -> ExecutionArtifact -> Audit
```

The product flow introduces user-facing outputs, not new canonical
ontology stages:

- `Findings` are structured proofing conclusions derived from analysis
  observations.
- `Suggested Improvements` are advisory remediation or optimization
  proposals attached to findings.
- `Suggested PromptDraft` is the reviewable PromptDraft proposal carried
  by the canonical chain.

These outputs remain subordinate to `PromptIntent` and `PromptDraft`.
They do not create approval authority and they do not execute.

Users interact with `PromptIntent`, Findings, Suggested Improvements,
and Suggested PromptDraft artifacts. Analysis and observations are
implementation artifacts that exist to improve proofing quality. They
are not part of the user-facing mental model.

## 7. Proposed Artifact Shapes

These are proposed shapes for a future pass. They are not implemented
here. All artifacts are immutable once created.

### 7.1 PromptIntent

| Field | Purpose |
|-------|---------|
| intent_id | Stable identifier for this intent artifact. |
| original_text | Verbatim user text, preserved unchanged. |
| question_text | Extracted or declared Question, if identifiable. |
| method_text | Extracted or declared optional Method, if identifiable. |
| author | User or system that captured the intent. |
| content_hash | Deterministic hash of original_text and declared metadata. |
| semantic_contract_version | Version of the artifact schema itself. |

Question and Method are conceptual components of PromptIntent. They are
not separate canonical artifacts.

### 7.2 AnalysisResult

| Field | Purpose |
|-------|---------|
| analysis_id | Stable identifier for this analysis result. |
| source_intent_hash | Content hash of the analyzed PromptIntent. |
| has_question | Whether a Question is identifiable. |
| has_method | Whether a Method is identifiable. |
| question_text | Observed Question text, if identifiable. |
| method_text | Observed Method text, if identifiable. |
| question_method_mixed | Whether Question and Method appear mixed. |
| method_reusable | Whether the Method appears reusable across Questions. |
| output_identifiable | Whether the requested output is identifiable. |
| declared_constraints | Observed constraints, if any. |
| declared_inputs | Observed inputs, if any. |
| declared_tools | Observed tools, if any. |
| observations | Ordered tuple of analysis observations. |
| semantic_contract_version | Version of the artifact schema itself. |
| analysis_rule_version | Version of the analysis rule set. |

AnalysisResult is an implementation artifact. It is not a canonical
ontology noun and not a user-facing object. Users interact with
PromptIntent, Findings, Suggested Improvements, and Suggested
PromptDraft artifacts. AnalysisResult exists to improve proofing quality
and output durability.

### 7.3 ProofingFinding

| Field | Purpose |
|-------|---------|
| finding_id | Stable identifier for this finding. |
| rule_id | Identifier of the rule or analyzer that triggered. |
| category | ProofingCategory enum value. |
| severity | ProofingSeverity enum value: error, warning, note. |
| message | Human-readable statement of the issue or opportunity. |
| explanation | Optional explanation of what was observed and why it matters. |
| suggested_improvement | Optional suggested improvement. |
| suggested_prompt_fragment | Optional suggested PromptDraft fragment. |
| confidence | Optional confidence value for advisory ranking. |
| span | Optional location within the original intent text. |

Every finding may optionally include an explanation, a suggested
improvement, a suggested PromptDraft fragment, and confidence. This makes
optimization part of the core product output rather than an implicit
side effect of linting.

Suggested Improvements are represented as optional fields on findings in
v0. Longer term, a separate SuggestedImprovement value object may age
better because one finding can have multiple valid improvements. For
example, an unspecified output schema may support JSON schema, Markdown
table, CSV, or bullet-list suggestions. That design is deferred until
the product needs multiple competing proposals per finding.

### 7.4 Suggested PromptDraft

| Field | Purpose |
|-------|---------|
| draft_id | Stable identifier for this draft artifact. |
| source_intent_hash | Content hash of the originating PromptIntent. |
| original_text | Verbatim intent text, preserved unchanged. |
| question_text | Question represented in the draft, if identifiable. |
| method_text | Optional Method represented in the draft, if identifiable. |
| suggested_text | Structurally suggested candidate prompt text. |
| findings | Ordered tuple of ProofingFinding records. |
| expected_output_schema | Declared output expectation, or null if absent. |
| allowed_inputs | Declared inputs the prompt may rely on. |
| allowed_tools | Declared tools the prompt may rely on. |
| content_hash | Deterministic hash of suggested_text. |
| version_identity | Deterministic identity for text, schema, and rule version. |
| semantic_contract_version | Version of the artifact schema itself. |
| proofing_rule_version | Version of the rule set that produced findings. |

A Suggested PromptDraft is advisory. It is never an approval and never
executable by prompt123.

### 7.5 Enums

- ProofingSeverity: error, warning, note.
- ProofingCategory: see section 8.

## 8. Proofing Categories

The proofing engine is a deterministic, pure interpretation of
AnalysisResult and declared metadata. Each rule emits zero or more
findings. No rule mutates state and no rule executes anything.

Categories are split between product findings that users understand and
technical findings that support governance and durability.

### 8.1 Product Findings

- question_unclear: the requested output is ambiguous or incomplete.
- method_unclear: the requested reasoning method is ambiguous,
  incomplete, or hard to follow.
- question_method_mixed: what should be produced and how reasoning
  should occur are mixed in a way that may confuse execution.
- missing_output_specification: the desired output shape, format, or
  success condition is missing.
- improvement_opportunity: the prompt could improve the probability of
  producing the author's intended result without changing intent.
- hidden_assumption: the prompt depends on unstated context, data,
  definitions, or user expectations.

### 8.2 Technical Findings

- mutable_reference: the prompt refers to mutable or undated sources.
- unsupported_pattern: the prompt uses a pattern the substrate does not
  support.
- hidden_tool: the prompt assumes an undeclared tool or runtime
  capability.
- missing_schema: no explicit expected output schema is declared where
  one is needed.
- ambiguous_metric: the prompt asks for a metric or judgment without
  defining the calculation or output basis.
- open_ended_request: the prompt is unbounded and lacks a stopping
  condition.

Each rule has a stable rule_id and belongs to a versioned rule set
(proofing_rule_version). Adding or changing rules bumps that version.

## 9. Explainability and Optimization Output

Findings are the primary output of prompt123. A finding records:

- what was observed in the intent,
- why it matters,
- how it may affect the probability that the model produces the
  author's intended result,
- which rule_id and rule version triggered it,
- any suggested improvement,
- any suggested PromptDraft fragment,
- confidence when the analyzer can support it.

Suggested Improvements are advisory and may include:

- clearer wording,
- a stronger output specification,
- an explicit schema,
- explicit constraints,
- a separated Question and Method,
- a narrower or dated reference,
- a suggested PromptDraft fragment.

Where the substrate proposes draft text, the proposal is itemized in the
findings so a reviewer can see each change and its reason. There is no
transformation without a recorded explanation. This satisfies the
contract rule that proofing must be explainable.

## 10. Error and Finding Taxonomy

Severity is governance-meaningful, not cosmetic. Downstream systems may
read severity to decide review handling, but prompt123 does not approve
or reject prompts.

- ERROR: the suggested draft contains a governance defect that downstream
  approval should not pass without remediation. Examples include missing
  schema, hidden execution assumption, or unsupported pattern.
- WARNING: the reviewer should explicitly acknowledge the finding before
  downstream approval. A warning does not block approval by itself, but
  approval must not proceed silently past it.
- NOTE: informational or optimization-oriented. It requires no
  acknowledgement and does not affect approvability by itself.

Rules:

- Severity is assigned by the rule, deterministically, from the same
  input.
- prompt123 records severity; it never clears or downgrades a finding.
- Remediation produces a new suggested draft, not an edit of the
  finding.
- A downstream approvability assessment may be derived from findings,
  but prompt123 stores no mutable approval flag.

## 11. Determinism, Version, and Replay Invariants

Governance supports the product; it does not define the product. The
proofing layer must still preserve deterministic identity and replay.

Four distinct identities must not be conflated:

- content_hash: deterministic hash of prompt text only. Equal text
  yields an equal content_hash. It is text-only and is not an identity
  for an artifact.
- version_identity: content_hash plus semantic_contract_version plus
  proofing_rule_version. Identifies a suggested draft as produced under
  a specific schema and rule set. Equal text under a newer rule set is a
  distinct version_identity.
- approval_identity: version_identity plus downstream approval context.
  It belongs to an ApprovedPrompt. Approval is always explicit and
  downstream.
- execution_artifact_identity: the identity of an ExecutionArtifact,
  adding execution-time snapshot context. It belongs to the downstream
  execution system and is out of scope for prompt123 implementation in
  this plan.

Invariants:

- All identities prompt123 owns are computed deterministically from
  their inputs.
- content_hash never includes schema or rule version; those belong to
  version_identity.
- A new rule version produces a distinct suggested draft artifact even
  when content_hash is unchanged.
- Identity inputs are ordered deterministically before hashing so the
  same logical artifact always yields the same identity.
- Re-running proofing under a newer rule set produces a new draft with a
  new proofing_rule_version; it does not overwrite historical output.

## 12. Normalization Policy

- original_text is always preserved, verbatim.
- suggested_text is never presented as the original and never overwrites
  original_text.
- Every suggested normalization is attached to a finding describing what
  changed and why.
- For v0, normalization is record-only: the substrate describes the
  normalization it would apply but does not apply it automatically.
- A suggested draft with no findings has suggested_text equal to
  original_text.

## 13. Data Model Invariants

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

## 14. Integration Boundaries

Approval linkage and ExecutionArtifact shapes remain part of the
canonical ontology, but they are integration work. They are not the core
product experience of this plan.

prompt123 may expose identities and immutable artifacts that downstream
systems can later approve or execute. prompt123 must not:

- create an ApprovedPrompt automatically,
- imply that a Suggested PromptDraft is approved,
- generate an execution snapshot,
- execute a prompt,
- read or modify downstream execution-system state.

Any proposal to relax these boundaries must first amend
docs/contracts/PRODUCT_CONTRACT.md.

## 15. Implementation Phases

Each phase is a separate, reviewable pass. Phases are ordered around
user-facing product value first, with governance and durability
introduced as supporting infrastructure before integration work.

### Phase 1: Findings Model

Deliverable: ProofingSeverity, ProofingCategory, and ProofingFinding as
frozen value objects. Models only, no rule logic.

Acceptance criteria:

- ProofingSeverity has exactly error, warning, note.
- ProofingCategory has the categories listed in section 8.
- ProofingFinding is a frozen dataclass with the fields in section 7.3.
- Optional explanation, suggested_improvement,
  suggested_prompt_fragment, and confidence fields are represented.
- All section 13 data model invariants hold.

Test requirements:

- construct each enum value and assert membership and count.
- construct a ProofingFinding with and without optional improvement
  fields.
- assert ProofingFinding is frozen: attribute assignment raises.
- assert no mutable default fields exist on ProofingFinding.

### Phase 2: Analysis

Deliverable: PromptIntent support for preserving original text and a
AnalysisResult that records observations about Question, optional
Method, output, constraints, inputs, and tools.

Acceptance criteria:

- original_text is preserved unchanged.
- AnalysisResult records whether a Question is identifiable.
- AnalysisResult records whether a Method is identifiable.
- Method may be absent without making the intent invalid or producing a
  finding by itself.
- mixed Question / Method responsibilities are recorded as observations
  before they become findings.
- requested output identifiability is recorded as an observation.
- no analysis rewrites original_text.

Test requirements:

- assert a Question-only prompt produces a valid PromptIntent.
- assert a prompt with Question and Method produces deterministic
  analysis observations for both components.
- assert mixed Question / Method text is recorded as an observation.
- assert missing Method does not automatically emit a finding.
- assert requested output identifiability is recorded.
- assert original_text remains byte-for-byte unchanged.

### Phase 3: Deterministic Proofing Engine

Deliverable: a pure, deterministic proofing engine that emits findings
from AnalysisResult. One category at a time, with product findings
first.

Acceptance criteria:

- rules are pure: same input yields same findings.
- rules emit findings only; they never mutate input or execute anything.
- rules consume AnalysisResult observations rather than reparsing intent
  text from scratch.
- product finding categories are implemented before technical finding
  categories unless a technical category is required to support a product
  finding.
- findings are returned in deterministic order.
- each rule belongs to a versioned rule set.

Test requirements:

- per rule: an input that triggers it and an input that does not.
- assert finding order is deterministic for a fixed input.
- assert running the engine does not mutate the input AnalysisResult.
- assert the rule set version is recorded on produced findings.

### Phase 4: Suggested Improvements

Deliverable: advisory suggested improvements attached to findings.

Acceptance criteria:

- a finding may include a suggested_improvement.
- suggested improvements preserve user intent.
- suggested improvements explain why the change improves communication
  between the author's intent and AI systems.
- improvement opportunities can be emitted without producing a full
  Suggested PromptDraft.
- suggestions are deterministic for deterministic rules.

Test requirements:

- assert missing output specification can produce a suggested
  improvement.
- assert improvement_opportunity can produce an advisory improvement.
- assert suggested improvements do not mutate PromptIntent.
- assert repeated proofing produces the same suggestions for the same
  input and rule version.

### Phase 5: Suggested PromptDraft Generation

Deliverable: Suggested PromptDraft artifact that carries original text,
suggested text, findings, and proofing provenance.

Acceptance criteria:

- Suggested PromptDraft is a frozen dataclass; findings is a tuple.
- original_text is preserved; suggested_text is separate.
- suggested_text is justified by findings and suggested improvements.
- a draft with no findings has suggested_text equal to original_text.
- the artifact is advisory and has no approval or execution behavior.

Test requirements:

- construct a Suggested PromptDraft and assert field values.
- assert Suggested PromptDraft is frozen and findings is an immutable
  tuple.
- assert original_text is never overwritten by suggested_text.
- assert suggested draft generation has no execution entry point.

### Phase 6: Artifact Identity and Replay

Deliverable: deterministic content_hash, version_identity, append-only
storage interface, and replay invariants for proofing outputs.

Acceptance criteria:

- content_hash depends on text only; schema and rule version do not
  change it.
- version_identity changes when rule or schema version changes, with
  text held constant.
- writing a suggested draft never edits or deletes a prior draft.
- a revision is stored as a new entry referencing its predecessor.
- read order is deterministic.

Test requirements:

- assert content_hash is stable across repeated calls.
- assert content_hash ignores schema and rule version.
- assert version_identity differs when proofing_rule_version differs.
- store two suggested drafts and assert both remain readable.
- assert a revision does not remove its predecessor.
- assert iteration order is stable across runs.

### Phase 7: Optional LLM-Assisted Analysis and Proofing

Deliverable: an optional LLM-assisted layer that proposes analysis
observations, findings, suggested improvements, and suggested
PromptDraft fragments. It is additive to, never a replacement for, the
deterministic analysis and proofing engine.

Acceptance criteria:

- all LLM outputs are persisted as replayable artifacts.
- all generated analysis observations are attributable to the LLM that
  produced them.
- all generated findings are attributable to the LLM that produced them.
- no generated text mutates original_text.
- no approval authority exists in the LLM layer.
- LLM-generated suggestions are record-only until explicitly reviewed.
- replay reads persisted artifacts and never re-queries a live model.

Test requirements:

- replay determinism tests: stored artifacts replay identically without
  re-querying a model.
- provenance tests: analysis prompt, proofing prompt, model identity,
  and config are persisted and retrievable.
- attribution tests: every LLM-generated finding records its LLM origin.
- no-silent-mutation tests: original_text is unchanged by the LLM layer.
- ambiguity-preservation tests: unresolved ambiguity remains recorded as
  findings and is never silently resolved by the LLM layer.

## 16. Future LLM-Assisted Analysis and Proofing

This section documents direction only. It positions LLM-assisted
analysis and proofing after deterministic analysis, proofing,
suggested improvements, suggested PromptDraft generation, and artifact
replay are implemented.

LLM assistance may perform:

- Analysis
- Proofing
- Suggestion generation

All outputs remain advisory. LLM assistance does not approve, execute, or
silently rewrite user intent.

## 17. Phase Gates

Gates are mandatory. A phase may not begin until the prior gate passes.

- No Analysis (Phase 2) before the findings model (Phase 1)
  passes its audit.
- No deterministic proofing engine (Phase 3) before AnalysisResult can
  preserve original text provenance and record Question / Method
  observations (Phase 2).
- No Suggested Improvements (Phase 4) before deterministic findings
  exist (Phase 3).
- No Suggested PromptDraft generation (Phase 5) before suggested
  improvements exist (Phase 4).
- No artifact identity or replay work (Phase 6) before Suggested
  PromptDraft shape exists (Phase 5).
- No LLM-assisted analysis or proofing (Phase 7) before deterministic
  analysis, deterministic proofing, suggested improvements, Suggested
  PromptDraft generation, and replay have passed their audits.
- Phases 1 to 6 contain no LLM calls, model clients, or external API
  calls. Phase 7 is the only phase that may involve an LLM, and only
  under the Future LLM-Assisted Analysis and Proofing doctrine in this
  plan and the LLM-assisted proofing doctrine in the product contract.
  Introducing LLM use earlier, or beyond those doctrines,
  requires amending the contract first.

## 18. Audit and Report Requirements

Every implementation phase must:

- write a phase report under docs/audits/, named for the phase, stating
  scope, findings, and a HOLD / WARNING / NOTE table and verdict;
- update docs/unified_diff.md with a dated change-log entry;
- run pytest, git diff --check, and the ASCII markdown check, and record
  the results in the phase report;
- keep all markdown ASCII-only.

A phase is not complete until its report is written and its validation
results are recorded.

## 19. Open Questions

- Should confidence be constrained to a fixed enum, a decimal score, or
  omitted for deterministic rules that cannot justify it?
- Should suggested PromptDraft fragments be stored only on findings, or
  also gathered into a separate ordered suggestions tuple on the draft?
- When should SuggestedImprovement become a separate value object rather
  than optional fields on ProofingFinding?
- Which analysis observations should be versioned independently
  from proofing rules?
- Where should proofing outputs persist: flat files, or a simple
  append-only log? Must remain dependency-free for v0.
- Should normalization stay record-only beyond v0, or become opt-in
  apply per rule? Current policy is record-only for v0.
- How is span located in free text without a parser? May start as a line
  or character range only.
- Should rule sets be data-defined or code-defined? Affects how
  proofing_rule_version is computed.
- Who assigns draft_id, and is it derived or random? Must stay
  deterministic if derived.

## 20. Final Recommendation

Proceed with Phase 1 as the next implementation pass: the findings model
only, including product-facing categories and optional improvement
fields. It is the smallest product-aligned, governance-safe step:
findings are the primary output, and every later phase depends on
findings before Analysis can translate intent into observations,
proofing can translate observations into findings, or later phases can
suggest improvements, generate PromptDrafts, or support replay.
