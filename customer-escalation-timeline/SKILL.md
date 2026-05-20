---
name: customer-escalation-timeline
description: Reconstruct customer support escalation timelines from exported tickets, event logs, handoff notes, and account context so CS, support, engineering, and CX leaders can produce a structured handoff packet, SLA/ownership risk report, and closure plan without connecting to Zendesk, Intercom, Slack, Jira, or a CRM.
---

# Customer Escalation Timeline

## Overview

Use this skill when a customer escalation, complaint, renewal-risk issue, Sev 1/Sev 2 support case, or executive escalation needs a clear timeline and handoff packet. The goal is to stop agents from rebuilding context from long threads, scattered Slack/email/CRM fragments, and ambiguous ticket status.

The skill works from local exports and notes. It does not log into support tools, change ticket ownership, send customer messages, or modify CRM/account records.

## Use And Do Not Use

Use for:

- Escalated support tickets where ownership, next step, or customer update cadence is unclear.
- AI-to-human, L1-to-L2, support-to-engineering, or CS-to-billing handoffs.
- SLA breach or near-breach reviews that need stage-by-stage evidence.
- Repeat-contact analysis where the customer may be describing the same issue differently.
- Executive, renewal, churn, legal-threat, or VIP-account escalations needing a concise brief.
- Post-resolution review of whether the fix, workaround, or root-cause tag actually closed the loop.

Do not use for:

- Sending customer communications without human approval.
- Closing, reassigning, deleting, or editing live tickets.
- Legal conclusions, employment discipline, or blame assignment.
- Raw secrets, tokens, customer payment details, protected health data, or full private transcripts unless the user confirms they are allowed to process them locally.

## Required Inputs

Ask only for missing inputs that materially affect the escalation review:

- Ticket export path with ticket ID, customer/account, priority/severity, status, timestamps, SLA fields, owner/team, product area, and root-cause tag when available.
- Event or conversation export path with ticket ID, event time, actor, channel, event type, message/summary, owner/team, next step, due time, and linked issue when available.
- Optional account context export with customer tier, renewal date, ARR/plan, health, CSM/AE owner, and past escalation count.
- Review time (`--now`) and SLA/acknowledgment thresholds if they differ from defaults.
- Output preference: Markdown report, copied table, or saved file.

Preferred fields:

```csv
tickets: ticket_id,customer_id,account,subject,status,severity,priority,created_at,first_response_at,escalated_at,sla_due_at,resolved_at,assigned_team,assignee,product_area,root_cause,sentiment,renewal_date,arr
events: ticket_id,event_time,event_type,actor,channel,team,owner,message,next_step,due_at,linked_item
accounts: customer_id,account,revenue_tier,renewal_date,arr,health_score,csm,ae,past_escalations_90d
```

## Workflow

### 1. Preserve The Review Boundary

Before classifying risk, capture:

- The customer problem in plain language.
- Ownership chain and whether each handoff was acknowledged.
- What was tried, what was confirmed, and what evidence is missing.
- Customer expectation, sentiment, renewal/VIP context, and legal/churn signals.
- SLA clock, response gaps, next action, owner, and due time.
- Linked Jira/Linear/GitHub/incident/status-page/customer-thread references.

Do not ask for passwords, private keys, payment card values, or unrestricted support-tool access.

### 2. Run The Local Timeline Preflight

Use explicit paths:

```bash
python3 customer-escalation-timeline/scripts/customer_escalation_timeline.py \
  --tickets /absolute/path/tickets.csv \
  --events /absolute/path/events.csv \
  --accounts /absolute/path/accounts.csv \
  --now 2026-05-21T09:00:00
```

The script accepts CSV or JSON. JSON may be a list of row objects or an object containing `tickets`, `events`, `accounts`, `rows`, or `items`.

### 3. Classify Findings

Use one primary action:

- `owner_acceptance_required`: escalation was handed off, reassigned, or mentioned but no accountable owner accepted it.
- `customer_update_due`: customer-facing update is overdue or no expectation was set.
- `handoff_packet_required`: the receiving team lacks problem summary, steps tried, evidence, or next step.
- `sla_or_queue_breach_review`: SLA, acknowledgment, stale queue, or silent ticket-drop risk needs review.
- `root_cause_followup`: issue was closed or marked fixed without root-cause tag, repeat-contact check, or post-fix volume review.
- `ready_for_review`: supplied evidence has owner, next step, due time, and enough timeline context.

Use one risk level:

- `critical`: VIP/renewal/legal/churn signal plus no owner, overdue SLA, unresolved blocker, or missing customer update.
- `high`: escalated ticket with missing owner acceptance, stale next step, repeated customer follow-ups, or handoff without packet.
- `medium`: incomplete root cause, fragmented channels, unclear linked issue, or repeat-contact risk.
- `low`: complete packet with minor documentation or closure-note gaps.

Do not say an escalation is ready to close while `critical` or `high` findings remain unresolved.

### 4. Produce The Escalation Report

Return:

```markdown
## Escalation Timeline Decision
[Hold closure / Owner acceptance required / Customer update due / Ready for review]

## Handoff Packet
| Ticket | Customer | Severity | Current owner | Problem | Tried/confirmed | Next step | Due |
|---|---|---|---|---|---|---|---|

## Timeline Findings
| Risk | Action | Ticket | Evidence | Reviewer next step |
|---|---|---|---|---|

## Controls Checked
[SLA clock, owner acceptance, customer update cadence, handoff completeness, linked issue, root-cause tag, repeat-contact signal, renewal/VIP context]

## Closure Gate
[Items that must be assigned, updated, linked, tagged, or evidenced before closure]

## Open Questions
[Only questions that affect customer escalation safety]
```

Use `templates/escalation-handoff.md` when the user asks for a reusable handoff artifact.

### 5. Apply Guardrails Before Advising Closure

Do not advise closure until:

- Every escalated ticket has an accountable owner and current next step.
- Customer-facing update timing is explicit or still within policy.
- Handoff packet includes problem, steps tried, confirmed evidence, suspected root cause, linked issue, owner, and due time.
- SLA breaches or queue stalls have a documented stage and cause.
- Repeat contacts and post-fix tickets are checked before marking the root cause resolved.
- Evidence is stored in the support/CRM/ticketing system outside the prompt transcript.

## Examples And Acceptance Checks

Positive example: "Use $customer-escalation-timeline on this Zendesk ticket export, Slack escalation CSV, and account context before the CSM briefs the VP."

Positive AI handoff example: "Review AI-to-human escalations and identify where the human agent lacked context or asked the customer to repeat themselves."

Negative example: "Close this angry customer's ticket for me." Do not modify live systems; produce a review report only.

Boundary example: "I only have a ticket CSV." Produce a limited timeline report and explain that event-level handoff and account-context checks are unavailable.

## Validation

Smoke-test the bundled fixture:

```bash
python3 customer-escalation-timeline/scripts/customer_escalation_timeline.py \
  --tickets customer-escalation-timeline/scripts/fixtures/tickets.csv \
  --events customer-escalation-timeline/scripts/fixtures/events.csv \
  --accounts customer-escalation-timeline/scripts/fixtures/accounts.csv \
  --now 2026-05-21T09:00:00
```

Expected result: a Markdown report with `Escalation Timeline Decision`, `owner_acceptance_required`, `customer_update_due`, `handoff_packet_required`, and `repeat_contact_or_fix_validation`.
