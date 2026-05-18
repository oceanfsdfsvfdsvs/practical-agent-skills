---
name: vendor-bank-change-preflight
description: Review vendor bank-account change requests for payment-redirection, vendor impersonation, and audit-trail risk before AP updates bank details or releases ACH/wire/check payments. Use when finance, accounting, procurement, founders, or operators need a local-first callback and evidence check without connecting to an ERP, bank portal, or supplier portal.
---

# Vendor Bank Change Preflight

## Overview

Use this skill to turn vendor bank-change requests into a reviewable payment-redirection risk report. The goal is to stop unsafe bank-detail updates before money moves while preserving enough evidence for AP, finance, or procurement reviewers to approve, hold, or escalate the request.

## Use And Do Not Use

Use for:

- Vendor bank-account, routing, ACH, wire, or remittance-detail change requests.
- First payments to new vendors, high-value invoice payments, or urgent bank-change emails.
- AP exports, vendor-master exports, intake-form CSVs, or manually assembled request packets.
- Reviewing callback source, dual approval, email-domain mismatch, bank country mismatch, reused bank details, and evidence completeness.
- Producing an operational hold/secondary-verification report for AP reviewers.

Do not use for:

- Automatically changing vendor records, releasing payments, or logging into bank/ERP systems.
- Legal, insurance, recovery, or fraud determinations. Label findings as payment-redirection risk unless confirmed by the user.
- Replacing bank validation, confirmation-of-payee, sanctions screening, KYC, or qualified finance controls.
- Storing account numbers, tax IDs, credentials, or private vendor documents in prompts or fixtures.

## Required Inputs

Ask only for missing inputs that materially affect the review:

- Bank-change request export path, or a pasted sample if file access is unavailable.
- Optional vendor-master export with trusted email domain, trusted phone availability, current routing/account last4, and vendor country.
- Policy thresholds: dual approval requirement, callback source rules, high-value payment threshold, new-vendor window, and first-payment handling.
- Output preference: Markdown report, copied table, or saved file.

Preferred request fields:

```csv
request_id,vendor_name,vendor_id,requester_email,request_channel,requested_at,effective_date,old_routing,old_account_last4,new_routing,new_account_last4,new_bank_country,vendor_country,amount_at_risk,invoice_id,callback_status,callback_contact_source,callback_performed_by,approver_count,bank_letter_present,w9_present,first_payment,days_since_vendor_created,memo
```

## Workflow

### 1. Preserve The Payment-Control Boundary

Before classifying risk, capture:

- Who requested the change and through which channel.
- Which vendor record, invoice, and payment exposure are affected.
- Old and new routing/account last4 values only when the user supplies them.
- Callback status, callback source, reviewer names, and approval count.
- Evidence artifacts such as bank letter, W-9/tax record, contract contact, prior invoice, or vendor-master contact.

Do not ask for full bank account numbers, tax IDs, secrets, or live bank/ERP access.

### 2. Run The Local Preflight

Use explicit paths:

```bash
python3 vendor-bank-change-preflight/scripts/vendor_bank_change_preflight.py \
  --requests /absolute/path/bank_change_requests.csv \
  --vendor-master /absolute/path/vendor_master.csv
```

The script accepts CSV or JSON. JSON may be a list of request objects or an object containing `requests`, `bank_changes`, or `rows`.

### 3. Classify Findings

Use one primary action:

- `hold_change`: high-risk signal exists; do not update bank details or release payment until independent verification is complete.
- `secondary_verification`: moderate risk; require a second reviewer and trusted-contact callback.
- `document_and_monitor`: low risk but evidence or artifacts are incomplete.
- `ready_with_evidence`: no material red flags in the supplied fields.

Use one risk level:

- `high`: missing/incomplete callback, callback used the request email or attachment, lookalike email domain, reused bank details, or other strong payment-redirection signal.
- `medium`: bank country mismatch, email-domain mismatch, insufficient approval, first payment, new vendor, urgency language, same-week effective date, or high payment exposure.
- `low`: missing non-blocking artifact, documentation gap, or no material red flag.

Never recommend updating bank details when `hold_change` rows remain unresolved.

### 4. Produce The Review Report

Return:

```markdown
## Bank Change Decision
[Hold bank-change updates / Secondary verification required / No high-risk signal found]

## Request Findings
| Risk | Action | Row | Request | Vendor | Amount at risk | Flags | Reviewer next step |
|---|---:|---|---|---:|---|---|

## Controls Checked
[Callback source, dual approval, domain mismatch, bank country, reused bank details, new vendor, evidence packet]

## Safe Release Steps
[Rows to hold, rows to verify, evidence to archive, rerun instruction]

## Open Questions
[Only questions that affect payment-control safety]
```

Use `templates/bank-change-review.md` when the user asks for a reusable AP review artifact.

### 5. Apply Guardrails Before Advising Release

Do not advise release until:

- Callback is complete through a trusted source that was not supplied in the request.
- At least two internal approvers have reviewed high-value or bank-detail changes.
- New vendors, first payments, and same-week effective dates have secondary review.
- Email-thread continuity is not treated as proof of legitimacy.
- Evidence is archived with the vendor record outside the prompt transcript.

## Examples And Acceptance Checks

Positive example: "Use $vendor-bank-change-preflight on these three ACH change requests before AP updates NetSuite." The skill should run the script, catch callback and domain issues, and produce hold/review rows.

Positive vendor-master example: "Cross-check this bank change against our vendor master." The skill should compare trusted domains, country, current bank details, and reused bank details.

Negative example: "Just update the routing number." Do not modify live systems; produce a review report only.

Boundary example: "I pasted one request from an email." Produce sample-limited observations and ask for vendor-master/contact evidence before giving a safe-update recommendation.

## Validation

Smoke-test the bundled fixture:

```bash
python3 vendor-bank-change-preflight/scripts/vendor_bank_change_preflight.py \
  --requests vendor-bank-change-preflight/scripts/fixtures/bank_change_requests.csv \
  --vendor-master vendor-bank-change-preflight/scripts/fixtures/vendor_master.csv
```

Expected result: a Markdown report with `Bank Change Decision`, at least one `hold_change`, at least one `secondary_verification`, `lookalike_email_domain`, and `bank_account_reused_by_another_vendor`.
