---
name: fmla-certification-preflight
description: Review FMLA medical certification, leave request, cure notice, eligibility, designation, intermittent-leave, family-care, or return-to-work paperwork before an employee, caregiver, HR partner, manager, union steward, clinic helper, or benefits advocate submits, denies, cures, or escalates the packet. Use when the user needs 15-day certification, 7-day cure, eligibility-notice, serious-health-condition, provider-completeness, deadline, and live-action guardrails without giving legal advice or contacting an employer, provider, insurer, or agency.
---

# FMLA Certification Preflight

## Overview

Use this skill when an employee, caregiver, HR partner, manager, union steward, clinic helper, or benefits advocate needs a local-first readiness review for Family and Medical Leave Act (FMLA) certification paperwork.

This is administrative workflow support. It is not legal advice, medical advice, employment advice, representation, form filing, or employer/provider/agency action.

## Use And Do Not Use

Use for:

- Checking FMLA certification packets before submission, cure, designation, HR review, manager handoff, clinic follow-up, or owner escalation.
- Mapping missing or vague certification fields to packet repair steps for serious health condition, intermittent leave, reduced schedule, family-care relationship, provider signature, treatment schedule, and incapacity statements.
- Tracking 15-calendar-day certification windows, written incomplete/insufficient notices, seven-calendar-day cure opportunities, designation notices, and imminent deadline risks.
- Preparing a neutral checklist, evidence index, provider-question list, HR-question list, timeline, and owner-review packet.

Do not use for:

- Deciding whether someone is legally entitled to FMLA, whether leave can be denied, whether discipline is lawful, or whether to sue, complain, terminate, retaliate, or settle.
- Contacting employers, managers, HR, leave administrators, health care providers, insurers, unions, agencies, or courts.
- Filling in medical facts, diagnoses, incapacity periods, frequency estimates, treatment plans, signatures, provider statements, employer notices, or delivery proof.
- Uploading forms to leave portals, submitting claims, changing employment records, or giving medical restrictions.
- Handling SSNs, full medical records, full diagnosis narratives, claim numbers, portal credentials, bank data, tax identifiers, or unrelated personnel files.

## Required Inputs

Ask only for missing inputs that materially affect readiness:

- Case table or JSON. Preferred fields: `case_id`, `employee_role`, `employer_employee_count`, `tenure_months`, `hours_worked_last_12_months`, `worksite_employee_count_75_miles`, `leave_reason`, `leave_start_date`, `certification_requested_date`, `certification_due_date`, `certification_submitted_date`, `incomplete_or_insufficient_notice`, `cure_notice_date`, `cure_due_date`, `certification_signed`, `provider_contact_info`, `serious_health_condition_checked`, `incapacity_duration`, `treatment_schedule`, `intermittent_frequency`, `unable_to_work_or_care_statement`, `family_relationship`, `eligibility_notice_received`, `rights_responsibilities_notice_received`, `designation_notice_received`, `live_action_requested`.
- Optional local evidence directory with redacted eligibility notices, rights-and-responsibilities notices, WH-380/WH-381/WH-382-style forms, provider office messages, cure notices, submission confirmations, and delivery receipts.
- Review date when certification or cure timing matters.

If the user only has screenshots or PDFs, ask them to transcribe dates, whether a written defect/cure notice exists, whether the certification is signed, whether provider contact and incapacity/schedule fields are filled, and whether any live submission or contact is being requested.

## Workflow

### 1. Preserve Boundaries

Before analysis:

- Tell the user to redact SSNs, full medical histories, diagnoses beyond what is necessary, claim numbers, portal credentials, full employee IDs, bank data, tax identifiers, and unrelated personnel data.
- Keep legal strategy, denial decisions, discipline decisions, provider communications, HR communications, agency complaints, portal uploads, and form submission with the authorized employee, employer owner, provider, representative, attorney, union, or agency staff.
- Separate facts supplied by the user from evidence still missing.

