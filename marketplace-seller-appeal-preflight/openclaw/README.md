# OpenClaw Install Notes

Copy the `marketplace-seller-appeal-preflight` directory into your OpenClaw workspace skills directory.

Suggested check when your OpenClaw CLI supports it:

```bash
openclaw skills check marketplace-seller-appeal-preflight
```

Then run the local fixture:

```bash
python3 marketplace-seller-appeal-preflight/scripts/marketplace_seller_appeal_preflight.py \
  --cases marketplace-seller-appeal-preflight/scripts/fixtures/appeal_cases.csv \
  --evidence-dir marketplace-seller-appeal-preflight/scripts/fixtures/evidence \
  --today 2026-06-01
```

Status: not locally verified unless `openclaw` CLI is installed in the runtime environment.
