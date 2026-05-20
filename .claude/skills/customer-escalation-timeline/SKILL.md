---
name: customer-escalation-timeline
description: Reconstruct customer support escalation timelines from exported tickets, event logs, handoff notes, and account context so CS, support, engineering, and CX leaders can produce a structured handoff packet, SLA/ownership risk report, and closure plan without connecting to Zendesk, Intercom, Slack, Jira, or a CRM.
---

# Customer Escalation Timeline

Use this mirror with the full repository checkout so relative paths such as `customer-escalation-timeline/scripts/customer_escalation_timeline.py` resolve correctly.

## Workflow

1. Confirm the user wants an escalation review, not live ticket modification or customer messaging.
2. Ask for local exports: tickets, event/conversation logs, and optional account context.
3. Run the local scanner when file paths are available:

```bash
python3 customer-escalation-timeline/scripts/customer_escalation_timeline.py \
  --tickets customer-escalation-timeline/scripts/fixtures/tickets.csv \
  --events customer-escalation-timeline/scripts/fixtures/events.csv \
  --accounts customer-escalation-timeline/scripts/fixtures/accounts.csv \
  --now 2026-05-21T09:00:00
```

4. Produce an escalation timeline report with handoff packet, timeline findings, controls checked, closure gate, and open questions.
5. Never close, reassign, delete, or edit live tickets. Do not send customer messages without human approval.

Expected fixture terms include `Escalation Timeline Decision`, `owner_acceptance_required`, `customer_update_due`, `handoff_packet_required`, and `repeat_contact_or_fix_validation`.
