---
name: saas-license-rightsize
description: Audit SaaS license exports, HR rosters, and usage CSVs to find reclaim, downgrade, duplicate-account, departed-employee, stale-admin, and owner-review opportunities. Use when IT, finance, procurement, MSP, or operations teams need a local-first license rightsize report before renewals, QBRs, budget reviews, or access cleanup without calling vendor APIs.
---

# SaaS License Rightsize

Use this skill to turn local SaaS admin exports, HR rosters, and usage reports into a reviewable license rightsize plan. The goal is to reclaim or downgrade seats with evidence, not to blindly remove access because a user looks inactive.

Run the bundled local audit when files exist:

```bash
python3 saas-license-rightsize/scripts/saas_license_rightsize.py \
  --licenses /absolute/path/licenses.csv \
  --employees /absolute/path/employees.csv \
  --usage /absolute/path/usage.csv \
  --today 2026-05-17
```

Use for license exports, SSO exports, HR rosters, usage files, and renewal or budget reviews. Do not use for live account changes unless the user explicitly authorizes the exact changes.

Classify findings as `reclaim_now`, `reclaim_or_downgrade`, `downgrade_review`, `merge_or_reclaim_duplicate`, `access_review`, `verify_identity_or_owner`, `owner_review`, or `monitor`.

Before recommending removal, check owner, HR status, role, usage evidence, contract constraints, and exception categories such as service accounts, break-glass accounts, legal/compliance accounts, executives, seasonal users, and users on leave.

Return:

```markdown
## License Portfolio Decision
[Immediate reclaim review / Owner review needed / Monitor only]

## Savings Summary
[Potential annual savings, high-risk seats, missing evidence]

## Seat Exceptions
| Risk | Action | App | Email | Plan | Role | Annual cost | Evidence | Next step |
|---|---|---|---|---|---|---:|---|---|

## Owner Action Plan
[One action per finding]

## Guardrails
[Do-not-remove categories, source limits, approval requirements]
```

Validation fixture:

```bash
python3 saas-license-rightsize/scripts/saas_license_rightsize.py \
  --licenses saas-license-rightsize/scripts/fixtures/licenses.csv \
  --employees saas-license-rightsize/scripts/fixtures/employees.csv \
  --usage saas-license-rightsize/scripts/fixtures/usage.csv \
  --today 2026-05-17
```
