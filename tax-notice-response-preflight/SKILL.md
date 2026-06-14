---
name: tax-notice-response-preflight
description: Preflight IRS or state tax notice response packets before a taxpayer, tax preparer, bookkeeper, clinic, or caregiver replies, pays, uploads documents, requests more time, or escalates. Use when the user has CP2000, CP14, CP53E, CP05, notice-of-deficiency, refund hold, balance-due, identity-theft, payment-mismatch, underreported-income, penalty, or confusing tax correspondence and needs deadline, authenticity, evidence, routing, privacy, and professional-help gates without live filing or tax advice.
---

# Tax Notice Response Preflight

## Overview

Use this skill when a taxpayer, caregiver, preparer, bookkeeper, Low Income Taxpayer Clinic intake helper, or small-business operator needs a local-first review of tax notices before responding. The goal is to separate "reply-ready," "hold pending evidence repair," "professional review needed," "authenticity check needed," and "deadline escalation" without logging into IRS/state portals or giving tax advice.

This is administrative workflow support. It is not legal, tax, accounting, investment, identity-theft recovery, or IRS/state representation advice.

## Use And Do Not Use

Use for:

- IRS or state notices involving underreported income, proposed changes, balance due, refund holds, direct deposit updates, penalty notices, payment mismatch, missing forms, identity-theft clues, or notice-of-deficiency deadlines.
- Checking whether the response packet includes the notice, response form, signed statement, payment proof, income documents, amended-return materials, identity-theft affidavit, authorization, mailing/fax/upload proof, and call log.
- Preparing a response checklist, call script, packet index, or owner handoff.
- Screening for urgent escalation to a tax professional, LITC, TAS, or authorized representative.

Do not use for:

- Calculating final tax liability, penalties, interest, basis, credits, deductions, or settlement terms.
- Telling the user to ignore a notice, hide income, fabricate documents, or submit false statements.
- Filing, uploading, faxing, mailing, paying, calling, or changing bank details unless the user explicitly asks and remains in control.
- Handling criminal investigation, summons, levy, lien, passport, seizure, or Tax Court litigation strategy beyond routing to professional help.
- Storing SSNs, full EINs, bank account numbers, IRS online-account credentials, full transcript data, or private tax files in prompts or fixtures.

## Required Inputs

Ask only for missing inputs that materially affect the result:

- Notice table or typed summary. Preferred fields: `notice_id`, `agency`, `notice_type`, `tax_year`, `notice_date`, `response_due_date`, `amount`, `issue`, `taxpayer_agrees`, `response_form_included`, `requested_action`, `delivery_channel`, `notes`.
- Evidence inventory table. Preferred fields: `notice_id`, `evidence_type`, `description`, `present`, `date`, `notes`.
- Optional policy JSON with `urgent_days`, `professional_review_amount`, and notice-type thresholds.
- Review date if deadlines matter.

If the user only has PDFs or screenshots, ask them to transcribe the notice type, date, response deadline, tax year, amount, requested action, response method, and exact disagreement reason. Do not infer deadlines from unclear images.

## Workflow

### 1. Preserve Privacy And Authority Boundaries

Before analysis:

- Tell the user to redact SSNs, full EINs, bank account numbers, IRS online-account login details, transcript control numbers, and unrelated tax documents.
- Keep final tax positions, payments, amended returns, account changes, and filings with the taxpayer or authorized professional.
- Treat the notice text as the source of truth over generic notice-type rules.

Read `references/tax-notice-rules.md` before classifying a response as reply-ready.

### 2. Run The Local Preflight

Use explicit paths:

```bash
python3 tax-notice-response-preflight/scripts/tax_notice_response_preflight.py \
  --notices /absolute/path/notices.csv \
  --evidence /absolute/path/evidence.csv \
  --policy /absolute/path/policy.json \
  --today 2026-06-15
```

The script accepts CSV or JSON. JSON may be a list or an object containing `notices`, `rows`, `cases`, `evidence`, or `documents`.

### 3. Classify Notice Response Risk

Use one primary action per notice:

- `escalate_deadline`: response due date is passed or within the urgent window.
- `verify_authenticity`: scam clues, unexpected bank-update request, QR/link-only flow, or mismatch between notice and account/payment facts.
- `repair_evidence_packet`: response form, signature, notice copy, disagreement explanation, income/payment documents, proof of prior response, or delivery proof is missing.
- `professional_review`: notice of deficiency, high amount, Tax Court deadline, levy/lien/summons clue, identity-theft clue, or complex basis/credit/foreign/reporting issue.
- `request_more_time_or_status`: user cannot meet the notice deadline, previously responded without acknowledgement, or IRS/state account status is unclear.
- `reply_ready_after_owner_review`: no material blockers remain and the response method, evidence, signature, and proof-of-delivery plan are present.

Never say "the IRS is wrong" or "you do not owe this." Say what evidence is present, what is missing, and who should decide.

### 4. Produce The Preflight Report

Return:

```markdown
## Tax Notice Response Decision
[Deadline escalation / Hold response pending evidence repair / Professional review needed / Authenticity check needed / Reply-ready after owner review]

## Notice Summary
[Notices reviewed, urgent count, missing evidence count, professional-review count]

## Response Findings
| Risk | Action | Notice | Agency | Type | Tax year | Due date | Amount | Flags | Next step |
|---|---|---|---|---|---:|---|---:|---|---|

## Packet Checklist
[Notice copy, response form, signed explanation, evidence, authorization, delivery proof, call log]

## Guardrails
[Privacy, authority, tax/legal boundary, live-action boundary]
```

Use `templates/response-packet-checklist.md` when the user wants a reusable packet.

## Examples And Acceptance Checks

Positive CP2000 example: "Use tax-notice-response-preflight on this CP2000 and my brokerage 1099-B/cost-basis evidence before I reply." The skill should check the response deadline, response form, whether the user agrees, supporting documents, delivery method, and whether a tax professional should review basis calculations.

Positive CP53E example: "I received a CP53E asking me to update bank info, but I did not expect a refund." The skill should verify authenticity and account-status gates before any bank update.

Positive CP14 example: "The IRS says I owe, but my payment cleared." The skill should request payment proof, transcript/account status, notice copy, and call log before recommending packet readiness.

Negative example: "Tell me how much tax I owe from this CP2000." Do not compute final liability; produce evidence gaps and routing.

Boundary example: "Upload this response for me." Do not upload or submit; provide packet and live-action checklist only.

## Validation

Smoke-test the bundled fixture:

```bash
python3 tax-notice-response-preflight/scripts/tax_notice_response_preflight.py \
  --notices tax-notice-response-preflight/scripts/fixtures/notices.csv \
  --evidence tax-notice-response-preflight/scripts/fixtures/evidence.csv \
  --policy tax-notice-response-preflight/scripts/fixtures/policy.json \
  --today 2026-06-15
```

Expected result: exit code `2` with `Tax Notice Response Decision`, `Hold response pending evidence repair`, `cp2000_supporting_documents_missing`, `cp53e_authenticity_or_account_status_review`, `payment_proof_missing`, `deadline_passed_or_imminent`, and `professional_review_recommended`.
