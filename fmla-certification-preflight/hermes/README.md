# Hermes Runtime Notes

Native Hermes packaging was not generated because the current Hermes skill handler spec was not verified in this environment.

Portable usage:

1. Keep this directory intact.
2. Point Hermes, or an agent running inside Hermes, at `SKILL.md`.
3. Run the local smoke test before use:

```bash
python3 fmla-certification-preflight/scripts/fmla_certification_preflight.py \
  --cases fmla-certification-preflight/scripts/fixtures/fmla_cases.csv \
  --evidence-dir fmla-certification-preflight/scripts/fixtures/evidence \
  --today 2026-06-16
```

Status: blocked-for-runtime-verification. Do not claim native Hermes support until the official/local Hermes skill spec and handler shape are confirmed.
