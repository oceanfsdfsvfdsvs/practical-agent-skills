# OpenClaw Install Notes

Copy `credit-report-dispute-preflight/` into your OpenClaw workspace skills directory, keeping the full directory tree so relative paths resolve:

```bash
cp -R credit-report-dispute-preflight /path/to/openclaw/workspace/skills/
```

Suggested local check, when supported by your OpenClaw CLI:

```bash
openclaw skills check credit-report-dispute-preflight
```

This environment did not have an OpenClaw CLI available during packaging, so runtime verification is not claimed.

Fixture smoke test:

```bash
python3 credit-report-dispute-preflight/scripts/credit_report_dispute_preflight.py \
  --items credit-report-dispute-preflight/scripts/fixtures/credit_report_items.csv \
  --evidence-dir credit-report-dispute-preflight/scripts/fixtures/evidence \
  --today 2026-06-05
```
