# OpenClaw Install Notes

Copy the full `saas-license-rightsize` directory into your OpenClaw workspace skills directory.

Suggested check when your local OpenClaw CLI supports it:

```bash
openclaw skills check saas-license-rightsize
```

Local validation does not require network access:

```bash
python3 saas-license-rightsize/scripts/saas_license_rightsize.py \
  --licenses saas-license-rightsize/scripts/fixtures/licenses.csv \
  --employees saas-license-rightsize/scripts/fixtures/employees.csv \
  --usage saas-license-rightsize/scripts/fixtures/usage.csv \
  --today 2026-05-17
```

This repository has not run `openclaw skills check` unless the final automation report explicitly says so.
