"""prompt123 - a governed prompt proofing and governance substrate.

prompt123 transforms raw analyst prompt intent into reviewable PromptDraft
artifacts. It does not execute prompts. See docs/contracts/PRODUCT_CONTRACT.md
for the governing contract.

Canonical ontology:

    PromptIntent -> PromptDraft -> ApprovedPrompt -> ExecutionArtifact -> Audit
"""

__version__ = "0.0.1"
