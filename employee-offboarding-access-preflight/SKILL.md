---
name: employee-offboarding-access-preflight
description: Audit employee or contractor offboarding exports for lingering access, privileged roles, direct-login SaaS accounts, active sessions, unreturned assets, and unrotated secrets before a departure or role-change access review is closed. Use when IT, security, HR ops, MSP, founders, or compliance owners need a local-first deprovisioning evidence report without connecting to an IdP, HRIS, MDM, or SaaS admin API.
---

# Employee Offboarding Access Preflight

## Overview

Use this skill to turn HR, identity, SaaS, group, device, and secret-owner exports into a reviewable offboarding access report. The goal is to catch lingering access before a termination, contractor exit, or role-change ticket is closed, while preserving enough evidence for IT, security, HR, or audit reviewers.

## Use And Do Not Use

Use for:

- Employee, contractor, intern, vendor, or admin departures.
- Internal transfers where old role-based access must be removed.
- HRIS, IdP, SaaS admin, group membership, device/MDM, password vault, or secrets inventory exports.
- Finding active accounts after departure, privileged roles, non-SSO direct logins, active sessions, MFA/recovery gaps, owned secrets, unreturned devices, and evidence gaps.
- Producing a hold/revoke/verify report before an offboarding ticket is marked complete.

Do not use for:

- Logging into HRIS, IdP, MDM, password vault, or SaaS admin systems.
- Automatically disabling accounts, wiping devices, rotating keys, or changing group membership.
- Employment, legal, or disciplinary decisions. Label findings as access-control risk unless confirmed by the user.
- Storing raw passwords, private keys, full secret values, personal documents, or confidential HR evidence in prompts or fixtures.

## Required Inputs

Ask only for missing inputs that materially affect the review:

- Departure roster path with work email, status, termination or transfer date, separation type, role, manager, and risk level when available.
- Account export path with app, email, account status, role, SSO/direct-login status, session and MFA revocation status when available.
- Optional group, device, and secret-owner exports.
- Policy thresholds: immediate termination handling, transfer review window, privileged access tolerance, post-departure verification window.
- Output preference: Markdown report, copied table, or saved file.

Preferred fields:

```csv
departures: email,name,employment_status,termination_date,last_working_day,separation_type,role,department,manager,risk_level,disable_by,knowledge_transfer_owner
accounts: app,email,account_status,role,privileged,sso_managed,last_login_date,session_revoked,mfa_revoked,owner,access_type,license_status,notes
groups: system,email,group,privileged,contains_sensitive_data,owner
assets: asset_id,email,asset_type,status,returned_at,wipe_status,contains_sensitive_data
secrets: secret_id,owner_email,system,secret_type,status,privileged,shared,rotated_at
```

## Workflow

### 1. Preserve The Access-Control Boundary

Before classifying risk, capture:

- Person, employment status, last working date, separation type, manager, and risk level.
- Account status, direct-login/SSO coverage, privileged role, active session, MFA, and last-login evidence.
- Group memberships, shared mailbox or repo ownership, device return/wipe state, and secret/API-key ownership.
- Which reviewer can revoke, rotate, transfer, or document each item.

Do not ask for passwords, private key material, recovery codes, full HR files, or live admin access.

### 2. Run The Local Preflight

Use explicit paths:

```bash
python3 employee-offboarding-access-preflight/scripts/employee_offboarding_access_preflight.py \
  --departures /absolute/path/departures.csv \
  --accounts /absolute/path/accounts.csv \
  --groups /absolute/path/groups.csv \
  --assets /absolute/path/assets.csv \
  --secrets /absolute/path/secrets.csv
```

The script accepts CSV or JSON. JSON may be a list of row objects or an object containing `departures`, `accounts`, `groups`, `assets`, `secrets`, `rows`, or `items`.

### 3. Classify Findings

Use one primary action:

- `revoke_now`: active account, privileged role, session, MFA, group, or direct login must be revoked before closure.
- `rotate_or_reassign_secret`: secret, token, API key, integration owner, shared credential, or service credential needs rotation or ownership transfer.
- `recover_or_wipe_device`: device, badge, hardware token, or BYOD access remains unreturned or unwiped.
- `secondary_verification`: evidence is incomplete, status is ambiguous, or transfer timing needs human confirmation.
- `document_complete`: supplied evidence shows access was revoked, transferred, or recovered.

Use one risk level:

- `critical`: active privileged access, active non-SSO login, unrevoked session/MFA, active owned secret, or sensitive group remains after departure.
- `high`: active standard account after departure, pending departure within the policy window, unreturned sensitive asset, missing direct-login evidence, or unknown employment status.
- `medium`: ownership transfer, stale membership, inactive account with missing evidence, or non-sensitive asset/documentation gap.
- `low`: complete but needs audit note, reviewer signoff, or post-departure scan.

Never say offboarding is complete while `critical` or `high` findings remain unresolved.

### 4. Produce The Review Report

Return:

```markdown
## Offboarding Access Decision
[Hold closure / Revocation required / Secondary verification required / Evidence complete]

## Departure Findings
| Risk | Action | Source | Person | System | Evidence | Reviewer next step |
|---|---|---|---|---|---|---|

## Controls Checked
[HR trigger, IdP/account disablement, session/MFA revocation, SSO/direct-login coverage, groups, secrets, devices, ownership transfer]

## Closure Gate
[Items that must be revoked, rotated, recovered, transferred, or evidenced before closure]

## Open Questions
[Only questions that affect access-control safety]
```

Use `templates/offboarding-review.md` when the user asks for a reusable IT/security review artifact.

### 5. Apply Guardrails Before Advising Closure

Do not advise closure until:

- Terminated users have no active account, active privileged role, active group membership, direct-login bypass, unrevoked session, or MFA recovery method in supplied exports.
- Shared credentials, service accounts, API keys, and integration owners are rotated or reassigned.
- Devices, badges, hardware tokens, and BYOD access are returned, wiped, or explicitly exception-approved.
- Internal transfers have old-role access removed or exception-documented.
- Evidence is archived in the ticketing, HR, IdP, or GRC system outside the prompt transcript.

## Examples And Acceptance Checks

Positive example: "Use $employee-offboarding-access-preflight on this HR departure roster and Okta, GitHub, Slack, MDM, and vault exports." The skill should run the script, catch lingering privileged access and direct-login accounts, and produce revoke/rotate/recover rows.

Positive transfer example: "Review this engineer-to-PM transfer before the role-change ticket closes." The skill should flag old engineering groups, repo admin roles, production secrets, and ownership transfer gaps.

Negative example: "Disable this person's account for me." Do not modify live systems; produce a review report only.

Boundary example: "I only have an HR roster." Produce a limited closure checklist and explain that account, group, device, and secret checks are unavailable.

## Validation

Smoke-test the bundled fixture:

```bash
python3 employee-offboarding-access-preflight/scripts/employee_offboarding_access_preflight.py \
  --departures employee-offboarding-access-preflight/scripts/fixtures/departures.csv \
  --accounts employee-offboarding-access-preflight/scripts/fixtures/accounts.csv \
  --groups employee-offboarding-access-preflight/scripts/fixtures/groups.csv \
  --assets employee-offboarding-access-preflight/scripts/fixtures/assets.csv \
  --secrets employee-offboarding-access-preflight/scripts/fixtures/secrets.csv
```

Expected result: a Markdown report with `Offboarding Access Decision`, `revoke_now`, `rotate_or_reassign_secret`, `shadow_saas_or_direct_login`, and `privileged_access_after_departure`.
