---
name: debt-collection-validation-preflight
description: Preflight debt collection validation and dispute packets before a consumer, caregiver, financial counselor, legal-aid intake helper, or benefits advocate responds to a collector, debt buyer, collection agency, or collection law firm. Use when the user needs to check validation notices, 30-day dispute timing, collector identity, original-creditor requests, amount/itemization gaps, not-mine or paid-debt evidence, continued collection after a timely dispute, time-barred-debt review, redaction risks, and owner next steps without making live payments, filing complaints, or giving legal conclusions.
---

# Debt Collection Validation Preflight

## Overview

Use this skill to turn debt collection letters, call notes, validation notices, payment records, credit-report screenshots, and dispute drafts into a validation-readiness report. The goal is an evidence and deadline gate before the user sends a debt validation request, written dispute, original-creditor request, complaint packet, or owner-reviewed response. This is not legal advice, debt settlement advice, credit repair, or a guarantee that a collector will stop collection.

## Use And Do Not Use

Use for:

- Consumers, caregivers, financial counselors, benefits advocates, and legal-aid intake helpers preparing local review packets.
- Collection letters, texts, emails, voicemails, lawsuits threatened by collectors, debt-buyer notices, medical or consumer debt collection contacts, and collection-law-firm letters before response.
- Cases involving "not mine," identity theft, paid or settled debt, wrong amount, unknown collector, missing validation notice, original-creditor request, old or possibly time-barred debt, continued collection after a written dispute, or credit-reporting threats.
- Local file review where evidence is in CSV rows, pasted notes, PDFs, screenshots, letters, receipts, or mailing records.

Do not use for:

- Live collector calls, portal submissions, complaint filing, payment authorization, settlement negotiation, lawsuit defense strategy, or jurisdiction-specific legal conclusions.
- Advising a user to ignore a court summons, admit debt, restart a limitations period, make payment, or dispute accurate debt in bad faith.
- Inventing dates, collector addresses, account numbers, debt ownership, validation notices, mailing receipts, or proof of payment.
- Uploading full SSNs, full ID scans, full account numbers, bank credentials, full card numbers, private keys, tokens, `.env` files, or unrelated consumer records.

## Required Inputs

Ask only for missing inputs that materially affect the decision:

- Contact identity: collector name, mailing address, phone/email if relevant, current creditor, original creditor if known, masked account number, and debt type.
- Timeline: first contact date, validation notice date, date received, written dispute/request sent date, collector response date, and any court/credit/reporting deadline.
- Validation notice details: amount, itemization date, dispute instructions, current creditor, original-creditor rights, tear-off or reply method, and collector address.
- Consumer position: unknown debt, not mine, identity theft, paid/settled, wrong amount, already disputed, old debt, medical billing issue, or settlement/payment question.
- Evidence: collector letter, envelope, validation notice, certified-mail receipt, payment/settlement proof, insurance/EOB or billing records, identity-theft report, account mismatch evidence, original-creditor documents, collector verification response, credit-report page, and call log.

## Workflow

### 1. Classify The Collection Issue

Normalize each case as `unknown_debt`, `not_mine`, `identity_theft`, `paid_or_settled`, `wrong_amount`, `old_debt`, `medical_collection`, `original_creditor_request`, `continued_collection_after_dispute`, or `mixed`. Identify whether the immediate packet is a validation request, dispute, original-creditor request, evidence repair, complaint escalation draft, or legal owner review.

Read `references/debt-collection-validation-rules.md` when the case involves validation notices, 30-day timing, written disputes, continued collection after dispute, old debt, medical debt, lawsuits, or complaint escalation.

### 2. Run Local Preflight When Files Exist

For CSV-backed batches, run:

```bash
python3 debt-collection-validation-preflight/scripts/debt_collection_validation_preflight.py \
  --cases /absolute/path/debt_collection_cases.csv \
  --evidence-dir /absolute/path/evidence \
  --today 2026-06-17
```

Use the script output as the evidence inventory. For pasted notes or screenshots, apply the same matrix manually and mark file coverage as incomplete.

### 3. Repair The Packet Before Sending

Prioritize blockers:

- Collector name, mailing address, current creditor, or amount is missing from the notice.
- No validation notice exists, or the user cannot identify the notice that starts the dispute window.
- The 30-day written dispute window is close and no dated response packet or mailing plan exists.
- The user says "not mine," "identity theft," "paid," or "wrong amount" without supporting evidence.
- The user sent a timely written dispute but collector activity appears to continue before verification.
- The user asks the agent to pay, call, submit a live complaint, or respond to a lawsuit without owner/legal review.

Separate "prepare a narrow preservation/dispute packet now" from "evidence still missing." Do not turn weak facts into legal certainty.

### 4. Produce The Validation-Readiness Output

Use `templates/validation-readiness-report.md` for final reports. Include:

- Hold/review/ready decision.
- Timeline and validation-window status.
- Notice and collector identity matrix.
- Evidence gaps and repair actions.
- Continued-collection, old-debt, lawsuit, credit-reporting, and live-action flags.
- Redaction and owner-review guardrails.

## Output Format

```markdown
## Debt Collection Validation Decision
[Ready for owner review / Review before send / Hold validation packet pending evidence repair]

## Case Summary
| Case | Collector | Current Creditor | Issue Type | Decision |
|---|---|---|---|---|

## Timeline
| Case | First Contact | Notice Received | Dispute Due | Dispute Sent | Status |
|---|---|---|---|---|---|

## Evidence Matrix
| Case | Evidence | Status | Source | Repair action |
|---|---|---|---|---|

## Blockers
| Case | Blocker | Why it matters | Next action |
|---|---|---|---|

## Review Flags
| Case | Flag | Why it matters | Next action |
|---|---|---|---|

## Packet Notes
[Concise facts, dates, disputed portions, requested validation, original-creditor request if applicable, and attachments; no threats or unsupported claims]

## Do Not Upload
[Full SSNs, full IDs, bank/card credentials, full account numbers, private keys, tokens, or unrelated records]
```

## Examples And Acceptance Checks

Positive example: "Use $debt-collection-validation-preflight on this collection letter, envelope, call log, and payment receipt before I respond." The skill should check the validation notice, compute the dispute timing, require proof for paid/not-mine claims, and flag live-action risks.

Positive batch example: "Review these 40 collection letters from a legal-aid intake clinic." The skill should produce case-level hold/review/ready decisions and identify which evidence is missing.

Negative example: "Write a scary letter that makes the collector delete everything." Do not make guaranteed deletion or harassment claims. Produce a fact-grounded validation packet or explain why it is not ready.

Boundary example: "I got sued and the answer is due Friday." Do not draft legal strategy as a substitute for counsel. Preserve facts, flag the court deadline, and route to legal owner review.

## Validation

Smoke-test the bundled fixture:

```bash
python3 debt-collection-validation-preflight/scripts/debt_collection_validation_preflight.py \
  --cases debt-collection-validation-preflight/scripts/fixtures/debt_collection_cases.csv \
  --evidence-dir debt-collection-validation-preflight/scripts/fixtures/evidence \
  --today 2026-06-17
```

Expected result: a Markdown report with `Debt Collection Validation Decision`, at least one `Hold validation packet pending evidence repair`, and flags such as `validation_notice_missing`, `timely_dispute_window_at_risk`, `collection_after_timely_dispute_without_verification`, `collector_identity_or_address_missing`, and `live_action_requested`.
