# Implementation Plan: PromptDraft Proofing Substrate (v2)

Plan type: revised implementation plan
Author: Drew Goldman
Source plan: docs/plans/prompt_draft_proofing_substrate_plan.md
Governing contract: docs/contracts/PRODUCT_CONTRACT.md
Date: 2026-06-03
Status: proposed

This plan revises the source plan. It preserves all governance
doctrine, artifact shapes, and phase structure from the original.
Key changes: the LLM is the primary proofing engine (not a future
optional layer), proofing prompts are domain-scoped governed
artifacts, Phase 4 includes terminal output, Phase 5 is the
domain-aware LLM proofer, and Phase 8 is full LLM rewrite mode
as a first-class deliverable.

## 1. Product Goal

Build the first governed proofing layer that turns a PromptIntent
into an explainable PromptDraft. The layer inspects raw analyst
intent, records structured findings, and produces a draft artifact
that a human or system can review. It never decides; it only
describes.

prompt123 exists to make LLM prompts as deterministic as possible
without erasing user intent. Users may express vague, incomplete,
or informal intent; the proofing layer transforms that intent into
a reviewable governed PromptDraft by identifying ambiguity, missing
schema, hidden assumptions, nondeterministic wording, and unsafe
external dependencies. The goal is not cleverness; it is
determinism, explainability, reviewability, and replay safety.

For the product to be practically usable, the LLM must handle both
full flagging and full rewriting. Deterministic rules alone cannot
cover the full space of vague or domain-specific intent. The LLM
is the primary proofing engine; governance primitives exist to
constrain and record what it does. The proofing prompt given to
the LLM is scoped to the declared domain_profile of the input.

The proofing layer has two components that run in sequence:

1. Deterministic pre-filter: runs first on every input. Handles
   basic pattern-matchable checks -- profanity, disallowed content,
   formatting violations -- that do not require language
   understanding. Fast, no model call. Cannot be disabled.
2. LLM proofer: runs after the pre-filter. Primary engine for
   everything else: ambiguity, missing schema, hidden assumptions,
   domain-specific issues, and intent that requires language
   understanding. Scoped to the declared domain_profile.

Two domain profiles are supported for now: generic and fin123.
All other domains are out of scope until fin123 is complete and
audited. generic is the fallback for intents that do not declare
a domain. fin123 extends generic with finance-specific categories.

Doctrine for this layer:

- User intent may be vague.
- PromptDrafts must make ambiguity explicit.
- prompt123 may propose clarifications or normalized draft language.
- prompt123 must preserve the original intent unchanged.
- prompt123 must never silently decide what the user meant.
- If intent remains ambiguous, the draft carries findings rather
  than inventing certainty.
- Approval remains explicit and downstream; execution remains
  downstream.

Success criterion: a PromptDraft is successful when it makes the
user's intent more deterministic and reviewable while preserving
the original intent and explicitly surfacing unresolved ambiguity.

The intended flow this plan works toward:

```
PromptIntent
  -> deterministic pre-filter (profanity, patterns, formatting)
  -> LLM proofer (scoped to domain_profile)
  -> PromptDraft (findings + suggestions)
  -> terminal display
  -> human or system review
  -> ApprovedPrompt
  -> ExecutionArtifact
  -> downstream execution system
```

prompt123 owns the first four stages only. Review, approval, and
everything after are owned by downstream systems.

## 2. Non-Goals

The proofing substrate does not, and this plan does not authorize
it to:

- execute prompts or call any model outside the governed LLM layer
- approve prompts, automatically or by inference
- silently rewrite a prompt and present the result as the original
- act as an agent, workflow runtime, or orchestrator
- call external APIs or tools outside the governed LLM layer
- read or mutate downstream execution-system state
- generate hidden behavior or side effects
- maintain conversational memory

Normalization is explicit and recorded. It is not silent rewriting:
the original intent text is always preserved alongside the
normalized text, and every change is named in the findings.

## 3. Ontology Impact

No new canonical nouns. The plan stays within the existing chain:

```
PromptIntent -> PromptDraft -> ApprovedPrompt -> ExecutionArtifact
-> Audit
```

The substrate enriches PromptDraft so it can carry proofing
findings, normalized text, domain profile, and the versioning
metadata needed for replay. It adds supporting value objects (a
finding record, severity and category enums) that are not ontology
nouns and remain subordinate to it.

