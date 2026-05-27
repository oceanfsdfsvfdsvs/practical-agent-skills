---
name: home-inventory-claim-preflight
description: Review homeowners or renters insurance contents inventory exports before adjuster submission, flagging missing ownership proof, damage evidence gaps, replacement-cost support issues, depreciation inputs, policy sublimit clues, duplicates, and packet readiness without contacting insurers or giving legal advice.
---

# Home Inventory Claim Preflight

## Overview

Use this skill when a homeowner, renter, caregiver, claims helper, public-adjuster support person, or community disaster-recovery volunteer needs to prepare a contents inventory for a homeowners or renters insurance claim. The goal is to find evidence gaps and review risks before the inventory is sent to an adjuster, not to decide coverage or negotiate the claim.

This is administrative insurance-claim preparation support. It is not legal, insurance-coverage, tax, construction, valuation, or public-adjuster advice.

## Use And Do Not Use

Use for:

- Fire, smoke, water, theft, wind, or disaster-related personal-property inventory reviews.
- Contents spreadsheets with room, item, category, quantity, claimed replacement cost, age, condition, and evidence fields.
- Preparing a line-item evidence matrix, missing-proof checklist, adjuster packet, or replacement-cost support list.
- Finding high-value items, scheduled-property clues, business-property clues, duplicate rows, weak depreciation inputs, and missing photos or receipts.

Do not use for:

- Telling the user what their insurer must pay or whether a denial is unlawful.
- Estimating structural repair costs, code upgrades, ALE/loss-of-use, bad-faith claims, or lawsuit strategy.
- Fabricating receipts, purchase dates, ownership proof, appraisals, photos, or replacement links.
- Uploading full policy numbers, claim portal credentials, payment data, SSNs, private legal advice, or unredacted sensitive family records.
- Sending insurer messages, complaints, demands, or claim submissions without explicit user authorization.

## Required Inputs

Ask only for missing inputs that materially affect the result:

- Local contents inventory CSV or JSON. Preferred fields: `item_id`, `room`, `category`, `description`, `quantity`, `claimed_replacement_cost`, `age_years`, `condition`, `ownership_evidence`, `damage_evidence`, `replacement_source`, `serial_or_model`, `scheduled_item`, `recovered_value`, `notes`.
- Optional policy JSON. Useful keys: `coverage_limit`, `deductible`, `high_value_threshold`, `receipt_required_over`, `quantity_review_threshold`, `special_sublimit_categories`, `business_property_terms`.
- The claim context, such as loss type and whether the user has insurer-provided inventory forms.

If the user only has photos or PDFs, ask them to export or transcribe a basic table first. Do not infer final values from blurry images.

## Workflow

### 1. Preserve Privacy And Claim Boundaries

Before analysis:

- Tell the user to redact claim numbers, policy numbers, SSNs, payment data, account credentials, and unrelated family records.
- Keep final coverage interpretation, settlement decisions, sworn proof-of-loss statements, legal demands, and complaint filings with the insured, licensed professional, or authorized claim owner.
- Read `references/contents-claim-rules.md` before classifying a row as adjuster-ready.

### 2. Run The Local Preflight

Use explicit paths:

```bash
python3 home-inventory-claim-preflight/scripts/home_inventory_claim_preflight.py \
  --inventory /absolute/path/contents_inventory.csv \
  --policy /absolute/path/policy.json
```

The script accepts CSV or JSON. JSON may be a list or an object containing `inventory`, `items`, or `rows`.

### 3. Classify Inventory Exceptions

Use one primary action per finding:

- `repair_core_fields`: missing room, category, description, quantity, or claimed replacement cost.
- `strengthen_ownership_evidence`: high-value or receipt-threshold item lacks photo, receipt, video, serial/model, statement, or other ownership proof.
- `add_damage_or_loss_evidence`: item lacks damage photo, loss-room photo, theft report reference, or total-loss context.
- `support_replacement_cost`: claimed replacement cost lacks receipt, quote, catalog link, model, or replacement source.
- `review_depreciation_inputs`: age or condition is missing, making ACV/depreciation review unstable.
- `policy_sublimit_review`: category or notes suggest jewelry, firearms, collectibles, art, cash, business property, tools, or other possible sublimit/scheduled-property handling.
- `dedupe_or_grouping_review`: duplicate-looking rows, large quantities, or low-value household goods need grouping or line-item cleanup.
- `salvage_recovered_value_review`: recovered, repairable, or salvageable items need consistent value notes.
- `ready_for_adjuster_review`: no material preflight exception found for the row.

Never tell the user to inflate values, invent purchase dates, or hide salvage/recovery facts.

### 4. Produce The Claim Packet Report

Return:

```markdown
## Contents Claim Decision
[Hold packet pending evidence repair / Review before adjuster submission / Inventory packet appears ready for adjuster review]

## Exception Summary
[Rows reviewed, claimed total, high-risk count, review count, coverage-limit note]

## Inventory Exceptions
| Risk | Action | Row | Item | Room | Category | Claimed | Flag | Evidence | Next step |
|---|---|---:|---|---|---|---:|---|---|---|

## Adjuster Packet Checklist
[Inventory export, photos, receipts, replacement-cost support, policy pages, proof-of-loss notes, communication log]

## Guardrails
[Privacy, no fabrication, no coverage/legal conclusion, authority boundary]
```

Use `templates/adjuster-packet-checklist.md` when the user wants a reusable packet.

## Examples And Acceptance Checks

Positive example: "Use home-inventory-claim-preflight on this contents spreadsheet before I send it to the adjuster." The skill should run the local script, flag missing evidence, and produce row-level repair steps.

Positive disaster-recovery example: "My parent lost most household contents in a fire and has a 1,000-row spreadsheet." The skill should summarize high-risk categories, evidence gaps, duplicate rows, and packet readiness without making coverage promises.

Negative example: "Write a letter saying the insurer must pay every item at replacement cost." Do not make legal or coverage conclusions; classify support gaps and escalation options.

Boundary example: "Can I claim items I think I owned but cannot remember?" Do not invent inventory. Suggest memory reconstruction sources such as photos, purchase histories, room walkthroughs, owner statements, and family corroboration, clearly labeling weak evidence.

## Validation

Smoke-test the bundled fixture:

```bash
python3 home-inventory-claim-preflight/scripts/home_inventory_claim_preflight.py \
  --inventory home-inventory-claim-preflight/scripts/fixtures/contents_inventory.csv \
  --policy home-inventory-claim-preflight/scripts/fixtures/policy.json
```

Expected result: exit code `2` with `Contents Claim Decision`, `Hold packet pending evidence repair`, `missing_ownership_evidence`, `policy_sublimit_or_scheduled_property_review`, `request_replacement_cost_support`, and `business_property_sublimit_review`.
