# Hermes Runtime Notes

Status: `blocked-for-runtime-verification`.

The skill is provided as a portable Markdown workflow plus a local Python script. Do not claim native Hermes execution until the active Hermes skill schema and handler contract are verified for this repository.

Use the local script as the validation boundary:

```bash
python3 saas-license-rightsize/scripts/saas_license_rightsize.py \
  --licenses saas-license-rightsize/scripts/fixtures/licenses.csv \
  --employees saas-license-rightsize/scripts/fixtures/employees.csv \
  --usage saas-license-rightsize/scripts/fixtures/usage.csv \
  --today 2026-05-17
```

Add a native `skill.yaml` or `handler.js` only after validating the expected Hermes schema, input contract, output contract, and local file access rules.
