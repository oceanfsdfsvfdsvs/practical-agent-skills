# OpenClaw Installation Notes

Copy `medical-bill-dispute-preflight/` into your OpenClaw workspace skills directory, keeping the full directory tree so relative paths resolve:

```bash
cp -R medical-bill-dispute-preflight /path/to/openclaw/workspace/skills/
```

Suggested check when your OpenClaw CLI supports local skill validation:

```bash
openclaw skills check medical-bill-dispute-preflight
```

Local validation in this repository:

```bash
python3 medical-bill-dispute-preflight/scripts/medical_bill_dispute_preflight.py \
  --bills medical-bill-dispute-preflight/scripts/fixtures/medical_bills.csv \
  --eob medical-bill-dispute-preflight/scripts/fixtures/eob.csv \
  --policy medical-bill-dispute-preflight/scripts/fixtures/policy.json
```

This runtime was not verified with a local OpenClaw CLI in this automation run.
