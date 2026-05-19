# Offboarding Access Rules

## Risk Signals

| Signal | Why It Matters | Default Action |
|---|---|---|
| Active privileged account after departure | Admin, owner, production, billing, or security roles can cause immediate damage. | `revoke_now` |
| Direct-login or non-SSO SaaS account | IdP disablement may not revoke standalone credentials. | `revoke_now` |
| Session or MFA not revoked | Disabled accounts can leave browser sessions, device tokens, or recovery paths usable. | `revoke_now` |
| Sensitive group membership after departure or transfer | Old role access can persist even when base identity is disabled. | `revoke_now` |
| Active owned secret, token, API key, or shared credential | Departing owners can retain long-lived access outside human account lifecycle controls. | `rotate_or_reassign_secret` |
| Unreturned device, badge, hardware token, or BYOD access | Physical and local data access can survive account disablement. | `recover_or_wipe_device` |
| Missing termination date or ambiguous HR status | Reviewers cannot prove timing or closure completeness. | `secondary_verification` |
| Internal transfer with old-role access | Role changes often bypass leaver workflows. | `secondary_verification` |

## Closure Criteria

Do not close an offboarding or role-change access review until:

- HR event, last working date, and access-disable deadline are recorded.
- Base IdP, email, VPN/ZTNA, endpoint, and critical SaaS accounts are disabled or transferred.
- Sessions, MFA, recovery methods, device tokens, and app passwords are revoked where export evidence exists.
- Direct-login SaaS accounts are disabled separately from IdP-controlled accounts.
- Privileged groups, production roles, repo/admin groups, and billing owner roles are removed or exception-approved.
- Secrets, API tokens, CI/CD credentials, personal access tokens, and shared vault entries owned by the departing person are rotated or reassigned.
- Devices, badges, hardware keys, and corporate mobile profiles are returned, wiped, or exception-documented.
- Reviewer signoff and evidence links are archived outside the prompt transcript.

## False Positives To Check

- Break-glass accounts with documented shared ownership.
- Service accounts incorrectly assigned to a human owner but already rotated.
- Legal hold, audit, payroll, or email-retention accounts that are intentionally suspended rather than deleted.
- Future-dated voluntary departures where knowledge transfer is still in progress.
- Contractors with renewed engagement under a different identity.

## Prompt Baseline Failure Modes

A plain prompt often says "disable accounts and collect laptop" but misses:

- Shadow SaaS and direct-login accounts outside SSO.
- Session, MFA, recovery method, and device-token revocation.
- Secrets and API keys owned by the departing person.
- Internal transfer access that is not triggered by termination workflows.
- Row-level closure gates that tell the reviewer exactly what must happen before ticket closure.
