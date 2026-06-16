# Hermes Runtime Notes

Native Hermes packaging is blocked pending a verified local Hermes skill specification and CLI. Do not claim this skill has been executed by Hermes until a current Hermes runtime can validate the package.

Portable fallback:

1. Keep this full skill directory together.
2. Load `SKILL.md` as the agent instruction.
3. Run the local fixture script from the repository root:

```bash
python3 debt-collection-validation-preflight/scripts/debt_collection_validation_preflight.py \
  --cases debt-collection-validation-preflight/scripts/fixtures/debt_collection_cases.csv \
  --evidence-dir debt-collection-validation-preflight/scripts/fixtures/evidence \
  --today 2026-06-17
```

Runtime verification status: `blocked-for-runtime-verification`.
