# OpenClaw Notes

Install by copying the `chargeback-evidence-pack/` directory into the OpenClaw workspace skills directory.

Suggested check when supported by your CLI:

```bash
openclaw skills check chargeback-evidence-pack
```

The bundled local validation does not require network access:

```bash
python3 chargeback-evidence-pack/scripts/chargeback_evidence_pack.py \
  --case chargeback-evidence-pack/scripts/fixtures/case_product_not_received.json \
  --evidence-dir chargeback-evidence-pack/scripts/fixtures/evidence
```
