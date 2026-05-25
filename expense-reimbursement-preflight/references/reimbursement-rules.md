# Reimbursement Review Rules

Use these rules to keep reimbursement reviews consistent and conservative.

## Hold-Level Signals

| Signal | Why It Matters | Default Action |
|---|---|---|
| Required receipt is missing | Approval lacks substantiation and may break accountable-plan or audit support. | `hold_reimbursement` |
| Duplicate receipt ID or duplicate employee/date/merchant/amount | Same expense may be reimbursed twice. | `hold_reimbursement` |
| Prohibited category or sensitive term | Policy may forbid reimbursement or require controller approval. | `hold_reimbursement` |
| Mileage rate exceeds policy | Reimbursement amount is mechanically inconsistent with stated miles. | `hold_reimbursement` |

## Review-Level Signals

| Signal | Why It Matters | Default Action |
|---|---|---|
| Category limit exceeded | Manager or finance needs documented exception approval. | `manager_review` |
| Meal or event lacks attendees | Business relationship and substantiation are incomplete. | `manager_review` |
| Itemized receipt missing | Total-only receipts can hide alcohol, personal items, tips, or taxes. | `manager_review` |
| Late submission | Policy may limit reimbursement or require exception approval. | `manager_review` |
| Missing purpose | Employee needs to explain the business connection. | `employee_correction` |
| Missing project or GL code | Export may create accounting cleanup work. | `coding_review` |

## Guardrails

- Classify exceptions, not misconduct.
- Apply the user's written policy when it conflicts with defaults.
- Do not infer final tax treatment or labor-law obligations.
- Do not process full card numbers, bank details, personal documents, tokens, or private keys.
- Preserve receipts, approvals, exception notes, and export evidence.
- Keep review close to submission; chasing missing context weeks later is the failure mode this skill is meant to reduce.
