# Tax Notice Response Preflight

Review IRS or state tax notices before replying, paying, uploading documents, requesting more time, or escalating.

This skill is for taxpayers, caregivers, preparers, bookkeepers, clinics, and small-business operators who need a structured first pass over confusing tax correspondence without connecting to IRS/state portals. It turns local notice summaries and evidence inventories into a response-readiness report.

## What It Catches

- Past-due or urgent response deadlines.
- CP2000 or underreported-income packets missing response forms, disagreement explanations, income documents, cost-basis support, or delivery proof.
- CP14/balance-due notices where payment proof, transcript/account status, or call notes are missing.
- CP53E/direct-deposit notices that need authenticity, account-status, and bank-owner checks before any bank update.
- Notice-of-deficiency, identity-theft, levy/lien/summons, high-amount, foreign/reporting, or complex basis issues that should route to professional review.
- Missing authorization, proof of prior response, request-for-more-time plan, or packet index.

## Quick Start

```bash
python3 tax-notice-response-preflight/scripts/tax_notice_response_preflight.py \
  --notices tax-notice-response-preflight/scripts/fixtures/notices.csv \
  --evidence tax-notice-response-preflight/scripts/fixtures/evidence.csv \
  --policy tax-notice-response-preflight/scripts/fixtures/policy.json \
  --today 2026-06-15
```

Preferred notice fields:

```text
notice_id, agency, notice_type, tax_year, notice_date, response_due_date,
amount, issue, taxpayer_agrees, response_form_included, requested_action,
delivery_channel, notes
```

Preferred evidence fields:

```text
notice_id, evidence_type, description, present, date, notes
```

## Output

The script produces a Markdown report with:

- Overall response decision.
- Notice summary.
- Row-level findings and next steps.
- Response packet checklist.
- Privacy, authority, and tax/legal guardrails.

## Safety

- This is administrative workflow support, not tax, legal, accounting, investment, or representation advice.
- The script does not call IRS/state portals, upload documents, send fax/mail, make payments, update bank details, or require credentials.
- Do not paste SSNs, full EINs, bank account numbers, IRS online-account credentials, full transcripts, private tax files, tokens, or secrets into public prompts.
- Keep final tax positions, filings, payments, amended returns, and live correspondence with the taxpayer or authorized professional.
