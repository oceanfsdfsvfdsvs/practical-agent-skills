---
name: medical-bill-dispute-preflight
description: Review patient medical bills, itemized statements, and insurance EOB exports for mismatches, missing EOBs, duplicate charges, surprise-billing clues, denial/appeal triggers, and financial-assistance next steps before a patient pays or escalates a billing dispute.
---

# Medical Bill Dispute Preflight

Use the canonical skill at `medical-bill-dispute-preflight/SKILL.md`.

Keep the full repository available when running the bundled local script so relative paths resolve correctly:

```bash
python3 medical-bill-dispute-preflight/scripts/medical_bill_dispute_preflight.py \
  --bills medical-bill-dispute-preflight/scripts/fixtures/medical_bills.csv \
  --eob medical-bill-dispute-preflight/scripts/fixtures/eob.csv \
  --policy medical-bill-dispute-preflight/scripts/fixtures/policy.json
```

This skill provides administrative and financial workflow support only. Do not provide medical, legal, tax, credit-repair, or guaranteed insurance-coverage advice.
