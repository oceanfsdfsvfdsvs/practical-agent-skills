---
name: parcel-claim-preflight
description: Preflight parcel loss, damage, missing-contents, and late-delivery claims before a merchant, marketplace seller, ops team, or consumer submits evidence to UPS, FedEx, USPS, third-party shipping insurance, or a platform claim portal. Use when the user needs to identify missing proof of value, tracking scans, damage photos, packaging photos, original packaging, deadlines, declared-value exposure, redaction risks, or owner next steps for a shipping claim packet.
---

# Parcel Claim Preflight

## Overview

Use this skill to turn messy shipping records, customer messages, carrier scans, order receipts, photos, and packaging notes into a claim-readiness report. The goal is a practical evidence gate before submission, not legal advice or a guarantee that a carrier, insurer, or marketplace will pay.

## Use And Do Not Use

Use for:

- UPS, FedEx, USPS, regional carrier, marketplace, and third-party shipping insurance claims.
- Damaged parcels, lost parcels, missing contents, and late-delivery/service-failure claims.
- Merchants, ecommerce operators, warehouse teams, support teams, consumers, and claims helpers.
- Checking proof of value, tracking, photos, packaging retention, deadlines, declared value, and sensitive-file redaction.

Do not use for:

- Live claim submission unless the user explicitly asks and authorizes the exact portal action.
- Legal threats, carrier harassment, fraud accusations, or inventing facts about scans, packaging, value, or damage.
- Replacing carrier-specific instructions when the claim amount, deadline, or terms are material. Mark uncertain rules as "verify in carrier portal before submit."
- Uploading credentials, tokens, private customer records, full card data, or `.env` files.

## Required Inputs

Ask only for missing inputs that materially affect the claim decision:

- Shipment identifiers: shipment ID, tracking number, order ID, carrier, service level, ship date, delivery or last-scan date.
- Claim context: damage, loss, missing contents, or late delivery; discovery date; claim deadline if known.
- Value context: item value, declared value, insured value, currency, replacement/refund status.
- Evidence: proof of value, tracking scans, damage photos, outer packaging photos, inner packaging photos, original packaging status, recipient/customer statement, repair estimate, packing slip.
- Any carrier or platform claim instructions already shown to the user.

## Workflow

### 1. Classify The Claim

Normalize the claim type as `damage`, `loss`, `missing_contents`, `late`, or `unknown`. Identify the carrier/platform, deadline, claim owner, and whether the packet is time-sensitive.

Read `references/parcel-claim-rules.md` when the case involves claim-type evidence mapping, packaging retention, deadline triage, declared-value exposure, or redaction decisions.

### 2. Run Local Preflight When Files Exist

For a CSV-backed batch, run:

```bash
python3 parcel-claim-preflight/scripts/parcel_claim_preflight.py \
  --shipments /absolute/path/shipments.csv \
  --evidence-dir /absolute/path/evidence \
  --today 2026-05-31
```

Use the script output as the evidence inventory. For pasted notes or screenshots, apply the same matrix manually and mark file coverage as incomplete.

### 3. Repair The Packet Before Submission

Prioritize blockers:

- Passed or unknown deadline.
- Missing proof of value.
- Missing tracking/scans.
- Missing damage photos or packaging photos for damage claims.
- Original packaging unavailable when inspection may be required.
- Claim amount exceeds declared or insured value.
- Sensitive files that require redaction before upload.

Do not convert weak evidence into certainty. If a packet is weak but the deadline is close, produce an urgent submission plan that separates facts, missing proof, and owner acceptance.

### 4. Produce The Claim-Readiness Output

Use `templates/claim-readiness-report.md` for final reports. Include:

- Submit/hold/review decision.
- Row-level evidence status.
- Missing proof and how to obtain it.
- Deadline and declared-value risks.
- Redaction notes.
- Owner next steps before portal upload.

## Output Format

```markdown
## Parcel Claim Decision
[Submit-ready after owner review / Review before submit / Hold claim pending evidence repair]

## Claim Summary
| Shipment | Carrier | Type | Value | Deadline | Decision |
|---|---|---|---:|---|---|

## Evidence Matrix
| Shipment | Required evidence | Status | Source | Repair action |
|---|---|---|---|---|

## Blockers
| Shipment | Blocker | Why it matters | Next action |
|---|---|---|---|

## Submission Notes
[Concise carrier/platform-facing facts, no speculation]

## Do Not Upload
[Secrets, unrelated customer records, unsupported claims, or sensitive files found]
```

## Examples And Acceptance Checks

Positive damage example: "Use $parcel-claim-preflight on these Shopify shipments and photo folders before I submit UPS damage claims." The skill should check proof of value, tracking, damage photos, outer and inner packaging photos, original packaging, deadlines, declared value, and redaction.

Positive loss example: "A FedEx shipment stopped scanning and the customer says it never arrived." The skill should focus on tracking history, proof of value, recipient statement, trace/search status, deadline, declared/insured value, and replacement status.

Negative example: "Write an angry letter saying the carrier stole the item." Do not make accusations; produce a fact-grounded claim packet or explain why evidence is missing.

Boundary example: "The customer threw out the box." Mark packaging/inspection risk clearly. Do not claim the damage packet is submit-ready unless the owner accepts that risk.

## Validation

Smoke-test the bundled fixture:

```bash
python3 parcel-claim-preflight/scripts/parcel_claim_preflight.py \
  --shipments parcel-claim-preflight/scripts/fixtures/shipments.csv \
  --evidence-dir parcel-claim-preflight/scripts/fixtures/evidence \
  --today 2026-05-31
```

Expected result: a Markdown report with `Parcel Claim Decision`, at least one `Hold claim pending evidence repair`, and flags such as `damage_photos_missing`, `packaging_photos_missing`, `original_packaging_unavailable`, and `claim_deadline_passed`.
