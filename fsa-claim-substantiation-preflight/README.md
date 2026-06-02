# FSA Claim Substantiation Preflight

Review Health FSA, Limited Purpose FSA, Dependent Care FSA, HRA, or HSA claim packets before submission, resubmission, or debit-card substantiation.

This skill is for employees, caregivers, HR benefits teams, and benefits administrators who need a local-first way to catch documentation gaps that commonly delay or deny claims. It turns claim tables and redacted evidence files into a blocker-focused packet readiness report.

## What It Catches

- Missing EOBs for insured care.
- Generic payment proofs used instead of itemized receipts.
- Receipts missing patient/dependent name, provider, service date, description, or amount.
- Service dates outside the coverage period or after the claim deadline.
- LMN, prescription, or plan-specific support gaps.
- Dependent-care provider certification, TIN, signature, or work-related-care context gaps.
- LPFSA deductible timing review items.
- Duplicate reimbursement or repeated receipt reuse.
- Unsafe requests to submit live portal actions.

## Quick Start

```bash
python3 fsa-claim-substantiation-preflight/scripts/fsa_claim_substantiation_preflight.py \
  --claims fsa-claim-substantiation-preflight/scripts/fixtures/fsa_claims.csv \
  --evidence-dir fsa-claim-substantiation-preflight/scripts/fixtures/evidence \
  --today 2026-06-03
```

Input may be CSV or JSON. Preferred fields:

```text
claim_id, account_type, expense_type, service_date, purchase_date, amount,
patient_name, dependent_name, provider_name, coverage_start, coverage_end,
claim_deadline, paid_by_debit_card, insurance_involved, eob,
itemized_receipt, receipt_has_patient, receipt_has_provider,
receipt_has_service_date, receipt_has_description, receipt_has_amount,
letter_of_medical_necessity, lmn_expiration, prescription_required,
prescription_present, provider_certification, provider_tax_id,
work_related_care, already_reimbursed, payment_proof_only,
deductible_met_date, live_portal_action_requested
```

## Output

The script produces a Markdown report with:

- Overall claim-packet decision.
- Claim and blocker summary.
- Row-level findings with flags and next steps.
- Correction checklist.
- Privacy, authority, and tax/medical/legal guardrails.

## Runtime Notes

- Codex/OpenAI: use `SKILL.md` and `agents/openai.yaml`.
- Claude Code: use `.claude/skills/fsa-claim-substantiation-preflight/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.
- Hermes: see `hermes/README.md`; native Hermes packaging is blocked until a current local spec is available.

## Safety

- This is administrative workflow support, not tax, legal, medical, plan-design, payroll, or benefits-administration advice.
- The script does not call benefits portals, payroll systems, insurer systems, email, fax, payment systems, or government systems.
- Do not paste full SSNs, full card numbers, account credentials, raw unrelated PHI, secrets, or private legal/tax advice into public prompts.
- Keep final claim submission, reimbursement, repayment, appeal, payroll, and tax decisions with the authorized owner.
