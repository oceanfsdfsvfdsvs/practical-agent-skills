---
name: ap-duplicate-payment-preflight
description: Inspect accounts payable invoice, bill, or payment-run exports for exact and near duplicate payments before release. Use when finance, operations, or founders need to catch duplicate supplier invoices, vendor aliases, resubmitted bills, invoice-number variants, and paid-versus-pending collisions without connecting to an ERP or exposing credentials.
---

# AP Duplicate Payment Preflight

Use this skill when reviewing local AP exports before payment release. Prefer the full skill directory when available because it includes the deterministic scanner, rules, template, and fixtures.

## Workflow

1. Ask for the CSV or JSON export path and any column mapping that is not obvious.
2. Run the local scanner from the skill directory:

```bash
python3 scripts/ap_duplicate_payment_preflight.py --payments scripts/fixtures/ap_payments.csv --date-window-days 14
```

3. Classify rows as `hold_payment`, `ap_review`, `allow_with_note`, or `no_exception`.
4. Do not approve or modify live payments. Produce a review report with row-level evidence and reviewer next steps.

## Guardrails

- Hold high-risk exact or normalized invoice duplicates until AP disposition exists.
- Treat paid-versus-pending collisions as high risk.
- Label vendor alias matches as probable, not certain.
- Do not block recurring, tax, utility, credit, reversal, void, or corrected-bill rows without context.
- Do not use live ERP credentials unless the user explicitly asks and provides environment-based authorization.
