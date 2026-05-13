---
name: chargeback-evidence-pack
description: Assemble reason-coded merchant dispute evidence packs from local order, receipt, tracking, support, and policy evidence without exposing secrets or private logs.
---

# Chargeback Evidence Pack

Use this mirror to invoke the repository skill at `chargeback-evidence-pack/SKILL.md`.

## Workflow

1. Confirm the dispute reason code and deadline.
2. Inventory local evidence files before drafting claims.
3. Run `chargeback-evidence-pack/scripts/chargeback_evidence_pack.py` when a case file and evidence directory are available.
4. Redact secrets, unrelated customer data, full card data, and raw private logs.
5. Produce a challenge/accept recommendation with evidence gaps and processor-ready next steps.

Keep the full repository available so relative script and reference paths resolve correctly.
