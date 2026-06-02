# Sample FSA Claim Substantiation Report

## FSA Claim Substantiation Decision
Hold claim packet pending evidence repair

## Packet Summary
Review date: 2026-06-03. Claims reviewed: 4. Blockers: 9. Review items: 4.

## Findings

| Severity | Action | Claim | Account | Expense | Amount | Flag | Evidence | Next step |
|---|---|---|---|---|---:|---|---|---|
| blocker | hold_claim | FSA-1001 | health_fsa | physical_therapy | USD 450.00 | missing_eob_for_insured_service | matching files: FSA-1001_receipt.txt | Add the insurance EOB or plan statement showing patient responsibility. |
| blocker | hold_claim | FSA-1002 | dependent_care_fsa | daycare | USD 1200.00 | dependent_care_certification_missing | matching files: FSA-1002_invoice.txt | Get provider certification/signature or compliant itemized statement before resubmission. |
| blocker | portal_guardrail | FSA-1004 | health_fsa | portal_submission | USD 80.00 | live_portal_action_requested | no matching local evidence files | Do not ask the agent to submit in a live portal; prepare the packet for owner action. |

## Correction Checklist

- Add EOBs for insured claims.
- Replace payment proofs with itemized receipts.
- Add dependent-care provider certification and TIN when required.
- Check coverage/runout deadlines before resubmission.

## Guardrails

Administrative packet-readiness support only. No tax, legal, medical, payroll, plan-design, portal-submission, or reimbursement decision is made here.
