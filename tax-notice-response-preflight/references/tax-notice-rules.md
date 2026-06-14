# Tax Notice Response Rules

Use these rules as administrative gates. The actual notice text and current official agency instructions win over this generic crosswalk.

## Source-Of-Truth Order

1. The taxpayer's actual notice, including notice type, tax year, date, deadline, response form, address/fax/upload method, and requested action.
2. Official IRS or state agency notice pages and publications.
3. Account transcript, payment history, refund status, or mailed/faxed/uploaded proof supplied by the user.
4. Generic notice-type heuristics in this file.

## Core Gates

- Authenticity gate: verify `.gov` URLs, secure connection, direct navigation rather than QR-only links, matching taxpayer/tax-year facts, and official contact method before sensitive action.
- Deadline gate: identify notice date, response due date, Tax Court or appeal deadline, and whether more-time/status contact is needed.
- Position gate: record whether the taxpayer agrees, disagrees, partly agrees, or is unsure. Do not invent tax positions.
- Evidence gate: map each disagreement to documents, not explanations alone.
- Delivery gate: identify the exact response channel from the notice and preserve upload/fax/mail/call proof.
- Professional-help gate: route high-risk or legally consequential notices to an authorized professional, LITC, TAS, or counsel.

## Notice-Type Heuristics

| Notice clue | Common workflow risk | Minimum packet checks |
|---|---|---|
| CP2000, CP2501, Letter 2030, underreported income, proposed changes | User treats proposal as final bill, amends incorrectly, misses response form, lacks income/payment support, or ignores cost basis. | Notice copy, response form, agree/disagree statement, income forms, basis/expense support when relevant, signed explanation, delivery proof. |
| CP14, balance due, payment mismatch | User pays twice or ignores a notice when payment may be misapplied. | Payment proof, IRS/state account or transcript check, notice copy, call log, payoff/penalty status if taxpayer agrees. |
| CP53E or direct deposit update | User may follow a fake or unexpected banking request, or update account without confirming refund/account status. | `.gov`/secure-site check, direct IRS account navigation, refund expected, bank account in taxpayer/joint name, 30-day window, no phone update promise. |
| CP05, refund hold, identity verification | User sends unrelated documents or misses identity/fraud-review path. | Notice copy, requested documents only, identity-theft clues, refund status, TAS/LITC routing when hardship exists. |
| CP3219A, statutory notice, notice of deficiency, Tax Court | User misses a jurisdictional deadline or sends an informal reply too late. | Exact deadline, envelope/postmark if relevant, prior response proof, professional review, Tax Court/LITC routing. |
| Penalty, late filing/payment, estimated tax | User asks for waiver without proving facts or checking payment/postmark records. | Penalty type, tax period, amount, payment/filing proof, reasonable-cause or first-time-abatement facts for professional review. |
| Levy, lien, summons, passport, criminal investigation | High-consequence enforcement or legal process. | Stop normal preflight and route to qualified professional; do not draft strategy as a generic workflow. |

## High-Risk Flags

- Deadline passed or due within the configured urgent window.
- User asks to update bank details from a link, QR code, email, text, or phone call.
- Notice amount exceeds the professional-review threshold.
- Notice says deficiency, Tax Court, levy, lien, summons, seizure, passport, criminal investigation, fraud, or identity theft.
- User already responded but has no delivery proof, acknowledgement, or status log.
- Response depends on cost basis, foreign reporting, business deductions, credits, crypto, amended returns, or multi-year corrections.

## Packet Checklist

- Notice copy and envelope if deadline/postmark matters.
- Response form, signed and dated when required.
- Plain-language statement of agree/disagree/partial/unsure.
- Evidence mapped to every disputed line.
- Payment proof or refund/account status when money already moved.
- Authorization form or representative contact proof when someone else will speak for the taxpayer.
- Delivery proof: upload confirmation, fax confirmation, certified mail receipt, or call log.
- Follow-up tickler for acknowledgement and next notice.

## Guardrails

- Do not compute final liability, penalty, interest, basis, credit, deduction, or settlement amount.
- Do not tell users to ignore notices or miss deadlines because they believe the agency is wrong.
- Do not submit, upload, fax, mail, pay, call, or update bank information without explicit live-action authorization.
- Do not ask for SSNs, full EINs, bank account numbers, IRS online-account credentials, full transcripts, tokens, or secrets.
