# prompt123

A governed prompt proofing and governance substrate for institutional LLM
execution systems.

## What this is

prompt123 takes raw analyst prompt intent and helps produce governed
`PromptDraft` artifacts. Those drafts can later be reviewed, approved,
pinned, and executed by any downstream execution system. fin123 is one
possible consumer, but prompt123 is not tied to it.

prompt123 exists to make LLM prompts as deterministic as possible
without erasing user intent. Users may express vague, incomplete, or
informal intent. prompt123 transforms that intent into a reviewable
governed `PromptDraft` by identifying ambiguity, missing schema, hidden
assumptions, nondeterministic wording, and unsafe external dependencies.
The goal is not to make prompts more clever. It is to make them more
deterministic, explainable, reviewable, and replay-safe.

prompt123 preserves the original intent unchanged and never silently
decides what the user meant. If intent remains ambiguous, the draft
carries findings rather than inventing certainty.

The doctrine is small and explicit:

- Raw prompts are intent.
- Proofed prompts are drafts.
- Approved prompts are execution artifacts.
- Execution systems own approval and execution.
- prompt123 must never silently rewrite and execute prompts.

## What this is not

prompt123 is not an LLM execution engine, not an agent framework, not a
prompt optimizer that silently rewrites prompts, and not a fin123
implementation. It makes no runtime LLM calls and contacts no external
APIs.

## Future LLM-assisted proofing

prompt123 may later use an LLM to assist proofing. If it does, the LLM
is advisory only: it proposes findings and normalization, never approves
or executes anything, and every suggestion is recorded as reviewable,
replayable governance evidence. Deterministic rule-based proofing
remains valid without any LLM. See the product contract for the
governing doctrine.

## Canonical ontology

```
PromptIntent -> PromptDraft -> ApprovedPrompt -> ExecutionArtifact -> Audit
```

See `docs/contracts/PRODUCT_CONTRACT.md` for the full product contract.

## Layout

```
prompt123/            Python package (placeholder modules only)
docs/contracts/       Product contract
docs/unified_diff.md  Change-tracking conventions
tests/                Minimal placeholder tests
```

## Status

Contract-first skeleton. There is intentionally no execution logic yet.
