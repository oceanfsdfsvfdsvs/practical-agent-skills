# Sample Expense Reimbursement Report

## Expense Reimbursement Decision

Hold reimbursement: high-risk exceptions need correction before approval.

## Exception Summary

- Rows reviewed: 6
- Hold exceptions: 5
- Review/correction exceptions: 9

## Expense Exceptions

| Risk | Action | Row | Employee | Category | Merchant | Amount | Flag | Evidence | Next step |
|---|---|---:|---|---|---|---:|---|---|---|
| high | hold_reimbursement | 2 | Avery Chen | client_meal | North Pier Grill | USD 236.40 | duplicate_receipt_or_charge | Receipt ID RCPT-7781 appears more than once. | Confirm one reimbursable claim and remove or explain duplicates. |
| medium | manager_review | 2 | Avery Chen | client_meal | North Pier Grill | USD 236.40 | meal_attendees_missing | Meal, event, or client entertainment expense lacks attendee names. | Add attendee list and business relationship before approval. |
| high | hold_reimbursement | 4 | Blair Patel | supplies | OfficeMax | USD 186.19 | missing_receipt | USD 186.19 requires receipt support. | Attach receipt or missing-receipt affidavit before approval. |
| high | hold_reimbursement | 5 | Casey Morgan | mileage | Field visit route | USD 98.00 | mileage_rate_exceeds_policy | Claimed USD 0.82/mile exceeds policy USD 0.70/mile. | Recalculate mileage reimbursement or document approved exception. |
| high | hold_reimbursement | 6 | Drew Rivera | gift_card | Amazon | USD 150.00 | prohibited_or_sensitive_category | Category or notes include restricted term: gift_card. | Route to finance owner for exception approval or employee correction. |

## Guardrails

- Treat findings as reimbursement-control exceptions, not fraud conclusions.
- Do not approve, reject, or edit live expense-system records without explicit authority.
- Preserve receipts, policy exceptions, manager approval, and reimbursement export evidence.
- Apply the user's local policy when it is stricter than the bundled defaults.
