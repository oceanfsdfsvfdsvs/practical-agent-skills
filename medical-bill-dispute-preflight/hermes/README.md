# Hermes Compatibility Notes

Hermes native skill packaging was not verified in this automation run because no current local Hermes skill spec or CLI was available in the repository.

Status: `blocked-for-runtime-verification`

Use the Markdown workflow directly until the target Hermes runtime format is confirmed:

- `medical-bill-dispute-preflight/SKILL.md`
- `medical-bill-dispute-preflight/agents/openai.yaml`
- `medical-bill-dispute-preflight/scripts/medical_bill_dispute_preflight.py`
- `medical-bill-dispute-preflight/templates/dispute-packet-checklist.md`

Local validation:

```bash
python3 medical-bill-dispute-preflight/scripts/medical_bill_dispute_preflight.py \
  --bills medical-bill-dispute-preflight/scripts/fixtures/medical_bills.csv \
  --eob medical-bill-dispute-preflight/scripts/fixtures/eob.csv \
  --policy medical-bill-dispute-preflight/scripts/fixtures/policy.json
```
