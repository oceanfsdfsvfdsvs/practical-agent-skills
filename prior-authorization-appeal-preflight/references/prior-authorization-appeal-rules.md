# Prior Authorization Appeal Rules

This skill produces an administrative appeal-readiness review. It does not decide clinical necessity, promise coverage, submit appeals, or provide legal advice.

## Denial Reason Taxonomy

| Denial reason | Evidence usually needed | Common missing pieces | Unsafe shortcut |
|---|---|---|---|
| `medical_necessity` | Denial letter, payer criteria, chart notes, diagnosis/service match, provider-signed medical necessity letter, objective results when relevant | Criteria not quoted, clinical note does not address each criterion, no risk-of-delay statement | Asserting "doctor ordered it" without mapping criteria |
| `step_therapy` | Required alternatives, trial dates, dose/duration, outcomes, failures, intolerance, contraindications, continuation history | Saying alternatives failed without dates or records | Inventing failed therapies or side effects |
| `missing_information` | Denial letter, exact missing item list, records/evidence index, fax/portal/call receipts | Resubmitting the same packet without addressing the listed gap | Treating it like a clinical denial |
| `coding_or_site_mismatch` | CPT/HCPCS/NDC, units, site of service, provider type, scheduled date, referral/order | Approved code differs from billed/requested code, wrong site, expired auth | Appealing before reconciling the request |
| `quantity_or_dose_limit` | Dose/unit rationale, label/criteria support, prior response, adverse event or failure at lower dose | No quantity rationale or objective response measure | Asking for exception without criterion mapping |
| `continuation_or_renewal` | Current benefit, stable response, prior approval, why interruption is risky, updated clinical notes | Current note only says condition improved, not why therapy continues | Letting renewal look like a new-start request |
| `network_or_referral` | Referral/order, network status, facility/provider identifiers, emergency or continuity context | Missing referral or out-of-network rationale | Ignoring plan routing requirements |

## Readiness Gates

Block submission when:

- Written denial/adverse determination is missing.
- Appeal deadline is passed and no late-appeal, grievance, external review, or resubmission path is identified.
- Third-party requester lacks representative authorization.
- Medical necessity or continuation denial lacks relevant records or provider-signed rationale.
- Step therapy denial lacks trial/failure/intolerance/contraindication evidence.
- Prior appeal was rejected and the new packet does not address the rejection reason.
- The user asks the agent to submit a live portal/fax/email action.

Route to review when:

- Deadline is within 7 days.
- Payer criteria are missing or unmapped.
- Objective support is missing for imaging, procedure, therapy, or DME requests.
- Code, unit, site, provider type, or quantity mismatch is suspected.
- Urgent handling is requested without clinician support.
- Peer-to-peer request or outcome is not logged.

## Owner Questions

Ask these before drafting:

- What exactly did the denial letter say, and what deadline/path does it give?
- Which plan criterion is disputed or unmet?
- Which document proves each criterion?
- If step therapy is involved, what alternatives were required, tried, failed, not tolerated, or contraindicated?
- If continuation is involved, what evidence shows benefit and risk of interruption?
- Who is authorized to file or speak with the plan?

## Baseline Prompt Failure Modes

A generic prompt often:

- Drafts a persuasive letter before checking deadline, authority, or denial category.
- Confuses billing/EOB disputes with prior authorization appeals.
- Omits payer criteria mapping and step-therapy evidence.
- Gives overconfident coverage or legal conclusions.
- Fails to flag live portal submission as an owner-only action.
