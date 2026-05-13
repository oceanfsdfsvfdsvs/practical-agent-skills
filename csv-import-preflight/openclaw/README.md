# OpenClaw Notes

Install by copying the `csv-import-preflight/` directory into the OpenClaw workspace skills directory.

Suggested check when supported by your CLI:

```bash
openclaw skills check csv-import-preflight
```

The bundled local validation does not require network access:

```bash
python3 csv-import-preflight/scripts/csv_import_preflight.py \
  csv-import-preflight/scripts/fixtures/bad_import.csv \
  --schema csv-import-preflight/scripts/fixtures/schema.json
```
