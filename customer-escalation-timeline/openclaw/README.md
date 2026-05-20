# OpenClaw Install Notes

Copy the full skill directory into your OpenClaw skills workspace so relative scripts, fixtures, references, and templates stay together.

```bash
mkdir -p ~/.openclaw/skills
cp -R customer-escalation-timeline ~/.openclaw/skills/
```

Suggested validation when your OpenClaw CLI supports local skill checks:

```bash
openclaw skills check customer-escalation-timeline
```

Local script smoke test:

```bash
python3 customer-escalation-timeline/scripts/customer_escalation_timeline.py \
  --tickets customer-escalation-timeline/scripts/fixtures/tickets.csv \
  --events customer-escalation-timeline/scripts/fixtures/events.csv \
  --accounts customer-escalation-timeline/scripts/fixtures/accounts.csv \
  --now 2026-05-21T09:00:00
```

This repository does not claim OpenClaw native validation unless the skill is installed into an OpenClaw-managed skills directory and the CLI check passes.
