---
name: chargeback-evidence-pack
description: Assemble evidence-backed response packs for ecommerce, SaaS, marketplace, subscription, digital-goods, or service payment disputes and chargebacks. Use when a merchant needs to decide whether to accept or challenge a card dispute, map a Stripe, Shopify, PayPal, Adyen, Square, or bank reason code to evidence, identify missing proof, redact unsafe details, or produce a processor-ready dispute narrative before submitting.
---

# Chargeback Evidence Pack

## Overview

Use this skill to turn messy order records, processor notices, customer messages, fulfillment data, and policy snippets into a reason-coded chargeback response pack. The goal is a defensible submission plan, not legal advice or a guarantee that the issuer will reverse the dispute.

## Use and Do Not Use

Use for:

- Card disputes, chargebacks, friendly-fraud claims, payment reversals, and processor evidence requests.
- Stripe, Shopify Payments, PayPal, Adyen, Square, bank, marketplace, subscription, SaaS, digital-goods, service, or physical-goods disputes.
- Deciding whether to accept, refund, or challenge based on reason category, deadline, amount, evidence strength, and staff cost.
- Building a concise evidence index, missing-evidence list, redaction notes, and bank-facing narrative.

Do not use for:

- Legal strategy, debt collection, threats, public shaming, or contacting a customer's employer, family, or bank.
- Submitting evidence inside a live processor account unless the user explicitly asks and has authorized that action.
- Inventing policy acceptance, delivery, customer identity, authorization, refund, or usage facts.
- Sharing full card numbers, CVV, passwords, tokens, raw private logs, government IDs, or unrelated customer data.

## Required Inputs

Ask only for missing inputs that materially affect the dispute decision:

- Processor or platform, dispute ID, reason code/category, amount, currency, and submission deadline.
- Product type: physical good, digital good, SaaS/subscription, marketplace order, appointment/service, donation, or other.
- Order and payment details: order ID, charge date, order date, refund status, duplicate charge history, and fraud checks such as AVS, CVV, 3DS, device, or account history when available.
- Fulfillment or service proof: tracking and delivery, signature, carrier page, pickup record, access logs, download logs, usage events, appointment records, or service completion notes.
- Customer communications and policy evidence: terms, refund policy, cancellation policy, checkout acknowledgement, support tickets, emails, chat logs, and prior resolution offers.

If the reason code is unknown, classify the dispute by the customer's claim text and mark processor-specific rules as "verify before submit."

## Workflow

### 1. Classify The Dispute

Identify:

- Processor/platform and whether the evidence form has strict fields, file limits, or character limits.
- Reason category: product not received, fraudulent/no authorization, duplicate, credit not processed, product unacceptable/not as described, cancelled subscription, digital goods, or unknown.
- Product type and what proof the issuer is likely to care about.
- Deadline and whether the merchant can still respond.
- Whether the customer's claim appears valid, partially valid, unsupported, or outside merchant control.

Read `references/dispute-evidence-rules.md` before building the response if the dispute involves reason-code mapping, sensitive evidence, or the accept-versus-challenge decision. Use its platform reason-code crosswalk to translate processor labels into this skill's normalized categories, and mark any uncertain mapping as "verify before submit."

### 2. Decide Whether To Challenge

Recommend accepting or refunding when:

- The customer is owed money under the merchant's own policy.
- Delivery, authorization, service completion, or policy acceptance cannot be shown.
- The dispute amount is too low relative to staff time and processor fees.
- A duplicate charge or unprocessed refund is confirmed.
- The response deadline has passed.

Recommend challenging only when the facts and evidence support the claim being invalid or incomplete. Never convert weak evidence into certainty.

### 3. Run Local Evidence Inventory

For file-backed cases, run:

```bash
python3 chargeback-evidence-pack/scripts/chargeback_evidence_pack.py --case /absolute/path/case.json --evidence-dir /absolute/path/evidence
```

The case JSON may include:

