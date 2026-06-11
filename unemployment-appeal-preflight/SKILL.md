---
name: unemployment-appeal-preflight
description: Review unemployment insurance denial, employer appeal, hearing, overpayment, misconduct, voluntary quit, able-and-available, work-search, or late-appeal packets before a claimant, employer, legal-aid intake helper, workforce navigator, or benefits advocate submits an appeal, prepares for a hearing, requests reopening, or organizes evidence. Use when the user needs deadline, issue, evidence-exchange, witness, hearing-packet, weekly-certification, and live-portal-action guardrails without giving legal advice or contacting an agency.
---

# Unemployment Appeal Preflight

## Overview

Use this skill when a claimant, employer, workforce navigator, legal-aid intake helper, caregiver, HR partner, or benefits advocate needs a local-first readiness review for an unemployment insurance appeal or hearing packet.

This is administrative workflow support. It is not legal advice, benefit eligibility advice, representation, tax advice, or agency action.

## Use And Do Not Use

Use for:

- Checking appeal or hearing packets after a benefit denial, disqualification, employer appeal, overpayment notice, reopening request, or second-level appeal.
- Mapping issue type to evidence gaps for misconduct, voluntary quit, able-and-available, work search, refusal of work, severance/wages, identity, and overpayment disputes.
- Preparing a neutral packet checklist, hearing outline, witness list, evidence-exchange checklist, deadline review, or questions for counsel/agency staff.
- Helping users avoid missed deadlines, missing determination notices, unsupported timelines, unexchanged exhibits, no-show risk, contradictory statements, and live portal mistakes.

Do not use for:

- Deciding eligibility, predicting hearing outcomes, telling a user they will win, or advising whether to appeal.
- Filing appeals, uploading evidence, contacting employers, contacting state agencies, requesting subpoenas, joining hearings, or sending portal messages without explicit authorized owner action.
- Inventing facts, dates, notices, witnesses, writeups, policies, work-search logs, medical notes, signatures, agency correspondence, or delivery proof.
- Accusing fraud, retaliation, misconduct, discrimination, or perjury. Label findings as evidence gaps or issue risks.
- Uploading SSNs, claimant IDs, portal credentials, full bank details, raw tax records, medical details, or secrets.

## Required Inputs

Ask only for missing inputs that materially affect readiness:

- Case table or JSON. Preferred fields: `case_id`, `party_role`, `state`, `appeal_stage`, `issue_type`, `determination_date`, `appeal_deadline`, `hearing_date`, `determination_notice`, `hearing_notice`, `hearing_packet`, `claimant_statement`, `employer_evidence`, `separation_timeline`, `policy_or_handbook`, `warning_or_writeup`, `firsthand_witness`, `witness_contact`, `work_search_or_weekly_certification`, `medical_or_caregiver_evidence`, `good_cause_explanation`, `evidence_exchanged_to_all_parties`, `language_access_or_accommodation`, `live_action_requested`.
- Optional local evidence directory with redacted determinations, hearing notices, employer exhibits, termination or resignation records, policies, warnings, witness notes, work-search logs, payment histories, appeal confirmations, delivery receipts, and agency correspondence.
- Review date when deadlines or hearing timing matter.

If the user only has screenshots or PDFs, ask them to transcribe the determination date, appeal deadline, hearing date, issue type, evidence list, and whether exhibits were sent to every listed party before producing a final classification.

## Workflow

### 1. Preserve Boundaries

Before analysis:

- Tell the user to redact SSNs, claimant IDs, portal credentials, bank details, full medical details, tax identifiers, employer trade secrets, and unrelated personal data.
- Keep eligibility decisions, legal strategy, hearing representation, appeal filing, subpoena requests, portal uploads, and agency communications with the authorized claimant, employer, representative, legal-aid provider, counsel, or agency staff.
- Separate facts supplied by the user from evidence still missing.

Read `references/unemployment-appeal-rules.md` before classifying a packet as ready.

### 2. Run The Local Preflight

Use explicit paths:

```bash
python3 unemployment-appeal-preflight/scripts/unemployment_appeal_preflight.py \
  --cases /absolute/path/appeal_cases.csv \
  --evidence-dir /absolute/path/evidence \
  --today 2026-06-12
```

The script accepts CSV or JSON. JSON may be a list or an object containing `cases`, `appeals`, `hearings`, or `rows`.

### 3. Classify Appeal Blockers

Use one primary action per finding:

- `hold_appeal_packet`: missing determination notice, issue type, appeal stage, hearing notice, hearing packet, claimant statement, or required local evidence.
- `deadline_escalation`: appeal deadline, hearing date, reopening period, or second-level appeal date is missing, passed, or near.
- `evidence_exchange_repair`: evidence has not been sent to the hearing office and all listed parties, exhibit pages are unnumbered, or delivery proof is missing.
- `issue_evidence_mapping`: misconduct, quit, able-and-available, work-search, overpayment, or separation issue is not tied to the right records and firsthand witnesses.
- `witness_readiness`: firsthand witness, contact, availability, or testimony topic is missing.
- `certification_continuity`: claimant has not continued required weekly certifications or work-search records during the appeal period.
- `owner_review`: packet has no material local blockers but still needs authorized owner review.

Never state that a user is eligible, ineligible, guaranteed to win, or legally required to take a specific action. Say what evidence is missing, what procedural question is unresolved, and who should verify it.

### 4. Produce The Report

Return:

```markdown
## Unemployment Appeal Decision
[Hold appeal packet pending evidence repair / Review before hearing or filing / Packet appears ready for authorized owner review]

## Appeal Summary
[Review date, cases reviewed, blocker count, review count]

## Findings
| Severity | Action | Case | State | Stage | Issue | Flag | Evidence | Next step |
|---|---|---|---|---|---|---|---|---|

## Hearing Packet Checklist
[Determination, deadline, hearing notice, issue list, exhibits, evidence exchange, witness list, weekly certifications, delivery proof, access needs]

## Guardrails
[Privacy, authority, no legal advice, no live agency action]
```

Use `templates/appeal-hearing-checklist.md` when the user wants a reusable checklist.

## Examples And Acceptance Checks

Positive example: "Use unemployment-appeal-preflight on this denial notice, hearing packet, employer exhibits, and timeline before my hearing." The skill should map issue type to deadlines, evidence exchange, witness readiness, and missing records.

Employer appeal example: "My former employer appealed after I was approved." The skill should check hearing notice, employer evidence, issue scope, claimant statement consistency, firsthand witness needs, and weekly certifications without predicting the outcome.

Negative example: "Tell me if I will win and file the appeal for me." Do not decide or file; produce evidence gaps, owner questions, and live-action boundaries.

Boundary example: "Upload these exhibits to the unemployment portal." Do not upload; prepare an exhibit checklist and require explicit authorized owner action.

## Validation

Smoke-test the bundled fixture:

```bash
python3 unemployment-appeal-preflight/scripts/unemployment_appeal_preflight.py \
  --cases unemployment-appeal-preflight/scripts/fixtures/appeal_cases.csv \
  --evidence-dir unemployment-appeal-preflight/scripts/fixtures/evidence \
  --today 2026-06-12
```

Expected result: exit code `2` with `Unemployment Appeal Decision`, `Hold appeal packet pending evidence repair`, `appeal_deadline_passed`, `hearing_packet_missing`, `misconduct_evidence_missing_or_unsupported`, `evidence_not_exchanged_to_all_parties`, `weekly_certification_or_work_search_missing`, and `live_action_requested`.
