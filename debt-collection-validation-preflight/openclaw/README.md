# OpenClaw Install Notes

Copy the full `debt-collection-validation-preflight` directory into the OpenClaw workspace skills directory, keeping `scripts/`, `references/`, `templates/`, and `examples/` together so relative paths resolve.

Suggested check when the local OpenClaw CLI supports it:

```bash
openclaw skills check debt-collection-validation-preflight
```

If `openclaw` is not installed or your version expects a registry package, treat runtime verification as not completed. The local Python fixture can still be run from the repository root:

```bash
python3 debt-collection-validation-preflight/scripts/debt_collection_validation_preflight.py \
  --cases debt-collection-validation-preflight/scripts/fixtures/debt_collection_cases.csv \
  --evidence-dir debt-collection-validation-preflight/scripts/fixtures/evidence \
  --today 2026-06-17
```
