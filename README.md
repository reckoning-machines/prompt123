# prompt123

A governed prompt proofing and governance substrate for institutional LLM
execution systems.

## What this is

prompt123 takes raw analyst prompt intent and helps produce governed
`PromptDraft` artifacts. Those drafts can later be reviewed, approved,
pinned, and executed by downstream systems such as fin123.

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
