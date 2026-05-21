---
name: invoice-three-way-match-preflight
description: Review supplier invoice lines against purchase orders and receiving records before payment release. Use when AP, procurement, receiving, operations, or founders need a local three-way match exception report that flags missing POs, unapproved or closed POs, vendor mismatches, quantity/price variance, missing receipts, and already-approved invoices with unresolved exceptions.
---

# Invoice Three-Way Match Preflight

## Overview

Use this skill to turn local invoice, purchase-order, and receipt exports into a reviewable three-way match exception report. The goal is to keep AP from paying invoices that do not match what was ordered, approved, and received while giving each exception a clear owner and next step.

## Use And Do Not Use

Use for:

- AP invoice review before ACH, wire, card, check, or ERP payment release.
- Matching invoice lines against purchase orders and receiving reports from QuickBooks, NetSuite, Sage, SAP, Oracle, Coupa, Bill.com, Ramp, Xero, or internal spreadsheets.
- Finding missing PO references, closed or unapproved POs, vendor mismatches, quantity overbilling, price variance, missing receipts, and partial-receipt exceptions.
- Producing an exception packet for AP, procurement, receiving, and requester review.

Do not use for:

- Automatically approving, posting, cancelling, or paying invoices in a live accounting system.
- Tax, audit, legal, or fraud conclusions. This skill produces operational review evidence.
- OCR extraction from raw invoice PDFs unless the user also provides structured exports or asks for a sample-limited manual review.
- Replacing local approval policy, tolerance rules, or segregation-of-duties controls.

## Required Inputs

Ask only for missing inputs that materially affect payment-release safety:

- Invoice line export path or pasted rows.
- Purchase-order line export path or pasted rows.
- Receipt or goods-received export path or pasted rows.
- Column mapping if headers are non-obvious. Preferred fields: `invoice_number`, `vendor_id`, `po_number`, `line_id`, `item_sku`, `quantity`, `unit_price`, `line_amount`, `currency`, `approval_status`.
- Tolerance policy for unit price and line amount variance. Default local script settings are `5.00` amount and `2%` unit-price variance.
- Output preference: Markdown report, CSV summary, or both.

If the user provides only partial data, state the review boundary and do not give a full payment-release decision.

## Workflow

### 1. Preserve The Review Boundary

Before classifying an exception, capture:

- Invoice number, vendor, PO number, line ID or SKU, quantity, unit price, line amount, currency, and approval status.
- PO status, approval state, ordered quantity, unit price, and vendor.
- Receipt quantity net of rejected quantity.
- Whether the invoice is already approved or scheduled despite open match exceptions.

Read `references/three-way-match-rules.md` before classifying missing receipts, partial receipts, price variance, or closed-PO exceptions.

### 2. Run The Local Preflight

Use explicit paths:

```bash
python3 invoice-three-way-match-preflight/scripts/invoice_three_way_match_preflight.py \
  --invoices /absolute/path/invoices.csv \
  --purchase-orders /absolute/path/purchase_orders.csv \
  --receipts /absolute/path/receipts.csv \
  --amount-tolerance 5.00 \
  --percent-tolerance 0.02
```

The script accepts CSV or JSON. JSON may be a list or an object containing `invoices`, `invoice_lines`, `purchase_orders`, `po_lines`, `receipts`, `receipt_lines`, or `rows`.

### 3. Classify Exceptions

Use one primary action:

- `hold_invoice`: high-risk mismatch that should not be released until the owner records a disposition.
- `route_exception`: medium-risk mismatch that needs AP, procurement, receiving, or requester review.
- `review_note`: weak or policy-dependent exception that needs a reviewer note.
- `no_exception`: no material match exception found in the provided data.

Use one primary owner:

- `AP`: math, currency, invoice metadata, coding, duplicate approval state.
- `procurement`: missing, closed, unapproved, or changed PO; price or vendor mismatch.
- `receiving`: missing receipt, partial receipt, rejected goods, or service acceptance gap.
- `requester_or_procurement`: no-PO invoice that needs owner confirmation or retroactive approval.

Never recommend payment release when high-risk exceptions remain unresolved.

### 4. Produce The Exception Report

Return:

```markdown
## Three-Way Match Decision
[Hold affected invoices / Route exceptions before payment / No material three-way match exceptions found]

## Exceptions
| Risk | Action | Invoice | PO | Vendor | Amount | Flags | Owner | Reviewer next step |
|---|---|---|---|---|---:|---|---|---|

## Controls Checked
[PO status, vendor, currency, quantity, price, line amount, receipt coverage, approved-with-exception gate]

## Safe Release Gate
[Rows to hold, rows to route, owners, evidence still missing]

## Open Questions
[Only questions that affect payment-release safety]
```

Use `templates/exception-report.md` when the user asks for a reusable review artifact.

### 5. Apply Guardrails Before Advising Release

Do not advise release until:

- High-risk exceptions have a recorded owner and disposition.
- Missing or partial receipts are resolved or explicitly approved under policy.
- Price and quantity variances are tied to approved PO changes, corrected invoices, or documented exception approval.
- Already-approved invoices with unresolved match exceptions are paused.
- The user has a way to hold or remove affected invoice lines before payment release.

## Examples And Acceptance Checks

Positive example: "Use $invoice-three-way-match-preflight on these AP invoice, PO, and receipt exports before our payment run." The skill should run the script, flag missing receipts, PO/vendor mismatches, price/quantity variance, and produce owner-specific next steps.

Positive partial-receipt example: "The vendor shipped part of the PO and invoiced the full amount." The skill should mark invoice quantity above received quantity as high risk and route to receiving before AP release.

Negative example: "Just approve anything under $500." Do not approve live payments; produce an exception report and apply the user's documented tolerance policy.

Boundary example: "I only have an invoice PDF screenshot." Provide sample-limited observations and ask for structured invoice, PO, and receipt exports before making a payment-run decision.

## Validation

Smoke-test the bundled fixture:

```bash
python3 invoice-three-way-match-preflight/scripts/invoice_three_way_match_preflight.py \
  --invoices invoice-three-way-match-preflight/scripts/fixtures/invoices.csv \
  --purchase-orders invoice-three-way-match-preflight/scripts/fixtures/purchase_orders.csv \
  --receipts invoice-three-way-match-preflight/scripts/fixtures/receipts.csv
```

Expected result: a Markdown report with `Three-Way Match Decision`, at least one `hold_invoice`, `invoice_quantity_exceeds_received`, `unit_price_variance`, `vendor_mismatch`, and `closed_or_cancelled_po`.
