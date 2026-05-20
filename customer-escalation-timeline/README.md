# Customer Escalation Timeline

Rebuild support escalation context before the customer has to repeat the story.

`customer-escalation-timeline` is a local-first agent skill for support, customer success, CX, engineering escalation, and founder-led teams that need to turn scattered ticket, chat, CRM, and account exports into a clear escalation timeline and handoff packet.

It helps an agent inspect exported tickets and event logs, classify ownership/SLA/handoff risks, and produce a reviewer-ready escalation report without connecting to Zendesk, Intercom, Slack, Jira, Linear, GitHub, or a CRM.

## Problem

Escalations fail when the next owner receives a long thread with no usable context, when customer updates drift, or when a "fixed" issue keeps generating repeat tickets under different wording. Teams can know they need a handoff note and still miss owner acceptance, SLA state, what was tried, linked issue evidence, renewal context, and root-cause follow-up.

This skill combines an escalation-review workflow with a deterministic local scanner so an agent can produce a repeatable handoff and closure-gate report.

## Why Use This Instead Of A Prompt

- Reconstructs per-ticket timeline from ticket and event exports.
- Flags missing owner acceptance, stale next steps, overdue customer updates, SLA risk, and handoff packet gaps.
- Adds account context such as VIP tier, renewal timing, ARR, health, and repeat escalations.
- Separates `owner_acceptance_required`, `customer_update_due`, `handoff_packet_required`, `sla_or_queue_breach_review`, and `ready_for_review`.
- Keeps the agent inside a review boundary instead of changing live tickets or sending customer messages.

## Contents

- `SKILL.md` - agent instructions and acceptance checks.
- `agents/openai.yaml` - OpenAI/Codex style metadata.
- `references/escalation-timeline-rules.md` - review rules, failure modes, and evidence checklist.
- `templates/escalation-handoff.md` - reviewer-ready handoff template.
- `examples/sample-report.md` - expected output shape.
- `scripts/customer_escalation_timeline.py` - local scanner for CSV/JSON exports.
- `scripts/fixtures/` - smoke-test ticket, event, and account exports.
- `openclaw/README.md` and `hermes/README.md` - runtime notes and current verification limits.

## Run

```bash
python3 customer-escalation-timeline/scripts/customer_escalation_timeline.py \
  --tickets customer-escalation-timeline/scripts/fixtures/tickets.csv \
  --events customer-escalation-timeline/scripts/fixtures/events.csv \
  --accounts customer-escalation-timeline/scripts/fixtures/accounts.csv \
  --now 2026-05-21T09:00:00
```

The script prints Markdown to stdout. It writes a file only when `--output` is provided.

## Inputs

CSV columns are matched case-insensitively. Preferred ticket fields:

```csv
ticket_id,customer_id,account,subject,status,severity,priority,created_at,first_response_at,escalated_at,sla_due_at,resolved_at,assigned_team,assignee,product_area,root_cause,sentiment,renewal_date,arr
```

Preferred event fields:

```csv
ticket_id,event_time,event_type,actor,channel,team,owner,message,next_step,due_at,linked_item
```

Preferred account fields:

```csv
customer_id,account,revenue_tier,renewal_date,arr,health_score,csm,ae,past_escalations_90d
```

JSON exports may be a list of objects or an object containing `tickets`, `events`, `accounts`, `rows`, or `items`.

## Install Notes

Codex/OpenAI-style agents can use the skill directory directly. Claude Code can copy the mirrored `.claude/skills/customer-escalation-timeline/SKILL.md` or the whole directory into its skills folder.

OpenClaw and Hermes support is documented but not claimed as fully verified unless the matching local CLI/spec is available.
