# Execution Report: [Short Title]

NOTE: This is a placeholder template. The structure below is a first guess
at the report format. It should be revised or replaced once the first real
execution pass has been completed and we know what a report actually needs
to capture.

---

Report type: [first / second / corrective / etc.] execution report
Source plan: Docs/plans/[plan_file.md]
Governing contract: Docs/contracts/PRODUCT_CONTRACT.md
Date: [YYYY-MM-DD]
Commit: [short hash]

This document records what was built during an execution pass against the
plan above. It does not restate the plan. It records decisions made,
deviations from the plan, validation results, and any items deferred to
the next pass.

---

## 1. Scope of This Pass

What was targeted. One paragraph, referencing the plan section(s) executed.

## 2. What Was Built

File-by-file or module-by-module summary of changes. Reference specific
files and line ranges where useful. No narrative — just what exists now
that did not before, and what changed.

## 3. Deviations from Plan

Any place the implementation diverged from the plan and why. If none, state
"No deviations."

## 4. Validation Results

- pytest: [N passed / N failed]
- git diff --check: [clean / issues]
- Any additional checks run and their outcomes

## 5. Contract Conformance

Brief assessment of whether the changes respect the product contract. Call
out any new scope risks, forbidden capabilities introduced, or doctrine
violations observed.

## 6. HOLD / WARNING / NOTE Table

| ID | Class   | Finding |
|----|---------|---------|
| 1  | NOTE    | [description] |

If none: "No items."

## 7. Summary

One paragraph. What was completed, what was deferred, and whether it is
safe to proceed to the next pass (audit, refine, or continue executing).

## Recommended Next Pass

State the next motion: audit, refine, or continue executing. Reference the
relevant plan section or a new audit if conformance should be checked first.
