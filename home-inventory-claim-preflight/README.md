# Home Inventory Claim Preflight

Review homeowners or renters insurance contents inventory exports before sending them to an adjuster.

This skill is for homeowners, renters, caregivers, claims helpers, and disaster-recovery volunteers who need a local-first way to find missing proof, weak valuation support, sublimit clues, duplicate rows, and packet readiness issues in a contents claim spreadsheet.

## What It Catches

- High-value items with weak ownership evidence.
- Missing damage photos or loss-context evidence.
- Claimed replacement costs without receipts, quotes, model details, or replacement sources.
- Missing age or condition fields that make depreciation review unstable.
- Jewelry, firearms, collectibles, art, tools, business property, and other possible sublimit/scheduled-property clues.
- Duplicate rows, excessive quantities, low-value household goods that may need grouping, and salvage/recovery inconsistencies.

## Quick Start

```bash
python3 home-inventory-claim-preflight/scripts/home_inventory_claim_preflight.py \
  --inventory home-inventory-claim-preflight/scripts/fixtures/contents_inventory.csv \
  --policy home-inventory-claim-preflight/scripts/fixtures/policy.json
```

Input may be CSV or JSON. Preferred fields:

```text
item_id, room, category, description, quantity, claimed_replacement_cost,
age_years, condition, ownership_evidence, damage_evidence, replacement_source,
serial_or_model, scheduled_item, recovered_value, notes
```

## Output

The script produces a Markdown report with:

- Overall packet decision.
- Exception summary and claimed total.
- Row-level inventory exceptions.
- Adjuster packet checklist.
- Privacy, fabrication, legal/coverage, and authority guardrails.

## Safety

- This is administrative claim-preparation support, not legal, coverage, tax, construction, valuation, or public-adjuster advice.
- The script does not call insurer portals, government systems, vendors, or external valuation services.
- Do not paste full policy numbers, claim numbers, SSNs, payment data, account credentials, private legal advice, or unrelated family records into prompts or fixtures.
- Keep final coverage, settlement, proof-of-loss, complaint, and legal decisions with the insured, licensed professional, or authorized claim owner.
