# Hermes Compatibility Notes

Hermes native skill packaging was not verified in this automation run because no current local Hermes skill spec or CLI was available in the repository.

Status: `blocked-for-runtime-verification`

Use the Markdown workflow directly until the target Hermes runtime format is confirmed:

- `tax-notice-response-preflight/SKILL.md`
- `tax-notice-response-preflight/agents/openai.yaml`
- `tax-notice-response-preflight/scripts/tax_notice_response_preflight.py`
- `tax-notice-response-preflight/templates/response-packet-checklist.md`

Local validation:

```bash
python3 tax-notice-response-preflight/scripts/tax_notice_response_preflight.py \
  --notices tax-notice-response-preflight/scripts/fixtures/notices.csv \
  --evidence tax-notice-response-preflight/scripts/fixtures/evidence.csv \
  --policy tax-notice-response-preflight/scripts/fixtures/policy.json \
  --today 2026-06-15
```
