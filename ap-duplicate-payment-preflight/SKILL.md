---
name: ap-duplicate-payment-preflight
description: Inspect accounts payable invoice, bill, or payment-run exports for exact and near duplicate payments before release. Use when finance, operations, or founders need to catch duplicate supplier invoices, vendor aliases, resubmitted bills, invoice-number variants, and paid-versus-pending collisions without connecting to an ERP or exposing credentials.
---

# AP Duplicate Payment Preflight

## Overview

Use this skill to turn an accounts payable export into a reviewable duplicate-payment exception report. The goal is to stop risky payments before release while preserving enough evidence for AP staff to decide whether each exception is a true duplicate, a credit/rebill, or an intentional recurring charge.

## Use And Do Not Use

Use for:

- AP payment-run review before ACH, wire, card, or check release.
- Bill, invoice, vendor, or payment exports from QuickBooks, NetSuite, Xero, Sage, Bill.com, Ramp, Coupa, SAP, Oracle, or an internal AP workflow.
- Finding invoice-number variants such as `INV-1007`, `INV1007`, `1007`, and OCR spacing differences.
- Catching vendor alias duplicates, duplicate vendor masters, paid-versus-pending resubmissions, and same-amount close-date collisions.
- Producing an exception pack that AP can review before approving payment.

Do not use for:

- Automatically cancelling, approving, or modifying payments in a live accounting system.
- Tax, audit, or legal conclusions. This skill produces operational review evidence.
- Fraud accusations. Label findings as duplicate-payment risk unless the user provides confirmed investigation results.
- Bank reconciliation across private bank feeds unless the user provides local exports and asks for local analysis.

## Required Inputs

Ask only for missing inputs that materially affect the decision:

- CSV or JSON export path, or a pasted sample if file access is unavailable.
- Column mapping if headers are non-obvious. Preferred fields: `vendor_name`, `vendor_id`, `invoice_number`, `invoice_date`, `payment_date`, `amount`, `currency`, `status`, `po_number`.
- Payment-run state: pending, approved, paid, or mixed.
- Review policy: same-vendor exact match, date window, vendor alias tolerance, recurring payment allowlist, and whether credits/rebills are expected.
- Output preference: Markdown report, CSV exception list, or both.

If the user only has a screenshot or a short sample, produce a sample-limited review and do not give a release decision for the full payment run.

## Workflow

### 1. Preserve The AP Review Boundary

Before classifying a duplicate, capture:

- Vendor name and vendor ID when present.
- Invoice number in raw and normalized forms.
- Amount, currency, invoice date, payment date, and status.
- Purchase order or memo if present.
- Whether a row is already paid, pending, approved, voided, credited, or reversed.

Read `references/duplicate-payment-rules.md` before classifying vendor aliases, recurring charges, credits, rebates, or tax/utility invoices.

### 2. Run The Local Preflight

Use the bundled script with explicit paths:

```bash
python3 ap-duplicate-payment-preflight/scripts/ap_duplicate_payment_preflight.py \
  --payments /absolute/path/ap_export.csv \
  --date-window-days 14
```

The script accepts CSV or JSON. JSON may be a list of payment objects or an object containing `payments`, `invoices`, `bills`, or `rows`.

### 3. Classify Exceptions

Use one primary action:

- `hold_payment`: same vendor or vendor alias, same normalized invoice number, same amount and currency, or a paid-versus-pending collision.
- `ap_review`: near match with same amount and close dates, missing invoice number, vendor alias, or same PO.
- `allow_with_note`: recurring, credit/rebill, tax, utility, rent, or subscription pattern that still needs the reviewer note recorded.
- `no_exception`: no meaningful duplicate signal.

Use one primary risk:

- `high`: exact invoice/amount match, paid-versus-pending collision, or vendor alias with same invoice and amount.
- `medium`: same amount within the review window with similar vendor or invoice, missing invoice number, or same PO with different invoice number.
- `low`: weak same-amount signal, common vendor, recurring context, or insufficient metadata.

Never recommend release when high-risk exceptions remain unresolved.

### 4. Produce The Exception Report

Return:

```markdown
## Payment Run Decision
[Hold payment run / Release after AP review / No material duplicate risk found]

## Duplicate Exceptions
| Risk | Action | Rows | Vendor | Invoice | Amount | Evidence | Reviewer next step |
|---|---|---|---|---|---:|---|---|

## Controls Checked
[Exact invoice match, normalized invoice match, vendor alias, same amount/date window, paid-versus-pending collision, PO collision]

## Safe Release Steps
[Rows to hold, rows to confirm, rows allowed with reviewer note, export/archive instruction]

## Open Questions
[Only items that affect payment release safety]
```

Use `templates/exception-report.md` when the user asks for a reusable AP review artifact.

### 5. Apply Guardrails Before Advising Payment Release

Do not advise release until:

- High-risk exceptions have a reviewer disposition.
- Paid and pending rows have been separated.
- Credits, reversals, voids, and rebills are not misread as duplicate payments.
- Vendor alias evidence is labeled as probable, not certain.
- The user has a way to hold or remove exception rows before payment release.

## Examples And Acceptance Checks

Positive example: "Use $ap-duplicate-payment-preflight on this QuickBooks bills export before we approve ACH." The skill should run the script, catch normalized invoice duplicates, paid-versus-pending collisions, and produce hold/review rows.

Positive alias example: "Our vendor master has Acme Services LLC and Acme Services as separate vendors." The skill should compare normalized vendor names and IDs, then mark same invoice/amount pairs for AP review.

Negative example: "Pay all invoices that look okay." Do not approve payments or operate a live AP system; produce a review report only.

Boundary example: "I pasted five rows from a screenshot." Produce sample-limited observations and ask for the export before making a payment-run decision.

## Validation

Smoke-test the bundled fixture:

```bash
python3 ap-duplicate-payment-preflight/scripts/ap_duplicate_payment_preflight.py \
  --payments ap-duplicate-payment-preflight/scripts/fixtures/ap_payments.csv \
  --date-window-days 14
```

Expected result: a Markdown report with `Payment Run Decision`, at least one `hold_payment`, at least one `ap_review`, `paid_vs_pending_collision`, and row numbers for reviewer follow-up.
