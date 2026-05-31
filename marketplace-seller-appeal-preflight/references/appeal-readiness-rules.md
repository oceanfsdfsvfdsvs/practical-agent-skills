# Appeal Readiness Rules

This skill produces an operational appeal-preflight packet. It does not submit appeals, promise reinstatement, provide legal advice, or help a seller evade marketplace enforcement.

## Enforcement Type Evidence Map

| Type | Required evidence | Helpful evidence | Common weak packet |
|---|---|---|---|
| `authenticity` | Supplier invoice or receipt, product identity match, quantity/date coverage, supplier contact, listing/ASIN/SKU mapping | Authorization letter, product photos, packaging/label photos, chain-of-custody note | Generic apology with invoices that do not match the product or seller |
| `ip` | Complaint notice, rights-owner context, authorization/license/distributor letter, listing correction or removal evidence | Brand registry correspondence, revised listing copy, supplier agreement | Arguing with the rights owner without proving authorization |
| `used_sold_as_new` | Affected orders, customer messages, product/packaging photos, inspection or fulfillment-process evidence, refund/replacement records | SOP changes, warehouse training, supplier quality evidence | Blaming the buyer without showing process repair |
| `restricted_product` | Cited policy, product composition/specs, compliance certificate where applicable, listing cleanup evidence | Product safety docs, category approval record | "Other sellers do it" or unsupported policy interpretation |
| `safety` | Safety notice, compliance certificate, test report where applicable, corrective removal/recall/customer-remediation evidence | Supplier QA record, revised listing warnings | Missing certificate or vague "we checked quality" |
| `fulfillment` | Affected orders, tracking, late-shipment/cancellation metrics, carrier issue evidence, corrective workflow | Staffing/process changes, cutoff-time changes, inventory controls | Promise to improve without order-level facts |
| `customer_defect` | Order defect metrics, customer communications, refunds/replacements, defect reason analysis | SOP/training evidence, listing/quality corrections | Ignoring defect rate or repeating a rejected appeal |
| `account_deactivation` | Notice text, affected enforcement list, case IDs, appeal history, owner actions across every cited issue | Account health export, issue-by-issue evidence index | Treating account deactivation as a single apology instead of issue-by-issue repair |

## Plan Of Action Quality Gate

A submit-ready appeal should contain:

- Root cause: specific, evidence-backed cause that explains why the violation happened.
- Corrective action: what was already done for affected listings, orders, customers, inventory, or suppliers.
- Preventive action: durable control that reduces recurrence, with owner and operating cadence where possible.
- Evidence index: file names, dates, product/order/listing coverage, and what each document proves.
- Policy mapping: the cited marketplace policy or notice reason and how the repair addresses it.

Treat these as blockers:

- Root cause is blank, generic, accusatory, or unsupported.
- Corrective action only says "we will be careful" and does not cover affected inventory/listings/orders.
- Preventive action has no process, owner, check, or recurrence control.
- Supplier invoices, authorization letters, product photos, or compliance docs do not match the listing, seller, quantity, date, or product identity.
- Prior appeals were rejected and the new draft does not address the rejection reason.
- Sensitive or unrelated files would be uploaded.

## Deception And Safety Guardrails

- Never fabricate invoices, supplier letters, customer statements, compliance certificates, tracking records, or purchase orders.
- Never advise sellers to open new accounts, hide relationships, manipulate reviews, contact buyers improperly, or bypass marketplace enforcement.
- Mark uncertain claims as unknown and request owner verification.
- Keep final legal, marketplace, and portal-submission decisions with the seller or authorized representative.
- Redact unrelated customer data, full payment details, credentials, API tokens, private keys, and internal secrets.
