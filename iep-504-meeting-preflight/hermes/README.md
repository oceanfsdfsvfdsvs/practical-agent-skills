# Hermes Notes

Native Hermes packaging is blocked for runtime verification until the current local Hermes skill spec and local-path validation flow are confirmed.

Portable use today:

1. Keep the full `iep-504-meeting-preflight` directory together.
2. Point Hermes or a Hermes-wrapped agent at `SKILL.md`.
3. Run the local script manually when deterministic packet checks are needed:

```bash
python3 iep-504-meeting-preflight/scripts/iep_504_meeting_preflight.py \
  --cases iep-504-meeting-preflight/scripts/fixtures/meeting_cases.csv \
  --evidence-dir iep-504-meeting-preflight/scripts/fixtures/evidence \
  --today 2026-06-06
```

Do not treat this as a native `hermes/skill.yaml` package until the current Hermes spec is available and locally validated.
