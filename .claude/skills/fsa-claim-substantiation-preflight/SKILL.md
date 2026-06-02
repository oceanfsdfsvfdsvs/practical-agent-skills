---
name: fsa-claim-substantiation-preflight
description: Review Health FSA, Limited Purpose FSA, Dependent Care FSA, HRA, or HSA reimbursement packets before submission or debit-card substantiation. Use when employees, caregivers, HR benefits teams, or benefits administrators need to catch missing EOBs, itemized receipt fields, service-date/coverage-period issues, LMN gaps, dependent-care provider certification gaps, duplicate reimbursement risk, and live-portal guardrails without logging into benefit portals.
---

# FSA Claim Substantiation Preflight

This is the Claude Code mirror for `fsa-claim-substantiation-preflight`.

Use the canonical skill directory at:

```text
fsa-claim-substantiation-preflight/
```

Keep the full repository available when running scripts so relative paths resolve correctly.

Smoke test:

```bash
python3 fsa-claim-substantiation-preflight/scripts/fsa_claim_substantiation_preflight.py \
  --claims fsa-claim-substantiation-preflight/scripts/fixtures/fsa_claims.csv \
  --evidence-dir fsa-claim-substantiation-preflight/scripts/fixtures/evidence \
  --today 2026-06-03
```

Read `fsa-claim-substantiation-preflight/SKILL.md` for the full workflow, boundaries, examples, and output format.
