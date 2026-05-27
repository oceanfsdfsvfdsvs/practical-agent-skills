---
name: home-inventory-claim-preflight
description: Review homeowners or renters insurance contents inventory exports before adjuster submission, flagging missing ownership proof, damage evidence gaps, replacement-cost support issues, depreciation inputs, policy sublimit clues, duplicates, and packet readiness without contacting insurers or giving legal advice.
---

# Home Inventory Claim Preflight

Use this Claude Code skill from the repository root so relative paths resolve. The canonical workflow, guardrails, script command, examples, and validation steps live in `home-inventory-claim-preflight/SKILL.md`.

Run the local fixture smoke test:

```bash
python3 home-inventory-claim-preflight/scripts/home_inventory_claim_preflight.py \
  --inventory home-inventory-claim-preflight/scripts/fixtures/contents_inventory.csv \
  --policy home-inventory-claim-preflight/scripts/fixtures/policy.json
```

Follow these boundaries:

- Treat this as administrative claim-preparation support, not legal, coverage, tax, construction, valuation, or public-adjuster advice.
- Do not fabricate receipts, purchase dates, appraisals, photos, replacement links, model numbers, or ownership stories.
- Redact policy numbers, claim numbers, SSNs, payment data, credentials, private legal advice, and unrelated family records.
- Keep final coverage, settlement, proof-of-loss, complaint, and legal decisions with the insured, licensed professional, or authorized claim owner.
