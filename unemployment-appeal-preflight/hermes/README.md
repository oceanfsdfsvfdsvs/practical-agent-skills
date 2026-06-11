# Hermes Notes

Native Hermes packaging is blocked for runtime verification until the current local Hermes skill spec and local-path validation flow are confirmed.

Portable use today:

1. Keep the full `unemployment-appeal-preflight` directory together.
2. Point Hermes or a Hermes-wrapped agent at `SKILL.md`.
3. Run the local script manually when deterministic packet checks are needed:

```bash
python3 unemployment-appeal-preflight/scripts/unemployment_appeal_preflight.py \
  --cases unemployment-appeal-preflight/scripts/fixtures/appeal_cases.csv \
  --evidence-dir unemployment-appeal-preflight/scripts/fixtures/evidence \
  --today 2026-06-12
```

Do not treat this as a native `hermes/skill.yaml` package until the current Hermes spec is available and locally validated.
