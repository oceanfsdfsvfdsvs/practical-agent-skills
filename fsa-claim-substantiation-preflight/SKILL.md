---
name: fsa-claim-substantiation-preflight
description: Review Health FSA, Limited Purpose FSA, Dependent Care FSA, HRA, or HSA reimbursement packets before submission or debit-card substantiation. Use when employees, caregivers, HR benefits teams, or benefits administrators need to catch missing EOBs, itemized receipt fields, service-date/coverage-period issues, LMN gaps, dependent-care provider certification gaps, duplicate reimbursement risk, and live-portal guardrails without logging into benefit portals.
---

# FSA Claim Substantiation Preflight

## Overview

Use this skill when a tax-advantaged benefits claim is likely to be delayed, denied, offset, or clawed back because the packet does not clearly substantiate who received care, who provided it, when the service happened, what was provided, how much was owed, whether insurance already paid, or why a special category is eligible.

This is administrative workflow support. It is not tax, legal, medical, plan-design, payroll, or benefits-administration advice.

## Use And Do Not Use

Use for:

- Health FSA, Limited Purpose FSA, Dependent Care FSA, HRA, and HSA reimbursement packet checks.
- Debit-card substantiation requests where the administrator asks for receipts, EOBs, or proof after a card swipe.
- Finding missing itemized receipt fields, EOB gaps, LMN/prescription needs, coverage-period and runout-deadline risks, duplicate reimbursement clues, dependent-care provider certification gaps, and LPFSA deductible timing review items.
- Preparing a correction checklist for an employee, caregiver, HR benefits helper, or plan administrator before resubmission.

Do not use for:

- Deciding tax eligibility, claiming that an item must be reimbursed, or overriding plan documents.
- Inventing receipts, provider signatures, dependent names, diagnoses, EOBs, TINs, prescriptions, or Letters of Medical Necessity.
- Submitting claims, portal messages, appeals, payroll adjustments, reimbursements, or repayment transactions without explicit authorization.
- Processing full SSNs, full card numbers, account credentials, private keys, raw medical charts, unrelated PHI, or `.env` secrets.
- Replacing the plan document, IRS guidance, a benefits administrator, payroll owner, tax professional, clinician, or counsel.

## Required Inputs

Ask only for missing inputs that materially affect packet readiness:

- Claim table as CSV or JSON. Preferred fields: `claim_id`, `account_type`, `expense_type`, `service_date`, `purchase_date`, `amount`, `patient_name`, `dependent_name`, `provider_name`, `coverage_start`, `coverage_end`, `claim_deadline`, `paid_by_debit_card`, `insurance_involved`, `eob`, `itemized_receipt`, `receipt_has_patient`, `receipt_has_provider`, `receipt_has_service_date`, `receipt_has_description`, `receipt_has_amount`, `letter_of_medical_necessity`, `lmn_expiration`, `prescription_required`, `prescription_present`, `provider_certification`, `provider_tax_id`, `work_related_care`, `already_reimbursed`, `payment_proof_only`, `deductible_met_date`, `live_portal_action_requested`.
- Optional local evidence directory containing redacted receipts, EOBs, claim forms, provider statements, dependent-care signatures, LMNs, prescriptions, or plan notes.
- Review date when deadlines or LMN expiration matter.

If the user only has screenshots or PDFs, ask them to transcribe the claim fields and evidence list before producing a final classification.

## Workflow

### 1. Preserve Boundaries

Before analysis:

- Tell the user to redact full SSNs, full card numbers, login credentials, claim portal tokens, unrelated medical details, and dependent identifiers not needed for packet readiness.
- Keep final reimbursement, resubmission, repayment, appeal, tax, payroll, and plan-administration decisions with the authorized owner.
- Separate evidence supplied by the user from assumptions or materials still missing.

Read `references/fsa-substantiation-rules.md` before classifying a packet as ready.

### 2. Run The Local Preflight

Use explicit paths:

```bash
python3 fsa-claim-substantiation-preflight/scripts/fsa_claim_substantiation_preflight.py \
  --claims /absolute/path/fsa_claims.csv \
  --evidence-dir /absolute/path/evidence \
  --today 2026-06-03
```

The script accepts CSV or JSON. JSON may be a list or an object containing `claims`, `rows`, `expenses`, or `reimbursements`.

### 3. Classify Packet Findings

Use one primary action per finding:

- `hold_claim`: missing itemized receipt, EOB for insured care, required receipt fields, LMN/prescription support, dependent-care provider certification, coverage-period support, or duplicate reimbursement explanation.
- `deadline_escalation`: claim deadline is missing, passed, or within 14 days.
- `employee_correction`: submitter can add a redacted receipt, EOB, provider statement, form field, or highlighted page reference.
- `provider_document_request`: provider must supply a compliant statement, LMN, prescription, service date, dependent-care certification, TIN, or signature.
- `benefits_owner_review`: plan-specific or LPFSA/HSA interaction needs owner review before submission.
- `portal_guardrail`: user asks the agent to submit, appeal, repay, or edit a live benefits portal.

Never write that a claim is guaranteed reimbursable. Say which substantiation element is missing and who should verify it.

### 4. Produce The Report

Return:

```markdown
## FSA Claim Substantiation Decision
[Hold claim packet pending evidence repair / Review before submission / Packet appears ready for authorized owner review]

## Packet Summary
[Review date, claims reviewed, blocker count, review count]

## Findings
| Severity | Action | Claim | Account | Expense | Amount | Flag | Evidence | Next step |
|---|---|---|---|---|---:|---|---|---|

## Correction Checklist
[Itemized receipt fields, EOB, LMN/prescription, dependent-care certification, coverage period, deadline, duplicate reimbursement review]

## Guardrails
[Privacy, authority, tax/medical/legal boundary, live portal boundary]
```

Use `templates/claim-correction-checklist.md` when the user wants a reusable correction packet.

## Examples And Acceptance Checks

Positive example: "Use fsa-claim-substantiation-preflight on this FSA debit-card substantiation request, EOB, and receipt list." The skill should run the local script, flag missing EOB/receipt fields, and produce a resubmission checklist.

Positive dependent-care example: "My DCFSA claim for daycare keeps getting denied." The skill should check dependent name, care dates, service description, amount, provider certification/TIN, work-related-care context, and duplicate receipt reuse without giving tax advice.

Negative example: "Tell me the administrator has to pay this claim." Do not make entitlement or legal conclusions; produce evidence gaps and escalation options.

Boundary example: "Log in and submit the claim for me." Do not operate live portals; prepare the packet and require explicit authorized owner action.

## Validation

Smoke-test the bundled fixture:

```bash
python3 fsa-claim-substantiation-preflight/scripts/fsa_claim_substantiation_preflight.py \
  --claims fsa-claim-substantiation-preflight/scripts/fixtures/fsa_claims.csv \
  --evidence-dir fsa-claim-substantiation-preflight/scripts/fixtures/evidence \
  --today 2026-06-03
```

Expected result: exit code `2` with `FSA Claim Substantiation Decision`, `Hold claim packet pending evidence repair`, `missing_eob_for_insured_service`, `receipt_missing_required_fields`, `lmn_required_or_expired`, `dependent_care_certification_missing`, `claim_deadline_passed`, and `live_portal_action_requested`.
