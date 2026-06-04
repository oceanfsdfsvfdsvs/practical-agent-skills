# Hermes Runtime Notes

Native Hermes packaging is blocked for runtime verification until the current local Hermes skill package spec and check command are confirmed.

Use the Markdown workflow and local script as source material:

- `credit-report-dispute-preflight/SKILL.md`
- `credit-report-dispute-preflight/agents/openai.yaml`
- `credit-report-dispute-preflight/scripts/credit_report_dispute_preflight.py`
- `credit-report-dispute-preflight/templates/dispute-readiness-report.md`

Fixture smoke test:

```bash
python3 credit-report-dispute-preflight/scripts/credit_report_dispute_preflight.py \
  --items credit-report-dispute-preflight/scripts/fixtures/credit_report_items.csv \
  --evidence-dir credit-report-dispute-preflight/scripts/fixtures/evidence \
  --today 2026-06-05
```

Status: `blocked-for-runtime-verification`; do not claim native Hermes execution until `hermes skills check` or the current equivalent accepts local skill directories.
