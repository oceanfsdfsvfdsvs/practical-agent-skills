# Hermes Compatibility Notes

The skill is packaged as a portable Markdown skill with a deterministic local script. A native Hermes adapter is not included because the local Hermes skill handler specification was not available during this run.

Status: `blocked-for-runtime-verification`

Use the skill manually by pointing Hermes-compatible agents at:

- `dsar-request-preflight/SKILL.md`
- `dsar-request-preflight/agents/openai.yaml`
- `dsar-request-preflight/scripts/dsar_request_preflight.py`

Local validation:

```bash
python3 dsar-request-preflight/scripts/dsar_request_preflight.py \
  --requests dsar-request-preflight/scripts/fixtures/requests.csv \
  --systems dsar-request-preflight/scripts/fixtures/systems.csv \
  --policy dsar-request-preflight/scripts/fixtures/policy.json \
  --today 2026-05-30
```

Do not claim Hermes-native installation success until the official or local Hermes skill spec is available and a handler check passes.