## 4. Proposed Artifact Shapes

These shapes are the implementation target across Phases 1-8.
This section defines them; the phases build and test them.
All artifacts are immutable once created.

### 4.1 PromptDraft (enriched)

| Field                     | Purpose |
|---------------------------|---------|
| draft_id                  | Stable identifier for this draft artifact. |
| source_intent_hash        | Content hash of the originating PromptIntent. |
| original_text             | Verbatim intent text, preserved unchanged. |
| normalized_text           | Structurally normalized candidate text. |
| findings                  | Ordered tuple of ProofingFinding records. |
| domain_profile            | The domain profile active when this draft was produced. |
| expected_output_schema    | Declared output expectation, or null if absent. |
| allowed_inputs            | Declared inputs the prompt may rely on. |
| allowed_tools             | Declared tools the prompt may rely on. |
| content_hash              | Deterministic hash of normalized_text. |
| semantic_contract_version | Version of the artifact schema itself. |
| proofing_rule_version     | Version of the rule set that produced findings. |
| proofing_prompt_version   | Version of the proofing prompt used by the LLM.
                             None for drafts produced without the LLM layer. |
| provider                  | LLM provider identity (e.g., "anthropic"). None for
                             deterministic-only drafts. |
| model_id                  | Model identifier used for the LLM proofer run. None
                             for deterministic-only drafts. |
| model_version             | Model version string. None for deterministic-only
                             drafts. |
| config_hash               | Deterministic hash of the proofing run configuration
                             (temperature, sampling). None for deterministic-only
                             drafts. |

A draft is advisory. It is never an approval and never executable.

### 4.2 ProofingFinding

| Field       | Purpose |
|-------------|---------|
| rule_id     | Identifier of the rule that triggered. |
| category    | ProofingCategory enum value. |
| severity    | ProofingSeverity enum value (error, warning, note). |
| message     | Human-readable description of the issue. |
| explanation | What was observed, why it matters, what rule applies. |
| span        | Optional location within the prompt text. |
| source      | Whether this finding came from a deterministic check
               or the LLM layer (ProofingSource enum). |

### 4.3 Enums

- ProofingSeverity: error, warning, note.
- ProofingCategory: see rule categories in section 5.
- ProofingSource: deterministic, llm.

## 5. Proofing Rule Categories

These categories define what the proofing layer flags. They apply
whether a finding is produced by the LLM or a deterministic check.
Each finding has a stable rule_id belonging to a versioned rule set
(proofing_rule_version). Adding or changing rules bumps that version.

- structure: unnormalized or unstructured prompt layout.
- ambiguity: ambiguous or unbounded output expectations.
- open_ended: unsupported open-ended instructions with no stopping
  condition.
- missing_schema: no explicit expected output schema.
- hidden_data: hidden assumptions about external or live data.
- hidden_tool: hidden tool or runtime assumptions not declared.
- unsupported_pattern: prompt patterns the substrate does not
  support.
- mutable_reference: unsafe references to mutable or undated
  sources.
- nondeterministic_wording: wording that invites nondeterministic
  output.
- vague_intent: user intent is underspecified or informal in a way
  that affects deterministic execution.
- missing_constraints: prompt lacks required bounds, definitions,
  assumptions, or stopping conditions.
- ambiguous_metric: prompt asks for a metric or judgment without
  defining the calculation or output basis.
- disallowed_content: input matches a disallowed pattern or
  profanity rule. Used exclusively by the deterministic pre-filter.
- system_error: a technical failure in the proofing layer that
  prevented normal processing. Used when the finding describes an
  infrastructure issue rather than a problem with the user intent
  (e.g., llm_parse_failure).

### 5.1 fin123 Domain Categories

These categories extend the generic list above. They apply only
when domain_profile is fin123. The fin123 proofing prompt instructs
the LLM to watch for these in addition to all generic categories.

- time_reference_unanchored: references to "current," "latest,"
  "recent," or "today's" financial data without a specific date or
  named data snapshot. Financial data changes constantly; an
  unanchored time reference makes the prompt nondeterministic.
- calculation_basis_undefined: a financial calculation is requested
  without specifying the methodology. Examples: returns without
  specifying time-weighted vs money-weighted, NPV or IRR without a
  discount rate, ratios without defining the numerator and
  denominator inputs.
- currency_unspecified: monetary values or comparisons that do not
  name an explicit currency. Applies to inputs, outputs, and any
  thresholds in the prompt.
