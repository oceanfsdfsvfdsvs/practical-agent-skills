# OpenClaw Install Notes

Copy `workers-comp-denial-preflight/` into your OpenClaw workspace skills directory.

Suggested check when your local OpenClaw CLI supports skill validation:

```bash
openclaw skills check workers-comp-denial-preflight
```

Local runtime verification status: not verified in this repository run unless the caller has an `openclaw` CLI available. The bundled Python fixture can still be run directly:

```bash
python3 workers-comp-denial-preflight/scripts/workers_comp_denial_preflight.py \
  --cases workers-comp-denial-preflight/scripts/fixtures/workers_comp_cases.csv \
  --evidence-dir workers-comp-denial-preflight/scripts/fixtures/evidence \
  --today 2026-06-14
```
