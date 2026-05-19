# Employee Offboarding Access Preflight

Catch lingering access, privileged roles, direct-login SaaS accounts, active sessions, unreturned devices, and owned secrets before an offboarding or role-change ticket is closed.

## What It Does

- Joins HR departure rows to account, group, device, and secret-owner exports.
- Flags active access after departure, privileged access, shadow/direct-login SaaS, unrevoked sessions and MFA, sensitive groups, unreturned devices, and unrotated secrets.
- Produces a Markdown closure-gate report with reviewer next steps.
- Runs locally on CSV or JSON exports. It does not call IdP, HRIS, MDM, SaaS, or vault APIs.

## Quick Start

```bash
python3 employee-offboarding-access-preflight/scripts/employee_offboarding_access_preflight.py \
  --departures employee-offboarding-access-preflight/scripts/fixtures/departures.csv \
  --accounts employee-offboarding-access-preflight/scripts/fixtures/accounts.csv \
  --groups employee-offboarding-access-preflight/scripts/fixtures/groups.csv \
  --assets employee-offboarding-access-preflight/scripts/fixtures/assets.csv \
  --secrets employee-offboarding-access-preflight/scripts/fixtures/secrets.csv
```

## Input Fields

```text
departures: email, name, employment_status, termination_date, last_working_day, separation_type, role, department, manager, risk_level, disable_by
accounts: app, email, account_status, role, privileged, sso_managed, last_login_date, session_revoked, mfa_revoked, owner, access_type, license_status, notes
groups: system, email, group, privileged, contains_sensitive_data, owner
assets: asset_id, email, asset_type, status, returned_at, wipe_status, contains_sensitive_data
secrets: secret_id, owner_email, system, secret_type, status, privileged, shared, rotated_at
```

## Output

The report includes:

- Overall offboarding closure decision.
- Finding table with risk, action, source, person, system, evidence, and next step.
- Controls checked and closure gate.
- Open questions when evidence is missing.

## Runtime Notes

- Codex/OpenAI-style agents: use `SKILL.md` and `agents/openai.yaml`.
- Claude Code: copy `.claude/skills/employee-offboarding-access-preflight/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.
- Hermes: see `hermes/README.md`; native packaging is blocked until the current local spec is verified.

## Safety

- Do not paste passwords, private keys, recovery codes, full HR files, or confidential audit evidence into prompts.
- Keep fixture data synthetic.
- The script reads explicit paths and writes only when `--output` is supplied.
- No hidden network calls, telemetry, credentials, or live admin actions are included.
