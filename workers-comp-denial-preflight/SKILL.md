---
name: workers-comp-denial-preflight
description: Review workers' compensation claim denial, delayed care, medical causation, pre-existing condition, late reporting, employer dispute, hearing, or appeal packets before an injured worker, caregiver, HR partner, union steward, legal-aid intake helper, or claims advocate organizes evidence or seeks owner review. Use when the user needs denial-letter, deadline, medical-record, incident-report, witness, work-restriction, health-insurance-crossover, evidence-exchange, and live-action guardrails without giving legal advice or contacting an insurer, employer, agency, or court.
---

# Workers' Comp Denial Preflight

## Overview

Use this skill when an injured worker, caregiver, HR partner, union steward, clinic helper, legal-aid intake helper, or claims advocate needs a local-first readiness review after a workers' compensation claim denial or disputed treatment.

This is administrative workflow support. It is not legal advice, benefit eligibility advice, medical advice, representation, insurance claim filing, or agency/court action.

## Use And Do Not Use

Use for:

- Checking denial or appeal packets before an owner, attorney, union representative, ombuds office, state information unit, or claims advocate reviews them.
- Mapping denial reasons to missing evidence for late notice, work-relatedness, pre-existing condition, medical necessity, independent medical exam, wage-loss, employer dispute, or documentation gaps.
- Preparing a neutral packet checklist, chronology, evidence index, provider-question list, witness list, hearing prep outline, or health-insurance crossover notes.
- Helping users avoid missed appeal deadlines, missing denial letters, unsupported causation narratives, no incident report, missing restrictions, untracked bills, and live portal mistakes.

Do not use for:

- Deciding compensability, predicting appeal outcomes, advising whether to sue or settle, telling a user they will win, or choosing legal strategy.
- Filing appeals, uploading evidence, contacting adjusters, employers, medical providers, state agencies, courts, or insurers without explicit authorized owner action.
- Inventing injury facts, dates, symptoms, witness statements, medical opinions, work restrictions, employer admissions, signatures, agency correspondence, or delivery proof.
- Accusing fraud, retaliation, misconduct, discrimination, bad faith, or perjury. Label issues as evidence gaps or procedural risks.
- Uploading SSNs, claim numbers, portal credentials, full medical histories, full health insurance IDs, bank details, tax records, or unrelated personal data.

## Required Inputs

Ask only for missing inputs that materially affect readiness:

- Case table or JSON. Preferred fields: `case_id`, `state`, `worker_role`, `injury_date`, `report_date`, `denial_date`, `appeal_deadline`, `hearing_date`, `denial_letter`, `denial_reason`, `incident_report`, `medical_records`, `medical_record_work_related`, `work_restrictions`, `witness_statement`, `employer_dispute`, `prior_condition_dispute`, `treatment_denied_or_bills`, `health_insurance_crossover`, `return_to_work_status`, `evidence_exchanged_to_parties`, `live_action_requested`.
- Optional local evidence directory with redacted denial letters, injury reports, supervisor emails, medical records that state work-relatedness, restrictions, bills, EOBs, witness notes, time records, appeal confirmations, and delivery receipts.
- Review date when deadlines or hearing timing matter.

If the user only has screenshots or PDFs, ask them to transcribe the denial date, deadline, denial reason, injury/report dates, state, hearing date if any, and whether medical records connect the injury to work before producing a final classification.

## Workflow

### 1. Preserve Boundaries

Before analysis:

- Tell the user to redact SSNs, claim numbers, portal credentials, full medical histories, full health insurance IDs, bank data, tax identifiers, employer trade secrets, and unrelated personal data.
- Keep legal strategy, compensability decisions, settlement advice, appeal filing, provider calls, insurer calls, employer communications, portal uploads, subpoena requests, and agency/court communications with the authorized worker, representative, attorney, union, advocate, medical provider, agency staff, or insurer.
- Separate facts supplied by the user from evidence still missing.

Read `references/workers-comp-denial-rules.md` before classifying a packet as ready.

