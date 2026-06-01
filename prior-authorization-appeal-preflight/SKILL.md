---
name: prior-authorization-appeal-preflight
description: Review prior authorization denials for medications, imaging, procedures, therapy, DME, or services before an appeal is submitted. Use when a patient, caregiver, benefits advocate, clinic, or HR benefits helper needs to map denial reasons to payer criteria, deadlines, medical necessity evidence, step-therapy proof, representative authorization, coding/site mismatches, and packet-readiness blockers without logging into insurer portals.
---

# Prior Authorization Appeal Preflight

## Overview

Use this skill when a prior authorization request has been delayed, denied, partially approved, or rejected on appeal and the user needs a local-first readiness review before submitting an internal appeal, reconsideration, peer-to-peer packet, or external review request.

This is administrative workflow support. It is not medical, legal, billing, insurance-coverage, or clinical advice.

## Use And Do Not Use

Use for:

- Medication, imaging, procedure, therapy, durable medical equipment, home health, infusion, or specialty-service prior authorization denials.
- Mapping denial reasons to missing evidence, payer criteria, step therapy, continuation-of-care proof, coding/site/quantity mismatches, or appeal deadlines.
- Preparing an owner-reviewed appeal packet checklist, evidence gap list, call script, or provider request list.
- Helping patients, caregivers, benefits advocates, small clinics, and HR benefits teams avoid resubmitting the same incomplete packet.

Do not use for:

- Deciding clinical necessity, changing treatment, or promising coverage.
- Inventing diagnoses, failed therapies, contraindications, signatures, payer criteria, or provider statements.
- Submitting appeals, portal messages, complaints, external review requests, or peer-to-peer requests without explicit authorization.
- Uploading uncensored PHI, full member IDs, SSNs, credentials, payment card data, private legal advice, or secrets.
- Replacing urgent medical care, clinician judgment, plan documents, regulator instructions, or counsel.

## Required Inputs

Ask only for missing inputs that materially affect readiness:

- Prior authorization case table or JSON. Preferred fields: `case_id`, `patient_role`, `plan_type`, `stage`, `service_type`, `requested_service`, `diagnosis_code`, `procedure_code`, `denial_reason`, `denial_date`, `appeal_deadline`, `urgent`, `denial_letter`, `medical_records`, `letter_of_medical_necessity`, `payer_criteria`, `step_therapy_required`, `failed_alternatives_documented`, `objective_results`, `representative_authorization`, `peer_to_peer_requested`, `patient_safety_risk`.
- Optional local evidence directory with redacted denial letters, chart notes, payer criteria, medical-necessity letters, step-therapy history, lab/imaging results, call logs, and representative authorization.
- Review date when deadlines matter.

If the user only has screenshots or PDFs, ask them to transcribe the denial reason, deadline, service, codes, and evidence list before producing a final classification.

## Workflow

### 1. Preserve Boundaries

Before analysis:

- Tell the user to redact full member IDs, SSNs, payment data, unrelated clinical details, portal credentials, and secrets.
- Keep final appeal, external review, grievance, portal, fax, and treatment decisions with the patient, authorized representative, treating clinician, or benefits owner.
- Separate clinical facts supplied by the user from evidence that is still missing.

Read `references/prior-authorization-appeal-rules.md` before classifying a case as ready to submit.

### 2. Run The Local Preflight

Use explicit paths:

```bash
python3 prior-authorization-appeal-preflight/scripts/prior_authorization_appeal_preflight.py \
  --cases /absolute/path/appeal_cases.csv \
  --evidence-dir /absolute/path/evidence \
  --today 2026-06-02
```

The script accepts CSV or JSON. JSON may be a list or an object containing `cases`, `appeals`, or `rows`.

### 3. Classify Appeal Blockers

Use one primary action per finding:

- `hold_appeal`: missing denial letter, missing medical records, missing medical necessity letter, missing step-therapy proof, missing representative authorization, passed deadline, repeated appeal not addressing rejection, or live portal action requested.
- `deadline_escalation`: deadline is missing, passed, or within 7 days.
- `criteria_mapping`: payer criteria or denial-specific requirement is not mapped to evidence.
- `step_therapy_repair`: trial/failure/intolerance/contraindication evidence is missing.
- `coding_site_reconciliation`: CPT/HCPCS/NDC, units, site of service, provider type, or scheduled date may not match the request.
- `expedited_review_check`: urgent or safety-risk case lacks clinician attestation for expedited handling.
- `peer_to_peer_log`: peer-to-peer request or outcome is not documented.
- `owner_review`: packet has no material local blockers but still needs authorized owner review.

Never write that a service "must be covered." Say what evidence is missing, what criteria are unmapped, and what owner should verify.

### 4. Produce The Report

Return:

```markdown
## Prior Authorization Appeal Decision
[Hold appeal pending evidence repair / Review before submission / Packet appears ready for authorized owner review]

## Appeal Summary
[Review date, cases reviewed, blocker count, review count]

## Findings
| Severity | Action | Case | Service | Denial reason | Flag | Evidence | Next step |
|---|---|---|---|---|---|---|---|

## Packet Checklist
[Denial letter, authorization, criteria map, clinical support, step therapy, code/site reconciliation, logs]

## Guardrails
[Privacy, authority, medical/legal/coverage boundary]
```

Use `templates/appeal-packet-checklist.md` when the user wants a reusable owner checklist.

## Examples And Acceptance Checks

Positive example: "Use prior-authorization-appeal-preflight on this MRI denial letter, chart note list, and appeal deadline." The skill should map the denial reason, check payer criteria and conservative therapy evidence, and produce a blocker/readiness report.

Positive medication example: "My biologic continuation was denied for step therapy even though I already failed alternatives." The skill should request documented trials, dates, outcomes, contraindications, continuation evidence, and provider-signed support without deciding clinical necessity.

Negative example: "Write a letter saying the insurer illegally denied this." Do not make legal conclusions; produce evidence gaps and owner escalation options.

Boundary example: "Submit the appeal in my portal." Do not submit; prepare the packet and require explicit authorized owner action.

## Validation

Smoke-test the bundled fixture:

```bash
python3 prior-authorization-appeal-preflight/scripts/prior_authorization_appeal_preflight.py \
  --cases prior-authorization-appeal-preflight/scripts/fixtures/appeal_cases.csv \
  --evidence-dir prior-authorization-appeal-preflight/scripts/fixtures/evidence \
  --today 2026-06-02
```

Expected result: exit code `2` with `Prior Authorization Appeal Decision`, `Hold appeal pending evidence repair`, `missing_step_therapy_documentation`, `missing_letter_of_medical_necessity`, `representative_authorization_missing`, `appeal_deadline_passed`, and `live_portal_action_requested`.
