# Hermes Compatibility Notes

Hermes native skill packaging was not verified in this automation run because no current local Hermes skill spec or CLI was available in the repository.

Status: `blocked-for-runtime-verification`

Use the Markdown workflow directly until the target Hermes runtime format is confirmed:

- `home-inventory-claim-preflight/SKILL.md`
- `home-inventory-claim-preflight/agents/openai.yaml`
- `home-inventory-claim-preflight/scripts/home_inventory_claim_preflight.py`
- `home-inventory-claim-preflight/templates/adjuster-packet-checklist.md`

Local validation:

```bash
python3 home-inventory-claim-preflight/scripts/home_inventory_claim_preflight.py \
  --inventory home-inventory-claim-preflight/scripts/fixtures/contents_inventory.csv \
  --policy home-inventory-claim-preflight/scripts/fixtures/policy.json
```
