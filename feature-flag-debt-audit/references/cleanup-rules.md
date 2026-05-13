# Feature Flag Cleanup Rules

## Flag Types

- `release`: temporary rollout toggle. Usually removable after launch is complete and stable.
- `experiment`: A/B or holdout flag. Usually removable after analysis, decision, and metric archival.
- `migration`: temporary dual-write, dual-read, schema, or backfill gate. Requires data and rollback checks.
- `ops`: kill switch, throttling, circuit breaker, or incident response guard. Treat as permanent unless owner approves.
- `entitlement`: customer, plan, region, compliance, or permission gate. Do not treat as debt without product approval.

## Safe Delete Signals

Strong delete candidates usually have several of these:

- Status is launched, complete, archived, inactive, or deprecated.
- Expiry date is in the past.
- Last-seen or evaluation date is older than the stale policy.
- Owner exists and owns the cleanup path.
- Code references are absent or isolated.
- Description confirms the rollout or experiment is complete.

## Owner Review Signals

Require owner review when:

- Owner is missing.
- Last-seen data is missing or untrusted.
- References appear in security, billing, auth, migration, or compliance paths.
- The flag name contains `kill`, `ops`, `guard`, `perm`, `entitlement`, `migration`, `billing`, `auth`, or `security`.
- The flag still has many code references or appears in tests only.

## Failure Modes To Prevent

- Deleting a kill switch because it has low traffic during normal operation.
- Removing only the flag configuration while leaving dead code branches in the app.
- Removing code before confirming the desired permanent branch.
- Treating missing evaluation telemetry as proof of no use.
- Deleting experiment flags before results, holdouts, or metric annotations are archived.
- Combining many unrelated flag deletions into one unreviewable pull request.

## Cleanup Ticket Requirements

Each cleanup ticket should include:

- Flag key, owner, status, type, and stale evidence.
- Files that reference the flag.
- Desired permanent branch after removal.
- Tests or smoke checks to run.
- Rollback action if production behavior changes.
- Expiry for the cleanup decision if owner review is not completed.
