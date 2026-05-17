# Unified Diff Conventions

prompt123 treats prompt change as a governed event. When a `PromptIntent`
becomes a `PromptDraft`, or a draft is revised, the difference must be
expressed as a reviewable unified diff.

## Why

The governance doctrine forbids silent prompt rewriting. A unified diff
is the minimal honest record of a change: it shows the original text, the
proposed text, and nothing hidden in between.

## Conventions

- Diffs compare prompt text as plain UTF-8, line by line.
- The "before" side is the prior artifact (intent or prior draft).
- The "after" side is the proposed artifact.
- A diff is advisory until an explicit approval converts the "after"
  side into an `ApprovedPrompt`.
- Every diff is paired with an explanation of what changed and why, in
  keeping with the explainability rule in the product contract.

## Example shape

```diff
--- PromptIntent
+++ PromptDraft
@@
-summarize the portfolio
+Summarize the portfolio as of the stated as-of date.
+State assumptions explicitly. Do not infer missing positions.
```

This file documents the convention only. Diff generation is not
implemented in the initial scaffold.

## Change Log

- 2026-05-17: First standalone repository contract audit recorded at
  docs/audits/standalone_repo_contract_audit.md. Verdict: PASS WITH
  WARNINGS. Added docs/audits/ and docs/plans/.
- 2026-05-17: First implementation plan recorded at
  docs/plans/prompt_draft_proofing_substrate_plan.md. Plan-only pass for
  the PromptDraft proofing substrate. No runtime behavior added.
