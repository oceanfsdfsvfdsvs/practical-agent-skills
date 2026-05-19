# Offboarding Access Review

## Offboarding Access Decision

Decision:

Review date:

Reviewer:

Scope:

## Departure Findings

| Risk | Action | Source | Person | System | Evidence | Reviewer next step |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

## Controls Checked

- HR trigger and last working date:
- IdP and email account disablement:
- SaaS direct-login coverage:
- Privileged roles and groups:
- Session, MFA, and recovery revocation:
- Secrets, tokens, and shared credentials:
- Devices, badges, and hardware tokens:
- Ownership transfer:
- Evidence archived:

## Closure Gate

Items required before closure:

1. 
2. 
3. 

## Open Questions

- 

## Rerun Command

```bash
python3 employee-offboarding-access-preflight/scripts/employee_offboarding_access_preflight.py \
  --departures /path/to/departures.csv \
  --accounts /path/to/accounts.csv \
  --groups /path/to/groups.csv \
  --assets /path/to/assets.csv \
  --secrets /path/to/secrets.csv
```
