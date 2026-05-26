## Medical Bill Dispute Decision
Hold payment pending reconciliation: high-risk billing exceptions need written clarification before payment.

## Exception Summary
- Bill rows reviewed: 6
- EOB rows reviewed: 3
- Hold exceptions: 7
- Review exceptions: 4

## Billing Exceptions
| Risk | Action | Row | Provider | Service date | CPT | Balance | Flag | Evidence | Next step |
|---|---|---:|---|---|---|---:|---|---|---|
| high | hold_payment | 2 | Metro ER | 2026-04-02 | 99284 | USD 500.00 | balance_exceeds_eob_patient_responsibility | Bill balance USD 500.00 exceeds EOB responsibility USD 114.00. | Ask provider billing to reconcile the account to the EOB before payment. |
| high | hold_payment | 5 | Coastal Anesthesia | 2026-04-02 | 00812 | USD 1400.00 | missing_eob_or_unprocessed_insurance | Insurance is marked unprocessed and no matching EOB line was found. | Ask provider to submit or correct the claim and ask insurer whether an EOB is pending. |
| medium | request_itemized_bill | 6 | Regional Lab | 2026-04-03 | - | USD 450.00 | request_itemized_bill | Bill line lacks CPT/HCPCS or is not itemized. | Request an itemized bill or superbill with codes, dates, quantities, and charges. |
| high | appeal_review | 7 | Advanced Imaging | 2026-04-05 | 70553 | USD 2400.00 | appeal_review | EOB denial PA_REQUIRED: Prior authorization missing. | Ask insurer for appeal procedure, deadline, and required evidence. |

## Dispute Packet Checklist
- Itemized bill or superbill for flagged provider lines.
- EOB for each claim and any reprocessed EOB versions.
- Written provider reconciliation request for balances exceeding EOB responsibility.
- Plan appeal instructions for denied or noncovered lines.
- Call log with representative names, reference numbers, promised actions, and dates.
- Financial assistance, charity-care, self-pay, or payment-plan application when affordability is the issue.

## Guardrails
- This is administrative and financial workflow support, not legal, medical, tax, credit-repair, or insurance-coverage advice.
- Redact SSNs, full member IDs, payment card data, credentials, and unrelated clinical notes.
- Do not submit complaints, appeals, payments, or portal messages without explicit authority.
