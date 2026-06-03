# OpenClaw Installation Notes

Copy `rental-security-deposit-dispute-preflight/` into your OpenClaw workspace skills directory, keeping the full directory tree so relative paths resolve:

```bash
cp -R rental-security-deposit-dispute-preflight /path/to/openclaw/workspace/skills/
```

Suggested check when your OpenClaw CLI supports local skill validation:

```bash
openclaw skills check rental-security-deposit-dispute-preflight
```

Local validation in this repository:

```bash
python3 rental-security-deposit-dispute-preflight/scripts/rental_security_deposit_dispute_preflight.py \
  --cases rental-security-deposit-dispute-preflight/scripts/fixtures/deposit_cases.csv \
  --rules rental-security-deposit-dispute-preflight/scripts/fixtures/state_rules.json \
  --evidence-dir rental-security-deposit-dispute-preflight/scripts/fixtures/evidence \
  --today 2026-06-04
```

This runtime was not verified with a local OpenClaw CLI in this automation run.