- benchmark_undefined: performance comparisons such as "beat the
  market" or "outperformed peers" without naming a specific
  benchmark index or peer group.
- fiscal_period_ambiguous: references to "last quarter," "annual,"
  "YTD," or similar periods without a fiscal year definition or
  explicit start and end dates.
- data_source_unspecified: references to "market data," "financial
  statements," "prices," or similar without naming a source,
  provider, or data vintage.
- regulatory_scope_undefined: prompts that touch investment
  recommendations, trading signals, or other regulated activities
  without explicit scope limitations or disclaimers.

## 6. Explainability

Every finding must be explainable. A finding records:

- what was observed in the intent,
- why it matters under the governance doctrine,
- which rule_id and rule version triggered it,
- whether it was produced by the LLM or a deterministic check.

Where the substrate normalizes text, the normalization is itemized
in the findings so a reviewer can see each change and its reason.
There is no transformation without a recorded explanation. This
satisfies the contract rule that proofing must be explainable.

## 7. Error and Finding Taxonomy

Severity is governance-meaningful, not cosmetic. Downstream
systems read severity to decide review handling.

- ERROR: the draft cannot be approved downstream without
  remediation. An error marks a governance defect: a missing
  schema, a hidden execution assumption, or an unsupported
  pattern. A draft with any ERROR finding is not approvable as-is.
- WARNING: the reviewer must explicitly acknowledge the finding
  before approval. A warning does not block approval, but approval
  must not proceed silently past it.
- NOTE: informational only. It requires no acknowledgement and
  does not affect approvability.

Rules:

- Severity is assigned by the rule or proofing prompt,
  deterministically, from the same input.
- prompt123 records severity; it never clears or downgrades a
  finding.
- Remediation produces a new draft (append-only), not an edit of
  the finding.
- A draft's approvability is derived from its findings, never
  stored as a separate mutable flag. Derivation rule: a draft is
  approvable if and only if it has no findings with severity ERROR.
  WARNINGs do not block approval but must be explicitly acknowledged.
  NOTEs have no effect on approvability.

## 8. Determinism, Version, and Hash Invariants

Four distinct identities must not be conflated:

- content_hash: deterministic hash of normalized_text only. Equal
  normalized_text yields an equal content_hash. It is text-only
  and is not an identity for an artifact.
- version_identity: content_hash plus semantic_contract_version
  plus proofing_rule_version. Identifies a draft as produced under
  a specific schema and rule set. Equal text under a newer rule
  set is a distinct version_identity.
- approval_identity: version_identity plus the approval context
  (approver and the explicit approval act). Identifies an
  ApprovedPrompt. Approval is always explicit.
- execution_artifact_identity: the identity of an
  ExecutionArtifact, adding the execution-time snapshot context.
  It belongs to the downstream execution system and is out of
  scope for prompt123.

Invariants:

- All identities prompt123 owns are computed deterministically
  from their inputs.
- content_hash never includes schema or rule version; those belong
  to version_identity.
- A new rule version or a new approval produces a distinct artifact
  even when content_hash is unchanged.
- Identity inputs are ordered deterministically before hashing so
  the same logical artifact always yields the same identity.

## 9. Normalization Policy

- original_text is always preserved, verbatim, on the draft.
- normalized_text is never presented as the original and never
  overwrites original_text.
- Every normalization produces a finding describing what changed
  and why.
- For v0, normalization is record-only: the substrate describes
  the normalization it would apply but does not apply it
  automatically. Applying a normalization is a later, separately
  gated decision.
- A draft with no findings has normalized_text equal to
  original_text.

## 10. Data Model Invariants

All artifact and value-object types must satisfy:

- frozen dataclasses: every type is @dataclass(frozen=True). No
  field is reassigned after construction.
- no mutable default fields: no list, dict, or set defaults.
  Collections are tuples. Defaults are immutable or absent.
- deterministic ordering: findings and any other collections are
  stored in a defined, stable order. The same inputs always yield
  the same order. Findings are ordered by: position in source text
  (ascending), then severity (error before warning before note),
  then rule_id (lexicographic). Ties are broken by rule_id.
- no silent mutation: there are no in-place setters. A change is
  a new artifact that references its predecessor.
- no execution behavior: models carry data and pure derived
  properties only. No model performs I/O, network calls, or prompt
  execution.

## 11. Replay and Governance Doctrine

