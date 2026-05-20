# Hermes Runtime Notes

This skill currently ships as a Markdown-plus-local-script skill. It does not include a native Hermes `skill.yaml` or handler because the current local Hermes skill packaging contract has not been verified in this repository.

Status: `blocked-for-runtime-verification`

Use the skill instructions and local script directly:

```bash
python3 customer-escalation-timeline/scripts/customer_escalation_timeline.py \
  --tickets customer-escalation-timeline/scripts/fixtures/tickets.csv \
  --events customer-escalation-timeline/scripts/fixtures/events.csv \
  --accounts customer-escalation-timeline/scripts/fixtures/accounts.csv \
  --now 2026-05-21T09:00:00
```

Before claiming Hermes native support, verify the current Hermes local skill specification and run the matching Hermes CLI inspection command against this skill.
