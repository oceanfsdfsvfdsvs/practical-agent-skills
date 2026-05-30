# Hermes Compatibility Notes

Hermes native skill packaging was not verified in this automation run. A local `hermes` CLI was available, but `hermes skills inspect ./parcel-claim-preflight` did not resolve this local directory as an installable Hermes skill source.

Status: `blocked-for-runtime-verification`

Use the Markdown workflow directly until the target Hermes runtime format or registry source is confirmed:

- `parcel-claim-preflight/SKILL.md`
- `parcel-claim-preflight/agents/openai.yaml`
- `parcel-claim-preflight/scripts/parcel_claim_preflight.py`
- `parcel-claim-preflight/templates/claim-readiness-report.md`

Local validation:

```bash
python3 parcel-claim-preflight/scripts/parcel_claim_preflight.py \
  --shipments parcel-claim-preflight/scripts/fixtures/shipments.csv \
  --evidence-dir parcel-claim-preflight/scripts/fixtures/evidence \
  --today 2026-05-31
```
