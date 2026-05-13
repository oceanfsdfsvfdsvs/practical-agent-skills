# CSV Import Preflight

Local-first skill for catching risky CSV/TSV imports before upload to SaaS, admin, CRM, billing, or internal tools.

## Use For

- Required-field, enum, date, numeric, and schema checks.
- Duplicate unique keys and destructive update risk.
- Producing a block/review/pass decision with row-level evidence.

## Run

```bash
python3 csv-import-preflight/scripts/csv_import_preflight.py \
  csv-import-preflight/scripts/fixtures/bad_import.csv \
  --schema csv-import-preflight/scripts/fixtures/schema.json
```

The bundled bad fixture intentionally exits with code `2` because it should block a risky import.

## Runtime Notes

- Codex/OpenAI: use `SKILL.md` plus `agents/openai.yaml`.
- Claude Code: use `.claude/skills/csv-import-preflight/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.
