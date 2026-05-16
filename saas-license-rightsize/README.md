# SaaS License Rightsize

Find reclaim, downgrade, duplicate-account, stale-admin, and departed-employee risks from local SaaS license exports before renewals or budget reviews.

This skill is for IT, finance, procurement, operations, founders, and MSP teams that have CSV/JSON exports from SaaS admin consoles, HR systems, SSO tools, or spreadsheets. It produces an owner-ready license rightsize plan without logging into vendor systems or calling SaaS APIs.

## What It Catches

- Active paid seats assigned to departed employees.
- Paid seats with no usage, stale usage, or no matching HR record.
- Premium tiers with low activity that may be downgrade candidates.
- Duplicate accounts for the same app and identity.
- Stale admin or owner roles that need access review.
- Missing owner, department, cost, or renewal evidence.

## Quick Start

```bash
python3 saas-license-rightsize/scripts/saas_license_rightsize.py \
  --licenses saas-license-rightsize/scripts/fixtures/licenses.csv \
  --employees saas-license-rightsize/scripts/fixtures/employees.csv \
  --usage saas-license-rightsize/scripts/fixtures/usage.csv \
  --today 2026-05-17
```

Preferred fields:

```text
licenses: app, email, user_name, plan, license_status, role, monthly_cost,
annual_cost, currency, department, owner, renewal_date, contract_id

employees: email, employee_status, department, manager, termination_date

usage: app, email, last_login_date, activity_count_30d, usage_minutes_30d,
feature_events_30d
```

## Output

The script produces a Markdown report with:

- Portfolio decision.
- Potential annual savings.
- Seat exception table.
- Owner action plan.
- Guardrails for exceptions and approval.

## Safety

- This is IT/finance operations support, not legal, HR, or procurement advice.
- The script does not call vendor APIs, disable users, send emails, or require credentials.
- Do not paste raw secrets, private keys, full employee files, or confidential audit evidence into public prompts.
- Treat usage-only evidence as provisional until the app owner confirms seasonal, compliance, executive, service-account, and break-glass exceptions.
