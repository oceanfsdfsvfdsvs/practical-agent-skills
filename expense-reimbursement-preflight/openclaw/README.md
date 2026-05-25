# OpenClaw Install Notes

Copy the full skill directory into your OpenClaw skills workspace so relative scripts, fixtures, references, and templates stay together.

```bash
mkdir -p ~/.openclaw/skills
cp -R expense-reimbursement-preflight ~/.openclaw/skills/
```

Suggested validation when your OpenClaw CLI supports local skill checks:

```bash
openclaw skills check expense-reimbursement-preflight
```

Local script smoke test:

```bash
python3 expense-reimbursement-preflight/scripts/expense_reimbursement_preflight.py \
  --expenses expense-reimbursement-preflight/scripts/fixtures/expense_report.csv \
  --policy expense-reimbursement-preflight/scripts/fixtures/policy.json \
  --today 2026-05-26
```

This repository does not claim OpenClaw native validation unless the skill is installed into an OpenClaw-managed skills directory and the CLI check passes.
