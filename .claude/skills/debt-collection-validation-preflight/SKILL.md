---
name: debt-collection-validation-preflight
description: Preflight debt collection validation and dispute packets before a consumer, caregiver, financial counselor, legal-aid intake helper, or benefits advocate responds to a collector, debt buyer, collection agency, or collection law firm. Use when the user needs to check validation notices, 30-day dispute timing, collector identity, original-creditor requests, amount/itemization gaps, not-mine or paid-debt evidence, continued collection after a timely dispute, time-barred-debt review, redaction risks, and owner next steps without making live payments, filing complaints, or giving legal conclusions.
---

# Debt Collection Validation Preflight

Use the repository copy at `debt-collection-validation-preflight/SKILL.md` for the full workflow, references, templates, examples, and local validation script. Keep the full skill directory available so relative paths under `scripts/`, `references/`, and `templates/` resolve correctly.

Quick validation:

```bash
python3 debt-collection-validation-preflight/scripts/debt_collection_validation_preflight.py \
  --cases debt-collection-validation-preflight/scripts/fixtures/debt_collection_cases.csv \
  --evidence-dir debt-collection-validation-preflight/scripts/fixtures/evidence \
  --today 2026-06-17
```
