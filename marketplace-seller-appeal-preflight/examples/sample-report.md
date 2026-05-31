# Marketplace Seller Appeal Preflight Report

Run date: 2026-06-01

## Seller Appeal Decision
- Hold appeal pending evidence repair: 2
- Review before submit: 1

## Case Rows
| Case | Marketplace | Scope | Reason | Decision | Blockers | Review notes |
|---|---|---|---|---|---|---|
| AMZ-1001 | Amazon | ASIN B0CASE01 / SKU CASE-RED | authenticity | Hold appeal pending evidence repair | missing_root_cause, missing_supply_chain_invoice, supplier_docs_do_not_match_listing, sensitive_file_redaction_required | appeal_deadline_within_3_days |
| AMZ-1002 | Amazon | Account | account_deactivation | Hold appeal pending evidence repair | missing_corrective_action, missing_preventive_action | prior_appeals_rejected |
| WMT-2001 | Walmart | order O-2001 | fulfillment | Review before submit | - | missing_policy_mapping |

## Submit Guardrails
- Do not submit until blockers are resolved or explicitly accepted by the seller owner.
- Do not invent invoices, authorization, customer statements, compliance documents, root causes, or remediation.
- Redact credentials, private keys, full payment data, and unrelated customer records before upload.