### 2. Run The Local Preflight

Use explicit paths:

```bash
python3 workers-comp-denial-preflight/scripts/workers_comp_denial_preflight.py \
  --cases /absolute/path/workers_comp_cases.csv \
  --evidence-dir /absolute/path/evidence \
  --today 2026-06-14
```

The script accepts CSV or JSON. JSON may be a list or an object containing `cases`, `claims`, `appeals`, or `rows`.

### 3. Classify Blockers

Use one primary action per finding:

- `hold_packet`: missing denial letter, denial reason, incident report, medical record, work-restriction evidence, or required local evidence.
- `deadline_escalation`: appeal deadline, hearing date, denial date, claim petition date, or state response window is missing, passed, or near.
- `medical_causation_repair`: denial cites non-work-related injury, pre-existing condition, inadequate medical evidence, IME, medical necessity, or treatment authorization, but the packet lacks provider records tying injury, restrictions, treatment, and work duties together.
- `employer_dispute_repair`: employer disputes the injury, notice, job duty, or timeline, but the packet lacks incident report, supervisor notice, witness support, time records, or contemporaneous notes.
- `billing_crossover_review`: workers' comp denial has created health-insurance, provider bill, EOB, collection, or timely-filing risk that needs owner/provider/insurer review.
- `evidence_exchange_repair`: appeal or hearing evidence has not been shared with all required parties or delivery proof is missing.
- `owner_review`: packet has no material local blockers but still needs authorized owner review.

Never state that the claim is covered, not covered, payable, fraudulent, or legally required to take a specific action. Say what evidence is missing, what procedural question is unresolved, and who should verify it.

### 4. Produce The Report

Return:

```markdown
## Workers' Comp Denial Decision
[Hold packet pending evidence repair / Review before filing or hearing / Packet appears ready for authorized owner review]

## Claim Summary
[Review date, cases reviewed, blocker count, review count]

## Findings
| Severity | Action | Case | State | Denial reason | Flag | Evidence | Next step |
|---|---|---|---|---|---|---|---|

## Packet Checklist
[Denial letter, deadline, incident report, medical causation, restrictions, witnesses, bills/EOBs, evidence exchange, delivery proof, owner questions]

## Guardrails
[Privacy, authority, no legal advice, no medical advice, no live insurer/employer/agency action]
```

Use `templates/denial-packet-checklist.md` when the user wants a reusable checklist.

## Examples And Acceptance Checks

Positive example: "Use workers-comp-denial-preflight on this denial letter, incident report, provider note, work restrictions, and bills before I talk with the state information unit." The skill should map denial reason to deadlines, medical causation, employer dispute, billing crossover, and evidence gaps.

Employer dispute example: "My employer says I did not report it on time." The skill should check injury/report dates, supervisor notice proof, incident report, witness support, and contemporaneous notes without deciding legal sufficiency.

Health-insurance crossover example: "Workers' comp denied it and now the hospital bill is coming to me." The skill should flag EOB/bill/timely-filing review and owner/provider/insurer questions without submitting claims.

Negative example: "Tell me if my claim is valid and file the appeal." Do not decide or file; produce evidence gaps, owner questions, and live-action boundaries.

Boundary example: "Send this packet to the adjuster." Do not send; prepare an evidence index and require explicit authorized owner action.

## Validation

Smoke-test the bundled fixture:

```bash
python3 workers-comp-denial-preflight/scripts/workers_comp_denial_preflight.py \
  --cases workers-comp-denial-preflight/scripts/fixtures/workers_comp_cases.csv \
  --evidence-dir workers-comp-denial-preflight/scripts/fixtures/evidence \
  --today 2026-06-14
```

Expected result: exit code `2` with `Workers' Comp Denial Decision`, `Hold packet pending evidence repair`, `appeal_deadline_passed`, `denial_letter_missing`, `medical_causation_evidence_missing`, `incident_report_missing`, `work_restrictions_missing`, `billing_crossover_review`, `evidence_not_exchanged_to_all_parties`, and `live_action_requested`.
