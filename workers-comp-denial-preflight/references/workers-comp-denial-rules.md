# Workers' Comp Denial Review Rules

This reference is a workflow checklist, not legal or medical advice. Workers' compensation rules vary by state and claim stage.

## Common Denial Themes

| Theme | Evidence to check | Skill action |
|---|---|---|
| Late notice or delayed reporting | Injury date, report date, supervisor notice, incident report, text/email proof, contemporaneous notes. | `employer_dispute_repair` or `deadline_escalation` |
| Injury not work-related | Provider note tying diagnosis to job duty, incident timeline, witness, job description, mechanism of injury. | `medical_causation_repair` |
| Pre-existing condition | Provider explanation distinguishing aggravation/new injury from prior condition, prior relevant records, restriction changes. | `medical_causation_repair` |
| Inadequate medical evidence | Medical record, diagnosis, treatment plan, restrictions, objective findings, follow-up plan. | `medical_causation_repair` |
| Employer disputes facts | Incident report, supervisor notice, time records, witness statement, job-duty proof, photos. | `employer_dispute_repair` |
| Treatment or bill denied | Denial letter, provider bill, EOB, authorization request, medical necessity note, health-insurance/timely-filing trail. | `billing_crossover_review` |
| Hearing or appeal packet | Denial letter, deadline, hearing notice, exhibit list, exchange/delivery proof, witness availability. | `deadline_escalation` or `evidence_exchange_repair` |

## Readiness Tests

- Does the packet include the actual denial letter or written denial reason?
- Are denial date, appeal deadline, hearing date, and review date explicit?
- Does at least one medical record connect injury, work duties, treatment, and restrictions?
- If the employer disputes notice or facts, is there incident-report or supervisor-notice proof?
- If witnesses matter, are names, role, firsthand basis, and availability captured?
- If bills were redirected to the worker or health insurer, are provider bills, EOBs, denial notes, and timely-filing risk tracked?
- If a hearing or appeal is pending, was evidence exchanged with all required parties and is delivery proof available?

## Guardrails

- Do not calculate state-specific legal deadlines unless the user provides an authoritative rule or deadline from the notice. Treat missing or passed deadlines as owner-review escalation.
- Do not decide compensability, impairment, disability, wage-loss entitlement, causation, or legal strategy.
- Do not contact employers, adjusters, agencies, courts, providers, or health insurers.
- Do not create medical opinions. Flag missing provider support and questions to ask the authorized medical or legal owner.
- Redact SSNs, claim numbers, portal credentials, full medical histories, health insurance IDs, bank data, tax identifiers, and unrelated personal data.
