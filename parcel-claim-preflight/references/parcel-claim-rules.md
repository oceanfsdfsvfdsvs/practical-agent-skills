# Parcel Claim Rules

## Claim Type Evidence Matrix

| Claim type | Blocker evidence | Helpful evidence | Common weak packet |
|---|---|---|---|
| `damage` | Proof of value, tracking/scans, damage photos, outer packaging photos, inner packaging photos, original packaging available | Repair estimate, replacement invoice, carrier inspection notes | Only a customer message or a single blurry product photo |
| `loss` | Proof of value, tracking/scans, recipient non-receipt statement | Search/trace case, delivery address match, replacement/refund status | No tracking history or no customer statement |
| `missing_contents` | Proof of value, tracking/scans, outer packaging photos, inner packaging photos, packing slip or contents list | Weight records, warehouse pick record, customer unboxing photos | Box photo without contents/packing evidence |
| `late` | Tracking/scans, proof of value, service-level record | Refund policy, promised delivery date, carrier guarantee terms | Claiming delay without service-level or scan evidence |

## Deadline Triage

- If the deadline has passed, mark the row `hold_claim` unless the user has a carrier-approved exception path.
- If the deadline is within seven days, mark as urgent and produce a minimal packet plan.
- If the deadline is unknown, do not assume the packet is safe; assign an owner to verify the carrier or insurer deadline before upload.

## Packaging And Inspection Rules

- Damage and missing-contents claims are materially weaker when original packaging is unavailable.
- Require both outer packaging and inner packaging evidence when the issue could involve handling, crush damage, wet damage, or missing contents.
- Do not invent inspection results. If the carrier has not inspected the package, say so.

## Value And Coverage Rules

- Compare item value with declared and insured value. If the claimed amount exceeds both, flag `claim_amount_exceeds_declared_or_insured_value`.
- Proof of value should be an invoice, receipt, order record, wholesale cost record, or other owner-approved valuation document.
- Separate reimbursement already issued to the customer from carrier liability; shipping a replacement does not make the carrier claim complete.

## Redaction Rules

Do not upload:

- API keys, tokens, passwords, private keys, `.env` files, or raw system logs containing secrets.
- Full card numbers, CVV, bank account details, unrelated customer records, or government IDs.
- Speculation, insults, or unsupported statements about theft or fraud.

Use fact labels such as "last carrier scan", "recipient non-receipt statement", "outer carton photo", and "invoice value" instead of exposing unrelated private data.
