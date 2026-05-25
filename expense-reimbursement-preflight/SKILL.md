---
name: expense-reimbursement-preflight
description: Review employee reimbursement or expense-report exports for missing receipts, duplicate claims, policy-limit issues, attendee or purpose gaps, mileage-rate errors, stale submissions, and coding gaps before approval, payroll, or ERP export. Use when finance, operations, managers, or founders need local-first reimbursement exceptions without logging into expense software.
---

# Expense Reimbursement Preflight

## Overview

Use this skill to turn employee reimbursement exports into a reviewable exception report before approval or payroll release. The goal is to catch missing substantiation, duplicate receipt or charge claims, policy-limit breaks, mileage-rate errors, and accounting context gaps while keeping final reimbursement decisions with the authorized owner.

## Use And Do Not Use

Use for:

- Employee reimbursement reports, corporate-card expense reports, spreadsheet claims, or expense-system exports.
- Pre-approval review before payroll, ACH, AP reimbursement, or ERP import.
- Checking receipts, duplicate claims, category limits, attendee lists, business purpose, mileage rate, late submission, currency, project, and GL coding.
- Creating an employee correction list and manager/finance review queue.

Do not use for:

- Tax, legal, labor-law, or fraud conclusions.
- Approving, rejecting, editing, or submitting live expense-system records without explicit user instruction.
- Processing full card numbers, bank details, private keys, tokens, or unrelated personal documents.
- Replacing a company's written reimbursement policy or controller judgment.

## Required Inputs

Ask only for missing inputs that materially affect the decision:

- Local CSV or JSON expense report export.
- Preferred fields: `report_id`, `employee`, `expense_date`, `submitted_date`, `category`, `merchant`, `amount`, `currency`, `receipt_id`, `receipt_attached`, `itemized_receipt`, `business_purpose`, `attendees`, `project`, `gl_code`, `miles`, `notes`.
- Local policy JSON when available: receipt thresholds, category limits, mileage rate, late-submission age, prohibited categories, and required attendees or itemized receipts.
- Review date if not today.

If no policy is supplied, say that bundled defaults are only a starting point and should be replaced by the user's written policy.

## Workflow

### 1. Preserve The Approval Boundary

Before classifying exceptions, capture:

- Who submitted the report and who can approve it.
- Expense date, submission date, amount, category, merchant, and currency.
- Receipt identifier or attachment status, itemized receipt status, purpose, attendees, project, and GL code.
- The written policy or explicit thresholds being applied.

Read `references/reimbursement-rules.md` before treating a row as safe to reimburse.

### 2. Run The Local Preflight

Use explicit paths:

```bash
python3 expense-reimbursement-preflight/scripts/expense_reimbursement_preflight.py \
  --expenses /absolute/path/expense_report.csv \
  --policy /absolute/path/policy.json \
  --today 2026-05-26
```

The script accepts CSV or JSON. JSON may be a list or an object containing `expenses`, `rows`, `claims`, or `report`.

### 3. Classify Reimbursement Exceptions

Use one primary action:

- `hold_reimbursement`: missing required receipt, duplicate receipt or charge, prohibited category, or mileage rate above policy.
- `manager_review`: category limit exceeded, late submission, missing itemized receipt, or missing attendees.
- `employee_correction`: missing business purpose or similar submitter-owned gap.
- `coding_review`: missing project, client, job, or GL code.
- `finance_review`: currency, FX, or local-policy ambiguity.

Never label a row as fraud unless the user provides completed investigation findings.

### 4. Produce The Exception Report

Return:

```markdown
## Expense Reimbursement Decision
[Hold reimbursement / Review before reimbursement / No material reimbursement exceptions found]

## Exception Summary
[Rows reviewed, hold count, review count]

## Expense Exceptions
| Risk | Action | Row | Employee | Category | Merchant | Amount | Flag | Evidence | Next step |
|---|---:|---|---|---|---:|---|---|---|---|

## Guardrails
[Authority, privacy, evidence retention, local policy caveats]
```

Use `templates/exception-report.md` when the user asks for a reusable artifact.

## Examples And Acceptance Checks

Positive example: "Use $expense-reimbursement-preflight on this monthly reimbursement CSV and our policy JSON before payroll." The skill should run the script, hold missing receipts and duplicates, route meal attendee gaps to manager review, and preserve finance guardrails.

Positive small-business example: "We are still using spreadsheets and emailed receipts." The skill should create a correction list and avoid recommending a paid SaaS migration unless asked.

Negative example: "Approve everything under $100." Do not approve live reimbursements; apply documented policy and produce exceptions.

Boundary example: "I only have receipt photos." Ask for a structured report or create a limited checklist; do not infer amounts or attendees from unclear images as final evidence.

## Validation

Smoke-test the bundled fixture:

```bash
python3 expense-reimbursement-preflight/scripts/expense_reimbursement_preflight.py \
  --expenses expense-reimbursement-preflight/scripts/fixtures/expense_report.csv \
  --policy expense-reimbursement-preflight/scripts/fixtures/policy.json \
  --today 2026-05-26
```

Expected result: exit code `2` with `Expense Reimbursement Decision`, `Hold reimbursement`, `missing_receipt`, `duplicate_receipt_or_charge`, `meal_attendees_missing`, and `mileage_rate_exceeds_policy`.
