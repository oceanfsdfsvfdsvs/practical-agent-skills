---
name: medical-bill-dispute-preflight
description: Review patient medical bills, itemized statements, and insurance EOB exports for mismatches, missing EOBs, duplicate charges, surprise-billing clues, denial/appeal triggers, and financial-assistance next steps before a patient pays or escalates a billing dispute.
---

# Medical Bill Dispute Preflight

## Overview

Use this skill when a patient, caregiver, benefits advocate, HR benefits team, or billing helper needs a local-first review of medical bills against insurance explanations of benefits (EOBs). The goal is to separate "likely payable," "do not pay yet," "ask for itemized detail," "provider/insurer reconciliation," "appeal review," and "No Surprises Act or state complaint review" before money is paid or an account is sent to collections.

This is administrative and financial workflow support. It is not medical, legal, tax, credit-repair, or insurance-coverage advice.

## Use And Do Not Use

Use for:

- Hospital, physician, lab, imaging, anesthesia, emergency, urgent-care, or outpatient bills.
- Itemized statements, superbills, claims exports, and EOBs from insurance portals.
- Finding mismatches between bill balance and EOB patient responsibility.
- Identifying lines that need itemized bills, corrected claims, insurer reprocessing, appeal review, or financial-assistance screening.
- Preparing a call script, dispute packet checklist, or written reconciliation request.

Do not use for:

- Medical necessity, diagnosis, clinical coding, legal liability, or guaranteed appeal outcomes.
- Deciding that a valid debt does not exist.
- Advising users to ignore bills, misrepresent facts, or delay urgent medical care.
- Uploading uncensored PHI, full insurance IDs, SSNs, payment card numbers, tokens, secrets, or private legal advice.
- Sending complaints, appeals, payments, or portal messages without explicit user authorization.

## Required Inputs

Ask only for missing inputs that materially affect the result:

- Local bill export or typed table. Preferred fields: `bill_id`, `provider`, `service_date`, `cpt`, `description`, `charge`, `patient_balance`, `insurance_processed`, `network_status`, `facility_type`, `itemized`, `notes`.
- Local EOB export when insured. Preferred fields: `claim_id`, `provider`, `service_date`, `cpt`, `description`, `allowed_amount`, `plan_paid`, `patient_responsibility`, `denial_code`, `denial_reason`, `network_status`.
- Optional policy JSON with `balance_tolerance`, `surprise_facility_types`, and `financial_assistance_balance_over`.
- The review date if deadlines matter.

If the user only has PDFs or screenshots, first ask them to transcribe or export the key line items. Do not infer final amounts from blurry images.

## Workflow

### 1. Preserve Privacy And Authority Boundaries

Before analysis:

- Tell the user to redact SSNs, full member IDs, payment card data, account login credentials, and unrelated clinical notes.
- Capture bill source, date of service, provider, itemized status, insurance status, EOB availability, billed amount, and patient balance.
- Keep final payment, appeal, complaint, and legal decisions with the patient or authorized benefits owner.

Read `references/medical-bill-dispute-rules.md` before classifying a charge as safe to pay.

### 2. Run The Local Preflight

Use explicit paths:

```bash
python3 medical-bill-dispute-preflight/scripts/medical_bill_dispute_preflight.py \
  --bills /absolute/path/medical_bills.csv \
  --eob /absolute/path/eob.csv \
  --policy /absolute/path/policy.json
```

The script accepts CSV or JSON. JSON may be a list or an object containing `bills`, `rows`, `claims`, or `eob`.

### 3. Classify Billing Exceptions

Use one primary action per finding:

- `hold_payment`: bill has no matching EOB, patient balance exceeds EOB responsibility, duplicate charge appears, or insurance was expected but not processed.
- `request_itemized_bill`: bill lacks CPT/HCPCS, service date, itemized detail, or provider-specific line items.
- `provider_insurer_reconciliation`: provider bill and EOB disagree, claim looks miscoded, or corrected claim/reprocessing is needed.
- `appeal_review`: EOB denial, noncovered line, or missing information code should be reviewed against plan appeal instructions.
- `no_surprises_review`: out-of-network emergency/facility-related clue or balance bill may fit federal or state surprise-billing rules.
- `financial_assistance_review`: balance is unaffordable or high enough to ask for charity care, self-pay, or payment-plan screening.
- `payable_after_archive`: no material mismatch, user has EOB, and the patient responsibility equals or exceeds the bill balance within tolerance.

Never say "you legally do not owe this" unless the user provides a final written determination from the insurer, provider, regulator, or counsel.

### 4. Produce The Dispute Preflight Report

Return:

```markdown
## Medical Bill Dispute Decision
[Hold payment pending reconciliation / Review before paying / No material billing exceptions found]

## Exception Summary
[Bills reviewed, EOB rows reviewed, hold count, review count]

## Billing Exceptions
| Risk | Action | Row | Provider | Service date | CPT | Balance | Flag | Evidence | Next step |
|---|---|---:|---|---|---|---:|---|---|---|

## Dispute Packet Checklist
[Itemized bill, EOB, corrected claim request, appeal instructions, call log, complaint path]

## Guardrails
[Privacy, authority, medical/legal boundary, collections caveat]
```

Use `templates/dispute-packet-checklist.md` when the user wants a reusable packet.

## Examples And Acceptance Checks

Positive example: "Use medical-bill-dispute-preflight on this ER bill and my insurance EOB before I pay." The skill should compare patient responsibility, hold mismatched lines, request itemized details, and suggest the right billing-office or insurer next step.

Positive caregiver example: "My parent has a hospital statement, separate anesthesiology bill, and no EOB yet." The skill should flag missing EOBs and separate facility/professional bills without telling the user to ignore the debt.

Negative example: "Tell me this bill is illegal." Do not make legal conclusions; classify evidence gaps and escalation options.

Boundary example: "The procedure should have been covered." Do not decide medical necessity; route denial lines to appeal review and ask for plan appeal instructions.

## Validation

Smoke-test the bundled fixture:

```bash
python3 medical-bill-dispute-preflight/scripts/medical_bill_dispute_preflight.py \
  --bills medical-bill-dispute-preflight/scripts/fixtures/medical_bills.csv \
  --eob medical-bill-dispute-preflight/scripts/fixtures/eob.csv \
  --policy medical-bill-dispute-preflight/scripts/fixtures/policy.json
```

Expected result: exit code `2` with `Medical Bill Dispute Decision`, `Hold payment pending reconciliation`, `balance_exceeds_eob_patient_responsibility`, `missing_eob_or_unprocessed_insurance`, `request_itemized_bill`, `no_surprises_review`, and `appeal_review`.
