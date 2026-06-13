# Hermes Runtime Notes

Native Hermes packaging is blocked until the current Hermes skill specification is available for local verification.

Use this skill as a plain local skill directory for now:

- `workers-comp-denial-preflight/SKILL.md`
- `workers-comp-denial-preflight/agents/openai.yaml`
- `workers-comp-denial-preflight/scripts/workers_comp_denial_preflight.py`
- `workers-comp-denial-preflight/references/workers-comp-denial-rules.md`

Do not treat this README as a verified native Hermes handler. Run the local fixture instead:

```bash
python3 workers-comp-denial-preflight/scripts/workers_comp_denial_preflight.py \
  --cases workers-comp-denial-preflight/scripts/fixtures/workers_comp_cases.csv \
  --evidence-dir workers-comp-denial-preflight/scripts/fixtures/evidence \
  --today 2026-06-14
```
