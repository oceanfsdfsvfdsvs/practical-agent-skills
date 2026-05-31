# Hermes Runtime Notes

Use the Markdown skill directly when Hermes can load local skill directories:

```text
marketplace-seller-appeal-preflight/SKILL.md
```

Local fixture:

```bash
python3 marketplace-seller-appeal-preflight/scripts/marketplace_seller_appeal_preflight.py \
  --cases marketplace-seller-appeal-preflight/scripts/fixtures/appeal_cases.csv \
  --evidence-dir marketplace-seller-appeal-preflight/scripts/fixtures/evidence \
  --today 2026-06-01
```

Status: `blocked-for-runtime-verification` for Hermes-native handler packaging until the active Hermes skill spec is confirmed. No native `skill.yaml` or handler success is claimed.
