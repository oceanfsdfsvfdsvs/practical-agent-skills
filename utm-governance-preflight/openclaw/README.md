# OpenClaw Install Notes

Copy the full `utm-governance-preflight` directory into your OpenClaw workspace skills directory.

Suggested check when your local OpenClaw CLI supports it:

```bash
openclaw skills check utm-governance-preflight
```

Local validation does not require network access:

```bash
python3 utm-governance-preflight/scripts/utm_governance_preflight.py \
  --links utm-governance-preflight/scripts/fixtures/campaign_links.csv \
  --policy utm-governance-preflight/scripts/fixtures/policy.json
```

This repository has not run `openclaw skills check` unless the final automation report explicitly says so.