- Proofed drafts are replayable artifacts. A PromptDraft records
  the rule version, schema version, and proofing prompt version
  used, so it can be re-read exactly as it was produced.
- Drafts and downstream artifacts are append-only. A revision is
  a new artifact that references its predecessor; prior artifacts
  are never edited or deleted.
- Execution systems pin immutable snapshots. Replay reads pinned
  ExecutionArtifact records, never live drafts and never
  regenerated prompts.
- Replay never silently upgrades. Re-running proofing under a
  newer rule set or proofing prompt produces a new draft with new
  version fields; it does not overwrite or supersede the
  historical draft in place.
- Replay reads pinned proofing prompt artifacts and never
  re-queries a live model.
- Approval stays explicit. Nothing in the proofing layer marks a
  draft approved.

## 12. Scope Boundaries (Forbidden Behaviors)

The proofing substrate must never:

- perform live execution of any prompt,
- autonomously rewrite a prompt without a recorded, reviewable
  finding,
- spawn or act as an agent,
- call external tools, models, or APIs outside the governed LLM
  layer,
- mutate historical prompts, drafts, or artifacts,
- approve prompts or imply approval,
- read or modify downstream execution-system state.

Any proposal to relax these boundaries must first amend
docs/contracts/PRODUCT_CONTRACT.md.

## 13. Implementation Phases

Each phase is a separate, reviewable pass. Phases are ordered so
that governance primitives land before any proofing logic. Each
phase lists its deliverable, acceptance criteria, and exact test
requirements.

### Phase 1: Enums and Value Objects

Deliverable: ProofingSeverity, ProofingCategory, ProofingSource,
and ProofingFinding as frozen value objects. Models only, no
proofing logic.

Acceptance criteria:

- ProofingSeverity has exactly error, warning, note.
- ProofingCategory has all categories from sections 5 and 5.1
  (generic and fin123 categories together in one enum).
- ProofingSource has exactly deterministic, llm.
- ProofingFinding is a frozen dataclass with the fields in
  section 4.2.
- All section 10 data model invariants hold.

Test requirements:

- construct each enum value and assert membership and count.
- construct a ProofingFinding and assert field values.
- assert ProofingFinding is frozen: attribute assignment raises.
- assert no mutable default fields exist on ProofingFinding.

### Phase 2: Deterministic Hashing and Identity

Deliverable: content_hash retained as text-only, plus a
version_identity helper combining content_hash,
semantic_contract_version, and proofing_rule_version.

Acceptance criteria:

- content_hash depends on normalized_text only; schema and rule
  version do not change it.
- version_identity changes when rule or schema version changes,
  with text held constant.
- both functions are deterministic and pure.

Test requirements:

- assert content_hash is stable across repeated calls.
- assert content_hash ignores schema and rule version.
- assert version_identity differs when proofing_rule_version
  differs.
- assert version_identity is stable for identical inputs.

### Phase 3: Enriched PromptDraft Model

Deliverable: the PromptDraft model with the fields in section 4.1,
including domain_profile and proofing_prompt_version.

Acceptance criteria:

- draft_id is a randomly assigned UUID generated once at
  construction. It is not derived from content and is unique per
  draft instance.
- PromptDraft is a frozen dataclass; findings is a tuple.
- original_text is preserved; normalized_text is a separate field.
- domain_profile is a required field.
- proofing_prompt_version is optional: None for drafts produced
  without the LLM layer, a version string for LLM-produced drafts.
- a draft with no findings has normalized_text equal to
  original_text.
- content_hash on the draft is computed from normalized_text.

Test requirements:

- construct a PromptDraft and assert field values including
  domain_profile, proofing_prompt_version, provider, model_id,
  model_version, and config_hash.
- assert PromptDraft is frozen and findings is an immutable tuple.
- assert original_text is never equal-by-identity to
  normalized_text unless content is identical.
- assert approvability derives from findings (error present =>
  not approvable).
- assert provider, model_id, model_version, and config_hash accept
  None (for deterministic-only draft construction).

### Phase 4: Governance Store and Terminal Output

Deliverable: an append-only governance store (in-memory or flat
file) and terminal output that renders findings and suggestions
in an agreed format. Proofing strategies do not matter here --
placeholder findings are acceptable. The goal of this phase is to
establish how output looks before any proofing logic lands.

Acceptance criteria:

