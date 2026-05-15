# Contract Renewal Risk Preflight

Find vendor contract renewal risk before an auto-renewal or cancellation notice deadline removes your leverage.

This skill is for procurement, finance, IT, operations, founders, and legal-ops teams that track vendor agreements in spreadsheets, CLM exports, SaaS management tools, or shared drives. It turns contract fields into an owner-ready renewal action plan.

## What It Catches

- Notice deadlines derived from renewal date minus required notice days.
- Missed or imminent auto-renewal windows.
- Missing owner, stale owner, missing notice method, or missing notice recipient.
- High-spend contracts with uncapped price increases.
- Low-usage or duplicate-tool notes that should trigger cancel or renegotiate review.

## Quick Start

```bash
python3 contract-renewal-risk-preflight/scripts/contract_renewal_risk_preflight.py \
  --contracts contract-renewal-risk-preflight/scripts/fixtures/contracts.csv \
  --today 2026-05-16
```

Input may be CSV or JSON. Preferred fields:

```text
vendor, contract_id, owner, department, annual_cost, currency, renewal_date,
notice_days, notice_deadline, auto_renew, renewal_term, price_increase_cap,
termination_notice_method, notice_address, last_review_date, usage_status, notes
```

## Output

The script produces a Markdown report with:

- Portfolio decision.
- Risk summary.
- Renewal exception table.
- Owner action plan.
- Guardrails for notice proof and legal review.

## Safety

- This is procurement operations support, not legal advice.
- The script does not call vendor APIs, send notices, write to SaaS systems, or require credentials.
- Do not paste confidential full contracts, secrets, customer data, or private legal advice into public prompts.
- Treat spreadsheet-only clause data as provisional until checked against the contract.
