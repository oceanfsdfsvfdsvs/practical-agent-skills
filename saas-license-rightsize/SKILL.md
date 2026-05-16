---
name: saas-license-rightsize
description: Audit SaaS license exports, HR rosters, and usage CSVs to find reclaim, downgrade, duplicate-account, departed-employee, stale-admin, and owner-review opportunities. Use when IT, finance, procurement, MSP, or operations teams need a local-first license rightsize report before renewals, QBRs, budget reviews, or access cleanup without calling vendor APIs.
---

# SaaS License Rightsize

## Overview

Use this skill to turn local SaaS admin exports, HR rosters, and usage reports into a reviewable license rightsize plan. The goal is to reclaim or downgrade seats with evidence, not to blindly remove access because a user looks inactive.

## Use And Do Not Use

Use for:

- SaaS app license exports, SSO exports, HR rosters, finance spend files, or manually prepared CSV/JSON tables.
- Finding active seats assigned to departed employees or unknown identities.
- Finding inactive, never-used, duplicated, over-tiered, or stale-admin seats.
- Estimating reclaim or downgrade savings before renewal, quarterly budget review, MSP QBR, or access cleanup.
- Producing owner-ready actions with guardrails for exceptions.

Do not use for:

- Removing licenses, disabling users, or changing vendor admin settings without explicit authorization.
- Legal, procurement, tax, or HR advice.
- Sending confidential employee data to third-party services.
- Treating low activity as proof that a seat is unnecessary when seasonal, compliance, executive, break-glass, or audit-access exceptions may apply.
- Replacing a full SAM/SaaS management platform for enterprises that need live discovery, integrations, approval workflows, and audit trails.

## Required Inputs

Ask only for missing inputs that materially change the decision:

- License export path with app, email, plan/tier, status, role, cost, owner, department, and renewal fields when available.
- HR roster path with email, employee status, department, manager, and termination date when available.
- Usage export path with app, email, last login, activity count, usage minutes, or feature events.
- Review date, if not today.
- Inactivity thresholds, if the company has a policy. Default to 60 days for review and 90 days for reclaim candidates.
- High-cost or high-risk apps where owner review should be stricter.

If the user only has one file, produce a limited report and state which checks could not run.

## Workflow

### 1. Preserve Evidence And Boundaries

Capture:

- Data source names and export dates when available.
- Whether cost is monthly, annual, or missing.
- Whether HR status is authoritative or only inferred.
- Whether usage is last login, events, minutes, admin activity, or billing activity.
- App owner and department, especially for high-cost or admin seats.

Read `references/license-risk-rules.md` before classifying executive, legal, compliance, break-glass, seasonal, or service-account seats.

### 2. Run The Local Audit When Files Exist

Use explicit relative or absolute paths:

```bash
python3 saas-license-rightsize/scripts/saas_license_rightsize.py \
  --licenses /absolute/path/licenses.csv \
  --employees /absolute/path/employees.csv \
  --usage /absolute/path/usage.csv \
  --today 2026-05-17
```

CSV and JSON inputs are supported. Preferred fields:

```text
licenses: app, email, user_name, plan, license_status, role, monthly_cost, annual_cost,
          currency, department, owner, renewal_date, contract_id
employees: email, employee_status, department, manager, termination_date
usage: app, email, last_login_date, activity_count_30d, usage_minutes_30d,
       feature_events_30d
```

### 3. Classify Seat Risk

Use one primary action:

- `reclaim_now`: active paid seat belongs to a departed employee or an obvious inactive paid account.
- `reclaim_or_downgrade`: materially inactive paid seat after the reclaim threshold.
- `downgrade_review`: premium tier or high-cost seat has low usage but may still need owner confirmation.
- `merge_or_reclaim_duplicate`: duplicate assigned accounts exist for the same app and identity.
- `access_review`: stale admin, owner, or privileged role should be reviewed even if cost is low.
- `verify_identity_or_owner`: license is active but HR/owner mapping is missing.
- `owner_review`: evidence is mixed or an exception may apply.
- `monitor`: no material reclaim signal appears.

Never recommend removal without an owner, HR, usage, and exception check for privileged, compliance, legal, executive, seasonal, or service-account seats.

### 4. Produce The Rightsize Plan

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
[One action per reclaim, downgrade, duplicate, or privileged access finding]

## Guardrails
[Do-not-remove categories, source limits, approval requirements]
```

Use `templates/reclaim-plan.md` when the user asks for a reusable artifact.

## Examples And Acceptance Checks

Positive example: "Use $saas-license-rightsize on these Google Workspace, Slack, and HR exports before renewal." The skill should join users across exports, flag departed employees, stale admins, premium seats with low usage, and duplicate accounts.

Positive MSP example: "Generate a QBR savings report from a client's Microsoft 365 and HR CSVs." The skill should produce savings estimates and owner actions while avoiding any vendor login or API call.

Negative example: "Delete every inactive user." Do not recommend deletion without checking owner, role, exception category, and approval path.

Boundary example: "I only have a license export." Produce a limited orphan/inactive review checklist and explain that departed-employee and usage checks are unavailable.

## Validation

Smoke-test the bundled fixture:

```bash
python3 saas-license-rightsize/scripts/saas_license_rightsize.py \
  --licenses saas-license-rightsize/scripts/fixtures/licenses.csv \
  --employees saas-license-rightsize/scripts/fixtures/employees.csv \
  --usage saas-license-rightsize/scripts/fixtures/usage.csv \
  --today 2026-05-17
```

Expected result: a Markdown report with `License Portfolio Decision`, `Potential annual savings`, `departed_employee_active_license`, `reclaim_now`, and `downgrade_review`.
