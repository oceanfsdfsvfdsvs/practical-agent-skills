# Hermes Compatibility Notes

Hermes native skill packaging was not verified in this automation run because no current local Hermes skill spec or CLI was available in the repository.

Status: `blocked-for-runtime-verification`

Use the Markdown workflow directly until the target Hermes runtime format is confirmed:

- `prior-authorization-appeal-preflight/SKILL.md`
- `prior-authorization-appeal-preflight/agents/openai.yaml`
- `prior-authorization-appeal-preflight/scripts/prior_authorization_appeal_preflight.py`
- `prior-authorization-appeal-preflight/templates/appeal-packet-checklist.md`

Local validation:

```bash
python3 prior-authorization-appeal-preflight/scripts/prior_authorization_appeal_preflight.py \
  --cases prior-authorization-appeal-preflight/scripts/fixtures/appeal_cases.csv \
  --evidence-dir prior-authorization-appeal-preflight/scripts/fixtures/evidence \
  --today 2026-06-02
```
