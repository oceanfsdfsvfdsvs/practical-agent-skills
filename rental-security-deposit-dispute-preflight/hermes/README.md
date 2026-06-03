# Hermes Compatibility Notes

Hermes native skill packaging was not verified in this automation run. Prior local checks in this repository showed the available `hermes` CLI did not recognize local skill directories as installable native skill sources.

Status: `blocked-for-runtime-verification`

Use the Markdown workflow directly until the target Hermes runtime format or registry source is confirmed:

- `rental-security-deposit-dispute-preflight/SKILL.md`
- `rental-security-deposit-dispute-preflight/agents/openai.yaml`
- `rental-security-deposit-dispute-preflight/scripts/rental_security_deposit_dispute_preflight.py`
- `rental-security-deposit-dispute-preflight/templates/deposit-dispute-report.md`

Local validation:

```bash
python3 rental-security-deposit-dispute-preflight/scripts/rental_security_deposit_dispute_preflight.py \
  --cases rental-security-deposit-dispute-preflight/scripts/fixtures/deposit_cases.csv \
  --rules rental-security-deposit-dispute-preflight/scripts/fixtures/state_rules.json \
  --evidence-dir rental-security-deposit-dispute-preflight/scripts/fixtures/evidence \
  --today 2026-06-04
```
