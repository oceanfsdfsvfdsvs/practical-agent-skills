# Dispute Evidence Rules

Use these rules to keep chargeback responses reason-coded, evidence-backed, and safe to submit. Processor and card-network rules change; verify platform-specific fields and deadlines before final submission.

## Platform Reason-Code Crosswalk

Use this crosswalk as a starting point, then verify the current processor notice before submission. Processor labels change, and the notice text should win over a generic mapping.

| Normalized category | Stripe examples | PayPal examples | Shopify Payments examples | Adyen examples | Square examples |
|---|---|---|---|---|---|
| product_not_received | `product_not_received` | Item not received | Product not received | Goods/services not received | Goods/services not received |
| fraudulent_or_no_authorization | `fraudulent` | Unauthorized transaction | Fraudulent | Fraud / No cardholder authorization | Fraudulent payment |
| duplicate | `duplicate` | Duplicate payment | Duplicate | Duplicate processing | Duplicate |
| credit_not_processed | `credit_not_processed` | Credit not processed / refund issue | Credit not processed | Credit not processed | Credit not processed |
| product_unacceptable_or_not_as_described | `product_unacceptable` | Significantly not as described | Product unacceptable / not as described | Not as described / defective | Product not as described |
| cancelled_subscription | `subscription_canceled` | Canceled recurring payment | Subscription canceled | Cancelled recurring transaction | Canceled recurring payment |
| digital_goods_or_service | Claim-text derived | Digital goods / intangible service dispute | Digital goods or service claim | Digital service dispute | Digital goods/service dispute |

Mapping rules:

- If the processor notice gives both a network code and plain-language claim, record both.
- If the label is broad, classify by the customer's claim text and evidence needed, not by the platform name alone.
- If a marketplace wraps the payment processor, preserve the marketplace case ID and processor dispute ID separately.
- If the customer claim mixes categories, choose the category that determines the strongest required evidence and list secondary evidence needs.

## Accept Versus Challenge

Accept or refund when any of these are true:

- The merchant's refund, cancellation, replacement, or service policy supports the customer.
- The product or service was not delivered, access was not granted, or the merchant cannot prove completion.
- Duplicate billing, wrong amount, or unprocessed refund is confirmed.
- Evidence depends on guesses, unsupported staff memory, or unverifiable claims.
- The deadline has passed or the processor no longer accepts evidence.
- The charge amount is lower than the likely dispute fee and staff time, unless repeat fraud or account risk justifies response.

Challenge only when available evidence directly answers the reason category.

## Reason-Code Evidence Matrix

| Reason category | Core evidence | Helpful support | Common failure |
|---|---|---|---|
| product_not_received | Order receipt, fulfillment record, tracking number, carrier delivery page, shipping address match, refund status | Signature, delivery photo, customer acknowledgement, prior successful deliveries | Arguing the customer is dishonest without proving delivery to the right destination |
| fraudulent_or_no_authorization | AVS/CVV/3DS result, customer account history, prior relationship, IP/device match, delivery or usage evidence | Account login history, saved payment method record, email match, signed authorization | Exposing raw card data or assuming AVS alone proves authorization |
| duplicate | Both charge IDs, timestamps, amounts, order IDs, settlement records, refund or reversal status | Cart/session logs, invoice history | Treating two similar orders as one without proving duplicate billing |
| credit_not_processed | Refund policy, refund request timeline, refund status, return tracking, customer communication | Processor refund ID, return inspection notes | Claiming "no refund owed" without policy acceptance or condition evidence |
| product_unacceptable_or_not_as_described | Product listing/description at purchase time, photos/specs, fulfillment record, support timeline, remediation offer | Quality-control notes, replacement offer, usage evidence | Ignoring partial validity of the complaint or overloading with unrelated catalog material |
| cancelled_subscription | Terms, renewal notice if available, cancellation path, cancellation timestamp, billing history, usage after charge | Account email match, support ticket timeline | Missing proof that the customer had a clear cancellation path or accepted renewal terms |
| digital_goods_or_service | Access grant, login/download/usage logs, IP/device/account match, terms acceptance, service completion record | Timestamped screenshots, project deliverables, attendee/check-in logs | Submitting raw private logs instead of summarized event evidence |
| unknown | Processor notice, customer claim text, transaction summary, product type, deadline | Any available order, delivery, access, policy, and communication evidence | Drafting a generic narrative before the real claim is identified |

## Product-Type Additions

Physical goods:

- Carrier tracking and delivery page.
- Shipping address and billing/customer account match.
- Signature, delivery photo, pickup confirmation, or proof of handoff when available.

Digital goods:

- Access grant timestamp, download, license activation, login, or usage event.
- Customer account email, IP/device consistency, terms acceptance, and refund policy.
- Avoid raw session tokens, complete IP histories, cookies, or internal abuse scores.

SaaS or subscription:

- Checkout terms, renewal/cancellation policy, renewal notice if available, usage after charge, cancellation timestamp, and support history.
- Show whether service remained available and whether the customer used it after the disputed charge.

Services or appointments:

- Booking confirmation, attendance/check-in, deliverables, completion notes, signed acceptance, or customer approval.
- Show scope, delivery date, and remediation offers when quality is disputed.

Marketplace or dropship:

- Seller fulfillment evidence, platform order record, carrier proof, buyer messages, and marketplace policy.
- Do not submit supplier-private invoices unless the processor specifically requests them and they are redacted.

## Redaction Rules

Never include:

- CVV, full PAN, passwords, API keys, access tokens, private keys, raw cookies, private SSH keys, or webhook secrets.
- Full government IDs, unrelated customer records, medical details, or internal risk-model details.
- Private customer support conversations outside the disputed transaction.

Prefer:

- "AVS passed" instead of full billing address screenshots when unnecessary.
- "3DS authenticated" instead of raw authentication traces.
- "Customer downloaded file at 2026-05-01 14:03 UTC" instead of raw logs with tokens.
- Cropped screenshots and PDF exports that only show transaction-relevant fields.

## Narrative Rules

Write for the issuing bank:

- State the transaction, product/service, reason category, and the exact facts that answer that category.
- Keep the narrative short and cite evidence labels or filenames.
- Acknowledge refunds, replacements, partial failures, or policy exceptions honestly.
- Avoid insults, speculation, "fraudster," "scam," "obviously," or emotional language.

Useful structure:

1. The customer placed order `[order_id]` for `[product/service]` on `[date]`.
2. The disputed claim is `[reason]`.
3. Available evidence shows `[delivery/access/authorization/policy/refund fact]`.
4. The attached evidence includes `[top 3 evidence labels]`.
5. Based on these facts, the merchant requests reversal of the dispute.

## Failure Modes Checklist

- Missing the deadline while searching for perfect evidence.
- Submitting generic screenshots that do not tie to the order ID, customer, or date.
- Treating a fraud reason code like a delivery dispute, or a delivery reason code like an authorization dispute.
- Hiding a prior refund, replacement promise, or service failure.
- Including secrets or raw logs in a processor upload.
- Writing a long complaint instead of a reason-coded proof packet.
- Failing to keep a copy of the submitted evidence and timestamp.
