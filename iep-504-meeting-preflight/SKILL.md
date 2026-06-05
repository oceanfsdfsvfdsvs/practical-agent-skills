---
name: iep-504-meeting-preflight
description: Review IEP, Section 504, special education evaluation, reevaluation, accommodation, service-log, progress, manifestation, or school meeting packets before a parent, caregiver, advocate, or school team attends a meeting, requests records, escalates a concern, or submits a complaint. Use when the user needs to map student needs, evaluations, goals, accommodations, services, progress data, missed services, consent/notice, deadlines, and evidence gaps without giving legal advice or taking live school-portal actions.
---

# IEP/504 Meeting Preflight

## Overview

Use this skill when a parent, caregiver, student support helper, advocate, or school team needs a local-first readiness review before an IEP meeting, 504 meeting, evaluation request, reevaluation, manifestation meeting, service-log review, records request, complaint packet, or follow-up with a school district.

This is administrative and educational workflow support. It is not legal, clinical, diagnostic, therapeutic, school-placement, or special education advocacy advice.

## Use And Do Not Use

Use for:

- Checking whether meeting packets include current evaluations, prior plans, progress reports, service logs, accommodation history, parent concerns, notices, consent status, and data tied to requested changes.
- Mapping concerns to evidence gaps before meetings about eligibility, goals, services, accommodations, behavioral supports, assistive technology, transition planning, missed services, or implementation failures.
- Preparing a neutral agenda, packet checklist, school-record request list, question list, or owner-reviewed follow-up plan.
- Helping families and school teams avoid attending meetings with vague requests, missing records, stale evaluations, unsupported service changes, or undocumented implementation concerns.

Do not use for:

- Deciding eligibility, disability category, placement, legal violations, compensatory education, discipline outcomes, diagnoses, treatment, or entitlement.
- Inventing evaluations, progress data, service minutes, provider notes, parent consent, signatures, notices, or school communications.
- Submitting complaints, due process filings, OCR complaints, FERPA requests, emails, portal messages, or meeting responses without explicit authorized owner action.
- Uploading full student IDs, SSNs, medical records, login credentials, private therapy notes, unrelated family details, or secrets.
- Replacing counsel, clinicians, licensed evaluators, school officials, parent centers, or jurisdiction-specific guidance.

## Required Inputs

Ask only for missing inputs that materially affect readiness:

- Case table or JSON. Preferred fields: `case_id`, `student_role`, `meeting_type`, `plan_type`, `grade_band`, `primary_concern`, `requested_change`, `meeting_date`, `last_evaluation_date`, `reevaluation_due_date`, `prior_plan`, `evaluation_report`, `progress_report`, `service_log`, `accommodation_log`, `parent_concerns`, `school_notice`, `consent_status`, `behavior_data`, `discipline_notice`, `transition_plan`, `assistive_technology_review`, `live_action_requested`.
- Optional local evidence directory with redacted IEP/504 plans, evaluations, progress reports, service logs, notices, consent forms, parent concern letters, communication logs, behavior data, and work samples.
- Review date when deadlines, meeting timing, or reevaluation dates matter.

If the user only has screenshots or PDFs, ask them to transcribe the meeting date, plan type, requested change, evidence list, and deadlines before producing a final classification.

## Workflow

### 1. Preserve Boundaries

Before analysis:

- Tell the user to redact student IDs, SSNs, portal credentials, medical account numbers, unrelated diagnoses, unrelated family details, and secrets.
- Keep final meeting decisions, legal filings, consent decisions, service changes, and medical/clinical conclusions with the parent/guardian, adult student, authorized advocate, school team, evaluator, clinician, or counsel.
- Separate facts supplied by the user from evidence still missing.

Read `references/iep-504-meeting-rules.md` before classifying a packet as ready.

### 2. Run The Local Preflight

Use explicit paths:

```bash
python3 iep-504-meeting-preflight/scripts/iep_504_meeting_preflight.py \
  --cases /absolute/path/meeting_cases.csv \
  --evidence-dir /absolute/path/evidence \
  --today 2026-06-06
```

The script accepts CSV or JSON. JSON may be a list or an object containing `cases`, `meetings`, `students`, or `rows`.

### 3. Classify Meeting Blockers

Use one primary action per finding:

- `hold_meeting_packet`: missing prior plan, current evaluation, progress report, parent concerns, consent/notice evidence, or required meeting-specific data.
- `deadline_escalation`: meeting date, evaluation request, consent, reevaluation, or record-response date is missing, passed, or near.
- `evaluation_repair`: requested change is not tied to a current evaluation, independent report, work sample, observation, or school data.
- `implementation_review`: service minutes, accommodations, progress, missed services, or provider logs are missing or inconsistent.
- `goal_data_mapping`: goals, baseline data, progress measures, or requested service changes are vague or unsupported.
- `behavior_or_discipline_review`: manifestation, suspension, behavior support, or safety concern lacks discipline notice, behavior data, or support plan evidence.
- `transition_or_at_review`: transition or assistive technology concern lacks age-appropriate transition, device, access, or trial data.
- `owner_review`: packet has no material local blockers but still needs authorized owner review.

Never write that a school "must provide" a placement, service, or remedy. Say what evidence is missing, what question is unresolved, and who should verify it.

### 4. Produce The Report

Return:

```markdown
## IEP/504 Meeting Decision
[Hold meeting packet pending evidence repair / Review before meeting / Packet appears ready for authorized owner review]

## Meeting Summary
[Review date, cases reviewed, blocker count, review count]

## Findings
| Severity | Action | Case | Plan | Meeting type | Concern | Flag | Evidence | Next step |
|---|---|---|---|---|---|---|---|---|

## Packet Checklist
[Plan, evaluation, progress data, service logs, accommodation history, notices, consent, parent concerns, meeting agenda]

## Guardrails
[Privacy, authority, legal/clinical/eligibility boundary]
```

Use `templates/meeting-packet-checklist.md` when the user wants a reusable checklist.

## Examples And Acceptance Checks

Positive example: "Use iep-504-meeting-preflight on this 504 meeting packet, accommodation log, and parent concern list." The skill should map concerns to missing accommodation history, progress data, notice/consent gaps, and meeting questions.

Positive IEP example: "We have an IEP annual review next week and want to ask for reading support changes." The skill should request current evaluation data, present levels, goal progress, service logs, work samples, and parent concerns without deciding placement.

Negative example: "Tell me the school violated IDEA and draft a due process complaint." Do not make legal conclusions; produce evidence gaps, owner questions, and escalation-prep boundaries.

Boundary example: "Email the principal and submit the complaint." Do not submit; prepare a packet and require explicit authorized owner action.

## Validation

Smoke-test the bundled fixture:

```bash
python3 iep-504-meeting-preflight/scripts/iep_504_meeting_preflight.py \
  --cases iep-504-meeting-preflight/scripts/fixtures/meeting_cases.csv \
  --evidence-dir iep-504-meeting-preflight/scripts/fixtures/evidence \
  --today 2026-06-06
```

Expected result: exit code `2` with `IEP/504 Meeting Decision`, `Hold meeting packet pending evidence repair`, `current_evaluation_missing_or_stale`, `progress_report_missing`, `service_log_missing`, `behavior_or_discipline_data_missing`, `reevaluation_deadline_review`, and `live_action_requested`.
