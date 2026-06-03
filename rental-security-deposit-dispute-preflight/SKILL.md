---
name: rental-security-deposit-dispute-preflight
description: Preflight residential rental security deposit return or deduction disputes before a tenant, renter helper, housing advocate, property manager, or small-claims filer sends a demand letter, complaint, or court packet. Use when the user needs to check refund deadlines, itemized deduction statements, normal wear-and-tear claims, move-in and move-out evidence, forwarding-address proof, receipts or estimates, deposit-cap issues, redaction risks, and owner next steps without making legal conclusions or filing live claims.
---

# Rental Security Deposit Dispute Preflight

## Overview

Use this skill to turn lease notes, move-out dates, deposit ledgers, itemized deductions, photos, walkthrough notes, and communications into a dispute-readiness report. The goal is an evidence and deadline gate before a tenant or helper sends a demand letter, agency complaint, or small-claims packet. It is not legal advice, and it does not decide who will win.

## Use And Do Not Use

Use for:

- Residential rental security deposit return disputes and deduction reviews.
- Tenants, roommates, caregivers, housing navigators, legal-aid intake helpers, and property managers doing a preflight check.
- Deadline, itemization, normal wear-and-tear, move-in condition, move-out photo, forwarding-address, receipt, demand-letter, and redaction review.
- Local file review where evidence is in CSV rows, pasted notes, screenshots, PDFs, photos, or email exports.

Do not use for:

- Live small-claims filing, attorney-client advice, eviction defense, rent strike planning, or harassment of a landlord.
- Inventing facts about property condition, dates, service, receipts, or communications.
- Jurisdiction-specific certainty when the governing state, city, lease terms, or current law is uncertain. Mark rules as "verify locally before send."
- Uploading full SSNs, bank details, full ID scans, private keys, tokens, `.env` files, or unrelated tenant/landlord records.

## Required Inputs

Ask only for missing inputs that materially affect the decision:

- Jurisdiction: state, city if relevant, lease type if known.
- Dates: move-out date, key return or possession surrender date, refund date, itemized-statement date, demand-letter date if any.
- Money: deposit amount, rent amount if relevant, amount withheld, refund amount, deduction rows.
- Evidence: lease, deposit receipt, move-in condition form/photos, move-out photos/videos, inspection notes, forwarding-address proof, itemized statement, receipts or estimates, communications, demand letter.
- Tenant context: forwarding address sent, pre-move-out inspection requested/offered when relevant, damage admitted, unpaid rent or lease-break issues.

## Workflow

### 1. Classify The Dispute

Normalize the case as `late_return`, `deduction_dispute`, `missing_itemization`, `normal_wear_tear`, `deposit_cap_or_receipt`, or `mixed`. Identify the jurisdiction, deposit amount, withheld amount, and deadline clock.

Read `references/deposit-dispute-rules.md` when the case turns on jurisdiction deadlines, itemized deductions, forwarding-address proof, normal wear-and-tear, receipts, deposit caps, or demand-letter sequencing.

### 2. Run Local Preflight When Files Exist

For CSV-backed batches, run:

```bash
python3 rental-security-deposit-dispute-preflight/scripts/rental_security_deposit_dispute_preflight.py \
  --cases /absolute/path/deposit_cases.csv \
  --rules rental-security-deposit-dispute-preflight/scripts/fixtures/state_rules.json \
  --evidence-dir /absolute/path/evidence \
  --today 2026-06-04
```

Use the script output as the evidence inventory. For pasted notes or screenshots, apply the same matrix manually and mark file coverage as incomplete.

### 3. Repair The Packet Before Escalation

Prioritize blockers:

- Refund or itemized statement deadline appears passed.
- No itemized deduction statement when money was withheld.
- No forwarding-address proof where it affects the refund clock.
- Deductions appear to charge normal wear-and-tear or routine turnover without support.
- Receipts, estimates, invoices, or photo evidence are missing for large deductions.
- Move-in condition evidence or move-out photos are missing.
- User asks the agent to submit a live court, agency, or payment action without explicit authorization.

If a deadline is close, separate "send now to preserve rights" from "evidence still missing." Do not turn weak facts into certainty.

### 4. Produce The Dispute-Readiness Output

Use `templates/deposit-dispute-report.md` for final reports. Include:

- Hold/review/ready decision.
- Deadline and itemization status.
- Deduction issue matrix.
- Missing evidence and how to obtain or label it.
- Demand-letter or small-claims packet next steps.
- Redaction and live-action guardrails.

## Output Format

```markdown
## Security Deposit Dispute Decision
[Ready for owner review / Review before escalation / Hold dispute packet pending evidence repair]

## Case Summary
| Case | State | Deposit | Withheld | Deadline | Decision |
|---|---|---:|---:|---|---|

## Evidence Matrix
| Case | Evidence | Status | Source | Repair action |
|---|---|---|---|---|

## Blockers
| Case | Blocker | Why it matters | Next action |
|---|---|---|---|

## Demand Packet Notes
[Concise facts, dates, amounts, and attachments; no threats or unsupported claims]

## Do Not Upload
[Secrets, unrelated records, full IDs, account numbers, or unsupported allegations]
```

## Examples And Acceptance Checks

Positive example: "Use $rental-security-deposit-dispute-preflight on this lease, move-out timeline, landlord deduction PDF, and photo folder before I send a demand letter." The skill should check refund deadline, itemized statement timing, deduction categories, receipts, move-in/out evidence, forwarding-address proof, and redactions.

Positive batch example: "Review these 12 tenant deposit cases for legal-aid intake." The skill should produce row-level hold/review/ready decisions and identify which files are missing.

Negative example: "Write a threatening letter saying the landlord committed fraud." Do not accuse. Produce a fact-grounded demand packet or explain evidence gaps.

Boundary example: "I do not know the state." Mark jurisdiction rules as unverified and ask for state/city before giving deadline-based conclusions.

## Validation

Smoke-test the bundled fixture:

```bash
python3 rental-security-deposit-dispute-preflight/scripts/rental_security_deposit_dispute_preflight.py \
  --cases rental-security-deposit-dispute-preflight/scripts/fixtures/deposit_cases.csv \
  --rules rental-security-deposit-dispute-preflight/scripts/fixtures/state_rules.json \
  --evidence-dir rental-security-deposit-dispute-preflight/scripts/fixtures/evidence \
  --today 2026-06-04
```

Expected result: a Markdown report with `Security Deposit Dispute Decision`, at least one `Hold dispute packet pending evidence repair`, and flags such as `late_itemized_statement`, `missing_itemized_statement`, `normal_wear_tear_deduction_review`, `missing_move_out_condition_evidence`, and `live_action_requested`.
