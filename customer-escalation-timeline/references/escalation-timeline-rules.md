# Escalation Timeline Rules

## Review Questions

1. Who owns the escalation now, and did they explicitly accept it?
2. What is the customer's problem in plain language?
3. What has already been tried, and what happened?
4. What is confirmed evidence versus assumption?
5. What is the next action, who owns it, and when is it due?
6. Is the customer update cadence still inside policy?
7. Which linked issue, incident, order, invoice, deployment, or account record explains the current blocker?
8. Has the root cause been tagged, and did repeat contacts drop after the fix?

## High-Risk Signals

- Escalated ticket with blank assignee, queue owner, or reassignment without acknowledgment.
- Last customer-visible update is older than policy while the ticket remains open.
- Customer has sent multiple follow-ups with no agent reply.
- Handoff note says only "investigating", "waiting on engineering", or similar thin status.
- Ticket bounced between teams more than twice.
- SLA due time has passed, is missing on a high-priority ticket, or is close with no owner.
- Account is VIP, high ARR, near renewal, low health, has legal/churn language, or has repeated escalations.
- Issue was closed or marked fixed without root-cause tag, linked issue, closure evidence, or repeat-contact check.

## Handoff Packet Minimum

Each escalation handoff should contain:

- One-sentence problem statement in customer language.
- Steps tried and outcomes.
- Confirmed facts and evidence links.
- Suspected root cause or category.
- Customer sentiment and expectation.
- Current owner and accepting team.
- Next action and due time.
- SLA state and customer-update requirement.
- Account context: tier, renewal date, health, ARR, or prior escalations when available.

## Closure Gate

Do not mark the escalation ready to close until:

- No `critical` or `high` findings remain.
- The customer-facing update path is explicit.
- The current owner accepted the handoff.
- Linked engineering/support/billing/incident items are present or explicitly not applicable.
- A root-cause or unresolved-reason tag exists.
- Repeat-contact or post-fix validation is planned for recurring issues.
