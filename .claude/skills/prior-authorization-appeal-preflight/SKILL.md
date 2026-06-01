---
name: prior-authorization-appeal-preflight
description: Review prior authorization denials for medications, imaging, procedures, therapy, DME, or services before an appeal is submitted. Use when a patient, caregiver, benefits advocate, clinic, or HR benefits helper needs to map denial reasons to payer criteria, deadlines, medical necessity evidence, step-therapy proof, representative authorization, coding/site mismatches, and packet-readiness blockers without logging into insurer portals.
---

# Prior Authorization Appeal Preflight

Use the repository skill at `prior-authorization-appeal-preflight/SKILL.md`.

When script-backed validation is useful, run:

```bash
python3 prior-authorization-appeal-preflight/scripts/prior_authorization_appeal_preflight.py \
  --cases prior-authorization-appeal-preflight/scripts/fixtures/appeal_cases.csv \
  --evidence-dir prior-authorization-appeal-preflight/scripts/fixtures/evidence \
  --today 2026-06-02
```

Preserve privacy boundaries, do not submit live portal/fax/email actions, and do not provide medical, legal, insurance-coverage, or guaranteed appeal-outcome advice.
