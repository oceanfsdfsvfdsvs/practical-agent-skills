## Prior Authorization Appeal Decision
Hold appeal pending evidence repair

## Appeal Summary
- Review date: 2026-06-02
- Cases reviewed: 3
- Blockers: 10
- Review items: 7

## Findings
| Severity | Action | Case | Service | Denial reason | Flag | Evidence | Next step |
|---|---|---|---|---|---|---|---|
| blocker | evidence_repair | PA-1001 | MRI lumbar spine | medical_necessity | missing_letter_of_medical_necessity | pa-1001_clinical_note.txt, pa-1001_denial_letter.txt | Prepare a provider-signed letter tying diagnosis, requested service, criteria, and risk of delay. |
| blocker | step_therapy_repair | PA-1001 | MRI lumbar spine | medical_necessity | missing_step_therapy_documentation | pa-1001_clinical_note.txt, pa-1001_denial_letter.txt | List required alternatives, trial dates, outcomes, failures, intolerance, or contraindications. |
| blocker | authorization_needed | PA-1003 | Home infusion therapy | missing_information | representative_authorization_missing | no matching local evidence files | Collect signed representative authorization before sending appeal materials. |
| blocker | manual_owner_action | PA-1003 | Home infusion therapy | missing_information | live_portal_action_requested | Input requested a live portal action. | Do not submit portal messages or appeals from this skill; prepare the packet for authorized owner review. |

## Packet Checklist
- Written denial/adverse determination with appeal instructions and deadline.
- Patient/member authorization if anyone else files or discusses the appeal.
- Denial reason mapped to payer criteria, with each criterion tied to evidence.
- Provider-signed medical necessity or reconsideration letter when clinical review is needed.
- Chart notes, prior treatment history, objective results, and step-therapy failure/intolerance evidence.
- Coding, units, site-of-service, and provider-type reconciliation for code/site/quantity denials.
- Peer-to-peer log, call log, fax/portal receipts, and owner/date tracker.

## Guardrails
- This is administrative workflow support, not medical, legal, insurance-coverage, or billing advice.
- Do not invent clinical facts, diagnoses, trials, failed therapies, contraindications, signatures, or plan criteria.
- Do not submit appeals, portal messages, complaints, or external review requests without explicit authorization.
