# Hermes Runtime Notes

Status: `blocked-for-runtime-verification`.

The skill is provided as a portable Markdown workflow plus a local Python script. Do not claim native Hermes execution until the active Hermes skill schema and handler contract are verified for this repository.

Use the local script as the validation boundary:

```bash
python3 utm-governance-preflight/scripts/utm_governance_preflight.py \
  --links utm-governance-preflight/scripts/fixtures/campaign_links.csv \
  --policy utm-governance-preflight/scripts/fixtures/policy.json
```

Add a native `skill.yaml` or `handler.js` only after validating the expected Hermes schema, input contract, output contract, and local file access rules.
