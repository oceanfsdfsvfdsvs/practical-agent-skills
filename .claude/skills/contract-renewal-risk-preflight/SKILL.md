---
name: contract-renewal-risk-preflight
description: Preflight vendor and SaaS contract renewals for auto-renewal, cancellation notice, stale owner, notice-method, spend, and usage-risk gaps. Use when procurement, finance, IT, ops, or founders need an owner-ready renewal action plan from local spreadsheets or contract extracts without contacting vendors or giving legal advice.
---

# Contract Renewal Risk Preflight

Use the repository skill at `contract-renewal-risk-preflight/SKILL.md`.

Keep the full skill directory available so relative paths to `scripts/`, `references/`, `templates/`, and `examples/` resolve correctly.

Start with the local fixture check when validating installation:

```bash
python3 contract-renewal-risk-preflight/scripts/contract_renewal_risk_preflight.py \
  --contracts contract-renewal-risk-preflight/scripts/fixtures/contracts.csv \
  --today 2026-05-16
```

Do not send vendor notices or provide legal advice. Produce an operational renewal-risk plan and escalate legal questions.