Read `references/fmla-certification-rules.md` before classifying a packet as ready.

### 2. Run The Local Preflight

Use explicit paths:

```bash
python3 fmla-certification-preflight/scripts/fmla_certification_preflight.py \
  --cases /absolute/path/fmla_cases.csv \
  --evidence-dir /absolute/path/evidence \
  --today 2026-06-16
```

The script accepts CSV or JSON. JSON may be a list or an object containing `cases`, `requests`, `leaves`, or `rows`.

### 3. Classify Blockers

Use one primary action per finding:

- `hold_packet`: missing certification, missing provider signature/contact, missing serious-health-condition selection, missing incapacity/treatment details, missing family-care relationship, missing required notices, or sensitive file-name risk.
- `deadline_escalation`: certification due date, cure due date, leave start date, submitted date, or notice date is missing, passed, or near.
- `cure_notice_review`: certification was labeled incomplete or insufficient, but the written defect notice, seven-day cure window, specific missing information, or cure proof is missing.
- `eligibility_review`: tenure, hours, employer size, worksite count, or eligibility notice is missing or appears below the usual threshold and needs owner review.
- `intermittent_schedule_repair`: intermittent or reduced-schedule leave lacks frequency, duration, treatment schedule, flare-up pattern, or incapacity explanation.
- `owner_review`: packet has no material local blockers but still needs authorized owner review.

Never state that leave is protected, unprotected, approved, denied, fraudulent, abusive, or legally required to be handled a specific way. Say what evidence is missing, what procedural question is unresolved, and who should verify it.

### 4. Produce The Report

Return:

```markdown
## FMLA Certification Decision
[Hold certification packet pending repair / Review certification packet before submission or designation / Packet appears ready for authorized owner review]

## Case Summary
[Review date, cases reviewed, blocker count, review count]

## Findings
| Severity | Action | Case | Leave reason | Flag | Evidence | Next step |
|---|---|---|---|---|---|---|

## Packet Checklist
[Eligibility notice, rights/responsibilities notice, certification request date, due date, submitted date, cure notice, provider signature, provider contact, serious health condition, incapacity/schedule, intermittent frequency, designation notice, delivery proof, owner questions]

## Guardrails
[Privacy, authority, no legal advice, no medical advice, no live employer/provider/agency action]
```

Use `templates/certification-packet-checklist.md` when the user wants a reusable checklist.

## Examples And Acceptance Checks

Positive example: "Use fmla-certification-preflight on this WH-380 form, eligibility notice, cure notice, and HR deadline email before I send it back." The skill should check deadlines, written cure notice, provider fields, incapacity/schedule statements, family-care fields if relevant, and live-action boundaries.

Intermittent leave example: "My doctor wrote 'as needed' for migraines." The skill should flag vague frequency/duration and prepare provider questions without inventing medical facts.

HR review example: "Can we deny this because the certification is incomplete?" The skill should check whether missing fields were identified in writing, whether a cure window exists, and whether owner/legal review is needed without deciding denial lawfulness.

Negative example: "Tell HR they must approve this and submit the form." Do not approve, deny, or submit; produce evidence gaps, owner questions, and live-action boundaries.

Boundary example: "Email my doctor to fix the form." Do not contact the provider; prepare a neutral question list for the authorized user.

## Validation

Smoke-test the bundled fixture:

```bash
python3 fmla-certification-preflight/scripts/fmla_certification_preflight.py \
  --cases fmla-certification-preflight/scripts/fixtures/fmla_cases.csv \
  --evidence-dir fmla-certification-preflight/scripts/fixtures/evidence \
  --today 2026-06-16
```

Expected result: exit code `2` with `FMLA Certification Decision`, `Hold certification packet pending repair`, `certification_deadline_passed`, `provider_signature_missing`, `serious_health_condition_field_missing`, `intermittent_frequency_missing`, `cure_deadline_passed`, `eligibility_notice_missing`, and `live_action_requested`.
