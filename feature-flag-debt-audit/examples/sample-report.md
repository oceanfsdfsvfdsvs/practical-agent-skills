# Sample Feature Flag Debt Report

## Flag Debt Decision

Owner review needed: 2 delete candidates, 1 permanent guardrail, 1 flag needing instrumentation.

## Cleanup Candidates

| Flag | Action | Risk | Evidence | Owner | Next step |
|---|---|---|---|---|---|
| `checkout_v2` | `delete_candidate` | `low` | expired, last seen 188 days ago, 2 references | payments | Create cleanup PR with checkout smoke test. |
| `old_nav_holdout` | `delete_candidate` | `medium` | archived and unreferenced, owner missing | unassigned | Assign owner before deletion. |

## Guardrails

`kill_checkout_payments` is a permanent ops flag and must stay until payments approves removal.

## Verification Plan

Run checkout unit tests, billing smoke checks, and confirm the flag can be restored in the flag system.
