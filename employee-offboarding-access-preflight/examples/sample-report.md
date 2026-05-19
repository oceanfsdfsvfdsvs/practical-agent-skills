## Offboarding Access Decision
Hold closure - 7 critical/high findings require revocation, rotation, recovery, or evidence before the offboarding review can close.

## Departure Findings
| Risk | Action | Source | Person | System | Evidence | Reviewer next step |
|---|---|---|---|---|---|---|
| critical | revoke_now | accounts row 2 | alex.left@example.com | GitHub | active_account_after_departure, privileged_access_after_departure, session_not_revoked | Disable account or remove access, revoke sessions/MFA, and archive reviewer evidence. |
| critical | revoke_now | accounts row 3 | alex.left@example.com | Figma | active_account_after_departure, shadow_saas_or_direct_login | Disable direct-login account outside SSO and preserve closure evidence. |
| critical | rotate_or_reassign_secret | secrets row 2 | alex.left@example.com | GitHub Actions | active_secret_owned_by_departing_person, privileged_secret | Rotate or reassign the secret and record the new owner. |
| high | recover_or_wipe_device | assets row 2 | alex.left@example.com | MacBook MDM-991 | device_not_returned, wipe_not_confirmed | Recover, lock, or wipe the device and preserve MDM evidence. |

## Controls Checked
HR trigger, IdP/account disablement, session/MFA revocation, SSO/direct-login coverage, groups, secrets, devices, ownership transfer.

## Closure Gate
- Resolve all `critical` and `high` rows before marking the ticket complete.
- Archive evidence links in the HR/ITSM/GRC ticket outside the prompt transcript.
