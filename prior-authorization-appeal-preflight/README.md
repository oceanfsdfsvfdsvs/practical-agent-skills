# Prior Authorization Appeal Preflight

Review prior authorization denials before resubmitting an appeal packet.

This skill is for patients, caregivers, benefits advocates, small clinics, and HR benefits helpers who need a structured local review of prior authorization denials without logging into insurer portals. It turns case tables and redacted evidence files into a blocker-focused appeal readiness report.

## What It Catches

- Missing written denial/adverse determination or appeal deadline.
- Missing representative authorization for caregivers or third-party helpers.
- Missing payer criteria mapping.
- Medical necessity packets without provider-signed support or relevant records.
- Step-therapy packets without trial, failure, intolerance, or contraindication proof.
- Code, unit, site-of-service, provider-type, or quantity-limit mismatches.
- Urgent cases without expedited-review support.
- Repeated appeals that do not answer the prior rejection.
- Unsafe requests to submit live portal actions.

## Quick Start

```bash
python3 prior-authorization-appeal-preflight/scripts/prior_authorization_appeal_preflight.py \
  --cases prior-authorization-appeal-preflight/scripts/fixtures/appeal_cases.csv \
  --evidence-dir prior-authorization-appeal-preflight/scripts/fixtures/evidence \
  --today 2026-06-02
```

Input may be CSV or JSON. Preferred fields:

```text
case_id, patient_role, plan_type, stage, service_type, requested_service,
diagnosis_code, procedure_code, denial_reason, denial_date, appeal_deadline,
urgent, denial_letter, medical_records, letter_of_medical_necessity,
payer_criteria, step_therapy_required, failed_alternatives_documented,
objective_results, representative_authorization, peer_to_peer_requested,
patient_safety_risk
```

## Output

The script produces a Markdown report with:

- Overall appeal decision.
- Case and blocker summary.
- Row-level findings with flags and next steps.
- Appeal packet checklist.
- Privacy, authority, and medical/legal/coverage guardrails.

## Runtime Notes

- Codex/OpenAI: use `SKILL.md` and `agents/openai.yaml`.
- Claude Code: use `.claude/skills/prior-authorization-appeal-preflight/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.
- Hermes: see `hermes/README.md`; native Hermes packaging is blocked until a current local spec is available.

## Safety

- This is administrative workflow support, not medical, legal, billing, insurance-coverage, or clinical advice.
- The script does not call insurer portals, provider portals, government systems, email, fax, or payment systems.
- Do not paste uncensored PHI, full member IDs, SSNs, credentials, payment card data, secrets, or private legal advice into public prompts.
- Keep final appeal, external review, grievance, portal, fax, and treatment decisions with the authorized owner.
