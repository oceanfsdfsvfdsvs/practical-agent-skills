# OpenClaw Install Notes

Copy the full `contract-renewal-risk-preflight` directory into your OpenClaw workspace skills directory.

Suggested check when your local OpenClaw CLI supports it:

```bash
openclaw skills check contract-renewal-risk-preflight
```

Local validation does not require network access:

```bash
python3 contract-renewal-risk-preflight/scripts/contract_renewal_risk_preflight.py \
  --contracts contract-renewal-risk-preflight/scripts/fixtures/contracts.csv \
  --today 2026-05-16
```

This repository has not run `openclaw skills check` unless the final automation report explicitly says so.
