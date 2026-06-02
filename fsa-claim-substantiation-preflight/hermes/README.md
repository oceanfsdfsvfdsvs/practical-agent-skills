# Hermes Compatibility Notes

Hermes native skill packaging was not verified in this automation run. A local `hermes` CLI was present, but `hermes skills check fsa-claim-substantiation-preflight` reported no hub-installed skills to check, and `hermes skills inspect ./fsa-claim-substantiation-preflight` did not recognize a local directory identifier. The repository does not yet include a confirmed Hermes native local-package spec.

Status: `blocked-for-runtime-verification`

Use the Markdown workflow directly until the target Hermes runtime format is confirmed:

- `fsa-claim-substantiation-preflight/SKILL.md`
- `fsa-claim-substantiation-preflight/agents/openai.yaml`
- `fsa-claim-substantiation-preflight/scripts/fsa_claim_substantiation_preflight.py`
- `fsa-claim-substantiation-preflight/templates/claim-correction-checklist.md`

Local validation:

```bash
python3 fsa-claim-substantiation-preflight/scripts/fsa_claim_substantiation_preflight.py \
  --claims fsa-claim-substantiation-preflight/scripts/fixtures/fsa_claims.csv \
  --evidence-dir fsa-claim-substantiation-preflight/scripts/fixtures/evidence \
  --today 2026-06-03
```