- proofing_prompts/ directory exists with the structure in
  section 14: generic/v1.txt as a non-empty placeholder and
  manifest.json mapping generic to v1.
- pre_filter_rules/ directory exists with profanity.txt,
  disallowed.txt, and formatting.json as minimal initial rule
  files (no proofing logic yet; these are the governed artifacts
  Phase 5 will load).
- writing a draft never edits or deletes a prior draft.
- a revision is stored as a new entry referencing its predecessor.
- read order is deterministic.
- terminal output displays a finding: rule_id, severity, message.
- terminal output displays a suggestion: what was observed, what
  is proposed.
- nothing is applied automatically; output is display only.

Test requirements:

- assert proofing_prompts/manifest.json loads and resolves generic
  to a readable file.
- assert pre_filter_rules/ contains profanity.txt, disallowed.txt,
  and formatting.json.
- store two drafts and assert both remain readable.
- assert a revision does not remove its predecessor.
- assert iteration order is stable across runs.
- assert terminal output renders a finding correctly.

### Phase 5: Proofing Engine (Pre-Filter + LLM Proofer)

Deliverable: the full proofing engine -- deterministic pre-filter
followed by the domain-aware LLM proofer. Both run on every input
in sequence. Output is structured findings and suggestions rendered
through the Phase 4 terminal format.

The pre-filter runs first. It applies basic deterministic checks
(profanity, disallowed content, formatting) and emits findings with
ProofingSource.deterministic. It cannot be disabled.

The LLM proofer runs after. The input declares a domain_profile;
the engine selects the matching proofing prompt and runs it. Output
is parsed into ProofingFinding records with ProofingSource.llm.

Acceptance criteria:

- pre-filter runs before any LLM call on every input.
- pre-filter findings carry ProofingSource.deterministic.
- domain_profile routes to the correct proofing prompt.
- an unknown or missing domain_profile raises a validation error
  before any LLM call is made.
- LLM output is parsed into ProofingFinding records.
- if LLM output cannot be parsed, the draft carries a single ERROR
  finding with rule_id llm_parse_failure and category system_error
  rather than raising an exception. The draft is still stored and
  reviewable.
- findings from both components render through the terminal format
  from Phase 4.
- original_text is never modified.
- proofing_prompt_version is recorded on every produced draft.
- provider, model_id, model_version, and config_hash are recorded
  on every LLM-assisted draft; these fields are None for
  deterministic-only drafts.

Test requirements:

- assert pre-filter runs before the LLM call.
- assert pre-filter findings carry ProofingSource.deterministic.
- assert a known domain_profile loads the expected proofing prompt.
- assert an unknown domain_profile raises a validation error before
  any LLM call.
- assert LLM output is parsed into valid ProofingFinding records.
- assert malformed LLM output produces an llm_parse_failure ERROR
  finding rather than an exception.
- assert original_text is unchanged after proofing.
- assert proofing_prompt_version is present on the output draft.
- assert provider, model_id, model_version, and config_hash are
  present on an LLM-produced draft.
- assert these four fields are None on a deterministic-only draft.

### Phase 6: Approval Linkage

Deliverable: ApprovedPrompt referencing a specific draft
version_identity. Approval input remains external and explicit.

Acceptance criteria:

- ApprovedPrompt references a draft by version_identity.
- approval_identity includes approval context per section 8.
- no code path approves a draft automatically.

Test requirements:

- construct an ApprovedPrompt from a draft and assert the
  reference.
- assert approval_identity differs from version_identity.
- assert a draft with any ERROR finding cannot form an ApprovedPrompt.

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

### Phase 8: Full LLM Rewrite Mode

Deliverable: explicit opt-in mode where the LLM handles complete
flagging and rewriting, not just proposals. This is the target
end state for practical usability -- deterministic rules alone
cannot cover the full space of domain-specific or vague intent.

Acceptance criteria:

- full rewrite mode must be explicitly invoked; never the default.
- every rewrite is named in a finding; nothing is silent.
- original_text is unchanged.
- a rewrite produces a new PromptDraft; approval chain unchanged.
- replay reads pinned artifacts and never re-queries the model.
- every LLM-produced draft records the proofing prompt version and
  model identity that produced it. Individual findings record
  ProofingSource.llm but do not duplicate draft-level metadata.

Test requirements:

