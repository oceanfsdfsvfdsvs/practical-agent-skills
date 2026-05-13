---
name: csv-import-preflight
description: Catch risky CSV or TSV imports before upload by validating schema, required fields, duplicates, type coercion, enum drift, and destructive update risk.
---

# CSV Import Preflight

Use this mirror to invoke the repository skill at `csv-import-preflight/SKILL.md`.

## Workflow

1. Ask for the CSV/TSV path and schema when needed.
2. Run `csv-import-preflight/scripts/csv_import_preflight.py` when local files exist.
3. Classify the import as block, review, or pass.
4. Explain row-level risks and the smallest safe remediation.

Keep the full repository available so relative script and reference paths resolve correctly.
