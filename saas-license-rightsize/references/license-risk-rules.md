# License Risk Rules

Use these rules when deciding whether a SaaS seat should be reclaimed, downgraded, reviewed, or left alone.

## Strong Reclaim Signals

| Signal | Why It Matters | Recommended Action |
|---|---|---|
| Active paid seat mapped to departed employee | Direct spend waste and lingering access risk. | `reclaim_now` after HR/offboarding confirmation. |
| No usage for 90+ days on a paid non-exception seat | Strong evidence that the seat may not be needed. | `reclaim_or_downgrade` with owner confirmation. |
| Duplicate accounts for the same app and email | One identity may be paying twice or keeping stale access. | `merge_or_reclaim_duplicate`. |
| Unknown employee with paid access | Could be contractor, alias, service account, or orphan. | `verify_identity_or_owner` before removal. |
| Stale admin or owner role | Access risk may matter even when license cost is low. | `access_review`; do not auto-remove. |

## Downgrade Signals

- Premium, pro, business, enterprise, admin, or creator tiers with low feature events.
- High-cost seats with light login-only usage.
- Users whose work only needs viewer/commenter/read-only access.
- Teams with many premium seats but concentrated real activity in a small group.

Estimate downgrade savings conservatively unless the lower-tier price is known. A 50% estimate is only a planning placeholder, not a finance booking number.

## Exception Categories

Do not recommend direct reclaim without owner review for:

- Executive, board, legal, finance close, audit, compliance, or regulatory seats.
- Break-glass, service, integration, bot, automation, mailbox, scanner, or shared accounts.
- Seasonal or quarterly users whose usage window is outside the export period.
- Users on leave, onboarding, role transition, or pending termination.
- Seats tied to contract minimums, true-up rules, bundled suites, or annual non-cancelable commitments.

## Evidence Quality

High confidence usually requires:

- License status and cost.
- HR status or owner confirmation.
- Usage recency and activity volume.
- Role/tier.
- App owner or department.

If one of these is missing, lower confidence and route to owner review.

## Common Failure Modes

- Treating last login as the only value signal for tools that work through integrations or APIs.
- Removing an admin account before confirming break-glass coverage.
- Counting annual savings that cannot be realized until renewal.
- Ignoring contract seat minimums.
- Using personal email aliases without mapping them to real employees.
- Sending private employee exports to a cloud tool without approval.
