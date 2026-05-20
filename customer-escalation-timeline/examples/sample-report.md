# Sample Escalation Timeline Report

## Escalation Timeline Decision
Hold closure - 2 critical, 3 high, 2 medium findings across 3 tickets.

## Handoff Packet
| Ticket | Customer | Severity | Current owner | Problem | Tried/confirmed | Next step | Due |
|---|---|---|---|---|---|---|---|
| T-1001 | Northstar Labs | Sev 2 | Unaccepted handoff | Checkout failures after launch. | Cache cleared; issue reproduces on account-specific checkout. | Engineering owner must accept and link bug. | 2026-05-21 10:00 |
| T-1002 | Blue Harbor | Sev 3 | Billing Ops | Renewal pricing mismatch after onboarding promise. | CSM notes and billing ticket disagree. | Reconstruct sales handoff and send customer update. | 2026-05-21 12:00 |

## Timeline Findings
| Risk | Action | Ticket | Evidence | Reviewer next step |
|---|---|---|---|---|
| critical | owner_acceptance_required | T-1001 | escalated without accepted owner; VIP account; SLA due in 30m | Assign owner and require acknowledgment before the next customer update. |
| high | customer_update_due | T-1002 | last customer update older than policy | Send clear update with next step and deadline. |

## Closure Gate
- T-1001: owner acceptance, linked engineering issue, customer update.
- T-1002: billing/sales evidence and customer update.