- assert full rewrite mode is off by default.
- assert original_text is unchanged after a full rewrite run.
- assert every rewrite is accompanied by a finding.
- replay determinism: stored artifacts replay without re-querying.
- attribution: every LLM-produced draft records proofing_prompt_version
  and model identity via the draft fields (not individual findings).
  Every finding records ProofingSource.llm to identify it as
  LLM-produced.

## 14. Proofing Prompt Governance

Proofing prompts are governed artifacts. They instruct the LLM
and are the core mechanism of the product -- not config strings.

- Each proofing prompt is versioned and immutable.
- Proofing prompt version is recorded on every LLM-assisted draft.
- Changing a proofing prompt produces a new version, never an
  overwrite.
- Each domain_profile has its own proofing prompt.
- Proofing prompts must instruct the LLM to produce structured
  output conforming to the schema in the LLM Output Schema section.
  Phase 5 prompts produce findings only. Phase 8 prompts
  additionally instruct for a rewrite candidate. Free-form prose
  is not acceptable as primary output.
- Proofing prompts must instruct the LLM never to approve,
  execute, or call external tools.
- Temperature and sampling config are part of the run config
  artifact and are pinned for replay.

### LLM Output Schema

The proofing prompt must instruct the LLM to return a single JSON
object matching this schema. Any response that does not conform
is treated as a parse failure (see Phase 5).

Phase 5 output schema:

```
{
  "findings": [
    {
      "rule_id":     "<string>",
      "category":    "<ProofingCategory value>",
      "severity":    "<error | warning | note>",
      "message":     "<string>",
      "explanation": "<string>",
      "span":        "<string or null>"
    }
  ],
  "suggestions": [
    {
      "rule_id":  "<string>",
      "observed": "<string>",
      "proposed": "<string>"
    }
  ]
}
```

Phase 8 extends this schema by adding one field:

```
  "rewrite_candidate": "<string or null>"
```

rewrite_candidate is the full rewritten prompt text. It is null
when the LLM finds no rewrite needed. It is never applied
automatically; it is stored on the draft as normalized_text and
requires explicit review.

Rules:

- The LLM must return valid JSON. Prose outside the JSON object
  is not acceptable.
- findings is required and may be an empty array.
- suggestions is required and may be an empty array.
- rewrite_candidate is only present in Phase 8 mode; it is absent
  from Phase 5 responses.
- No field outside this schema may be present in the response.
  Extra fields cause a parse failure.

### Storage and Loading

Proofing prompts are stored as plain text files in a
proofing_prompts/ directory at the project root. The directory
structure is:

```
proofing_prompts/
  generic/
    v1.txt
    v2.txt
  fin123/
    v1.txt
  manifest.json
```

manifest.json maps each domain_profile to its active version:

```
{
  "generic": "v1",
  "fin123": "v1"
}
```

Loading rules:

- The engine reads manifest.json to resolve domain_profile to a
  version string.
- It then loads proofing_prompts/{domain_profile}/{version}.txt.
- The version string from the manifest is what gets recorded as
  proofing_prompt_version on the produced draft.
- The engine never infers "latest" -- it always reads the pinned
  version from the manifest.
- If a domain_profile is not in the manifest, the engine raises a
  validation error before making any LLM call.
- generic must always be present in the manifest. It is the
  fallback for intents that do not declare a specific domain.

Updating a proofing prompt means writing a new version file and
updating the manifest. The old version file is never deleted or
overwritten. This preserves replay: a prior draft that recorded
proofing_prompt_version: v1 can always reload v1.txt.

### Development Process

The categories in section 5 are the direct input to writing a
proofing prompt. Each proofing prompt must instruct the LLM to
inspect the input for every category relevant to that domain and
produce a structured finding for each one it detects.

Process for developing a proofing prompt:

1. Start from a base template that covers all generic categories
   from section 5 and defines the required output schema. The
   base template is the v1.txt file for the generic domain_profile
   created in Phase 4.
2. Add domain-specific rules on top of the base. Domain rules
   extend the base; they do not replace it.
3. Test the draft prompt against known example intents -- inputs
   where the expected findings are already decided. The prompt
   is not ready until it produces the expected findings reliably.
4. Iterate: adjust wording, tighten output schema constraints,
   and re-test until output is structured and findings are
   accurate.
5. Version and commit the prompt as a governed artifact. It is
   now immutable. Future changes produce a new version.

The base template must define the output schema the LLM must
follow: a JSON array of finding objects, each with rule_id,
category, severity, message, explanation, and an optional span.
Free-form prose outside that schema is not acceptable output.

