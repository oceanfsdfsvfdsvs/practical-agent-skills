# Hermes Runtime Notes

Status: blocked-for-runtime-verification.

The skill provides portable Markdown instructions, metadata, fixtures, and a local Python scanner, but no native Hermes handler is claimed here because the current Hermes skill handler specification was not available for verification in this run.

Until the Hermes spec is confirmed, install the skill as documentation plus a local tool:

```bash
python3 feature-flag-debt-audit/scripts/feature_flag_debt_audit.py \
  --flags feature-flag-debt-audit/scripts/fixtures/flags.csv \
  --code-dir feature-flag-debt-audit/scripts/fixtures/sample_app
```

Add a native `skill.yaml` or `handler.js` only after validating the expected Hermes schema and invocation contract.
