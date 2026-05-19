---
name: employee-offboarding-access-preflight
description: Audit employee or contractor offboarding exports for lingering access, privileged roles, direct-login SaaS accounts, active sessions, unreturned assets, and unrotated secrets before a departure or role-change access review is closed. Use when IT, security, HR ops, MSP, founders, or compliance owners need a local-first deprovisioning evidence report without connecting to an IdP, HRIS, MDM, or SaaS admin API.
---

# Employee Offboarding Access Preflight

Use this skill when reviewing employee, contractor, admin, or role-change offboarding evidence. Keep the full repository available so relative paths to `scripts/`, `templates/`, `references/`, and `examples/` resolve.

## Workflow

1. Ask for a departure roster and available access exports: accounts, groups, devices/assets, and secret-owner inventory.
2. Do not request passwords, private keys, recovery codes, full HR files, or live admin access.
3. Run the local script with explicit relative or absolute paths:

```bash
python3 employee-offboarding-access-preflight/scripts/employee_offboarding_access_preflight.py \
  --departures /path/to/departures.csv \
  --accounts /path/to/accounts.csv \
  --groups /path/to/groups.csv \
  --assets /path/to/assets.csv \
  --secrets /path/to/secrets.csv
```

4. Classify rows using one primary action: `revoke_now`, `rotate_or_reassign_secret`, `recover_or_wipe_device`, `secondary_verification`, or `document_complete`.
5. Never say offboarding is complete while critical or high findings remain unresolved.
6. Return a Markdown report with `Offboarding Access Decision`, `Departure Findings`, `Controls Checked`, `Closure Gate`, and `Open Questions`.

## Guardrails

- Do not log into HRIS, IdP, MDM, vault, or SaaS admin systems.
- Do not disable accounts, wipe devices, rotate keys, or remove groups directly.
- Label findings as access-control risk, not employment or legal determinations.
- Archive evidence in the user's HR/ITSM/GRC system outside the prompt transcript.

## Validation

```bash
python3 employee-offboarding-access-preflight/scripts/employee_offboarding_access_preflight.py \
  --departures employee-offboarding-access-preflight/scripts/fixtures/departures.csv \
  --accounts employee-offboarding-access-preflight/scripts/fixtures/accounts.csv \
  --groups employee-offboarding-access-preflight/scripts/fixtures/groups.csv \
  --assets employee-offboarding-access-preflight/scripts/fixtures/assets.csv \
  --secrets employee-offboarding-access-preflight/scripts/fixtures/secrets.csv
```

Expected output includes `Offboarding Access Decision`, `revoke_now`, `rotate_or_reassign_secret`, `shadow_saas_or_direct_login`, and `privileged_access_after_departure`.