A generic domain_profile (domain_profile: generic) must always
exist. It uses the base template with no additions and is the
fallback for intents that do not declare a domain.

Open question:

- How granular is versioning: per full prompt or per section?

## 14A. Deterministic Pre-Filter Specification

The pre-filter runs first on every input and cannot be disabled.
It performs three classes of checks:

1. Profanity: matches against a governed wordlist. Produces a
   finding with category disallowed_content, source deterministic,
   and severity ERROR.
2. Disallowed patterns: matches against a governed list of regular
   expressions. Produces a finding with category disallowed_content,
   source deterministic, and severity ERROR.
3. Formatting: verifies the input is non-empty and within the
   maximum allowed character length. A violation produces a finding
   with category structure, source deterministic, and severity ERROR.

Rule files are stored under pre_filter_rules/ at the project root:

```
pre_filter_rules/
  profanity.txt      -- one rule_id|term per line, case-insensitive
                        exact word boundary match
  disallowed.txt     -- one rule_id|regex per line
  formatting.json    -- {"max_chars": <integer>}
```

Rules:

- Rule files are plain text, version-controlled, and immutable
  once committed.
- Changing a rule file bumps proofing_rule_version before the
  change is used. The old file is never deleted or overwritten;
  replay must be able to reload the exact version that produced
  a given draft.
- The pre-filter loads rule files at engine startup. It does not
  reload them at runtime.
- Each matched rule produces exactly one ProofingFinding with the
  rule's rule_id.
- proofing_rule_version covers pre-filter rule changes only. Any
  change to any file in pre_filter_rules/ must bump
  proofing_rule_version. Changes to proofing prompt files bump
  proofing_prompt_version instead; these are separate and
  independent.

Phase assignment: pre_filter_rules/ and its initial rule files
are created in Phase 4 (as governed artifacts). Pre-filter code
that loads and applies them ships in Phase 5.

## 15. Phase Gates

Gates are mandatory. A phase may not begin until the prior gate
passes.

- No LLM proofer (Phase 5) before governance store and terminal
  format are agreed (Phase 4).
- No approval linkage (Phase 6) before a draft version_identity
  exists and is tested (Phases 2 and 3).
- No execution artifact work (Phase 7) before ApprovedPrompt
  linkage exists (Phase 6).
- No full LLM rewrite mode (Phase 8) before Phases 1 to 7 are
  complete and have passed their audits.
- Phases 1 to 4 contain no LLM calls. Phase 5 onwards may involve
  the LLM only under the governance doctrine in sections 14 and 14A.

## 16. Audit and Report Requirements

Every implementation phase must:

- write a phase report under docs/reports/, named for the phase,
  stating scope, findings, and a HOLD / WARNING / NOTE table and
  verdict;
- update docs/unified_diff.md with a dated change-log entry;
- run pytest, git diff --check, and the ASCII markdown check, and
  record the results in the phase report;
- keep all markdown ASCII-only.

A phase is not complete until its report is written and its
validation results are recorded.

## 17. Open Questions

- Where should drafts persist: flat files, or a simple append-only
  log? Deferred to Phase 4; must remain dependency-free.
- Should normalization stay record-only beyond v0, or become opt-in
  apply per rule? Current policy is record-only for v0 (section 9).
- How is span located in free text without a parser? May start as
  a line or character range only.
- Should rule sets be data-defined or code-defined? Affects how
  proofing_rule_version is computed.
- RESOLVED: draft_id is a randomly assigned UUID generated once
  at construction. It is not derived from content and is unique
  per draft instance. Phase 3 tests assert this.
- How are domain profiles discovered and loaded -- by name, by
  file, by registry? Must be deterministic and dependency-free.
- RESOLVED: domain_profile is an optional field on PromptIntent,
  defaulting to generic. The proofing engine reads it from the
  PromptIntent and records the resolved value on the produced
  PromptDraft.
- Who authors and reviews proofing prompts?
- Should proofing prompts pass through prompt123 before use?

## 18. Final Recommendation

Proceed with Phase 1 as the next implementation pass: enums and
value-object models only, with the tests listed under Phase 1. It
is the smallest governance-safe step, introduces no LLM calls, and
unblocks all later phases without committing to proofing logic.
Each subsequent phase is gated by section 15 and closed by a
report under section 16.