```json
{
  "processor": "Stripe",
  "dispute_id": "dp_123",
  "reason_category": "product_not_received",
  "product_type": "physical",
  "amount": "249.00",
  "currency": "USD",
  "deadline": "2026-05-15",
  "order_id": "10042",
  "charge_date": "2026-04-27",
  "tracking_number": "1Z999",
  "delivered_at": "2026-05-01",
  "avs_result": "pass",
  "cvv_result": "pass",
  "refund_status": "not_refunded",
  "policy_accepted_at": "2026-04-27T10:42:00Z"
}
```

For pasted screenshots or partial notes, apply the same matrix manually and label row counts, file coverage, and deadline checks as incomplete.

### 4. Build The Evidence Pack

Create a response pack with:

- A one-paragraph dispute narrative tied to the exact reason category.
- Evidence index with filename, evidence type, why it matters, and redaction status.
- Missing proof list separated into blockers and nice-to-have support.
- Processor-safe statement of facts: order, payment, fulfillment/access, customer communication, policy acceptance, and refund status.
- Submission checklist, including file limits, deadline, and final review owner.

Prefer facts over argument. Issuers do not need long moral claims; they need proof that addresses the reason code.

### 5. Redact And Limit Disclosure

Remove or avoid:

- Full card PAN, CVV, passwords, API keys, access tokens, private keys, raw cookies, full government IDs, unrelated customer records, and internal fraud tooling details.
- Internal blame, speculation, insults, threat language, and unsupported claims such as "definitely fraud."
- Evidence unrelated to the disputed transaction.

Use processor-safe labels such as "AVS passed," "3DS authenticated," "download event at timestamp," or "carrier delivered to shipping ZIP" instead of exposing raw sensitive logs.

## Output Format

Use this structure unless the user asks for a different format:

```markdown
## Dispute Decision
[Challenge candidate / Accept or refund / Blocked until evidence is added / Deadline risk]

## Case Summary
| Field | Value |
|---|---|
| Processor | ... |
| Reason category | ... |
| Product type | ... |
| Amount | ... |
| Deadline | ... |

## Evidence Index
| Evidence | Status | Source | Why it matters | Redaction |
|---|---|---|---|---|

## Missing Evidence
| Missing item | Severity | How to get it |
|---|---|---|

## Submission Narrative
[Concise bank-facing narrative grounded only in available evidence]

## Submit Checklist
[Deadline, file names, owner review, processor-specific checks]

## Do Not Include
[Secrets, unrelated customer data, unsupported claims, or unsafe details found]
```

## Examples And Acceptance Checks

Positive physical-goods example: "Use $chargeback-evidence-pack on this Shopify chargeback. Customer says product was not received, but UPS shows delivered and AVS passed." The skill should map the case to product-not-received, request or index delivery proof, order receipt, address match, customer communication, refund status, and produce a concise narrative without promising a win.

Positive SaaS example: "A Stripe customer disputed a subscription renewal as cancelled. We have terms acceptance and usage logs." The skill should focus on subscription terms, cancellation history, renewal notices if available, post-charge usage, customer messages, and refund status.

Negative example: "Write a legal threat letter to scare this customer after a chargeback." Do not use this skill for threats or collection tactics; instead explain safe dispute-response boundaries.

Boundary example: "I only know the processor says fraud and the deadline is tomorrow." The skill should produce an urgent evidence request list and a limited draft, but it must not invent authorization, delivery, identity, or policy facts.

## Validation

Smoke-test the bundled fixture:

```bash
python3 chargeback-evidence-pack/scripts/chargeback_evidence_pack.py --case chargeback-evidence-pack/scripts/fixtures/case_product_not_received.json --evidence-dir chargeback-evidence-pack/scripts/fixtures/evidence
```

Expected result: a Markdown report that classifies the dispute as product not received for physical goods, marks delivery/order/policy evidence as present, flags customer communication as missing, notes sensitive-file redaction risks when present, and gives a challenge-candidate decision only after owner review.
