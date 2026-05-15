# Renewal Risk Rules

Use these rules before telling a user that a vendor contract is safe to renew, cancel, or ignore.

## High-Risk Signals

| Signal | Why It Matters | Default Action |
|---|---|---|
| Notice deadline already passed | The customer may have lost cancellation leverage or triggered a renewal term. | Escalate to owner, procurement, and legal. |
| Notice deadline within 14 days | Stakeholders may not have time to confirm usage, authority, and notice method. | Send or escalate notice after authority and clause check. |
| Auto-renewal with missing notice days | Renewal date alone is not enough to calculate the real cancellation deadline. | Read the contract clause before deciding. |
| Missing or stale owner | Calendar reminders fail when the owner leaves or changes role. | Assign accountable owner before vendor negotiation. |
| High spend with uncapped uplift | Missed windows can preserve unfavorable price increases. | Start procurement review and benchmark alternatives. |

## Medium-Risk Signals

- Notice deadline is 15-90 days away.
- Notice recipient or method is missing.
- Last review is older than one year.
- Usage notes mention low adoption, duplicate tools, or planned replacement.
- Renewal term is multi-year or equal to the original commitment period.

## Common Failure Modes

- Tracking only `renewal_date` while ignoring `notice_deadline`.
- Treating an account manager email as valid notice when the contract requires certified mail, portal submission, or legal notice.
- Assuming a SaaS admin dashboard cancellation button satisfies the contract.
- Keeping renewal reminders with a person who has left the company.
- Waiting for the vendor quote before deciding whether to cancel.
- Failing to preserve notice proof and vendor acknowledgement.

## Safe Output Rules

- Say "appears to" when relying on extracted spreadsheet fields rather than contract clauses.
- Do not give legal advice or interpret enforceability.
- Do not contact vendors or send notices unless the user explicitly asks and provides the content and delivery channel.
- Always separate operational urgency from legal conclusion.
