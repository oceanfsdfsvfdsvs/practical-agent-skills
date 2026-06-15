# OpenClaw Install Notes

Native OpenClaw validation was not run in this environment because the OpenClaw CLI/spec was not available.

Portable install path:

1. Copy `fmla-certification-preflight/` into your OpenClaw workspace skills directory.
2. Keep the full skill directory together so `scripts/`, `references/`, `templates/`, and `examples/` resolve relative to `SKILL.md`.
3. Run the local smoke test:

```bash
python3 fmla-certification-preflight/scripts/fmla_certification_preflight.py \
  --cases fmla-certification-preflight/scripts/fixtures/fmla_cases.csv \
  --evidence-dir fmla-certification-preflight/scripts/fixtures/evidence \
  --today 2026-06-16
```

If your OpenClaw CLI supports skill checks, run:

```bash
openclaw skills check fmla-certification-preflight
```

Status: install notes provided; native OpenClaw runtime verification remains blocked until the CLI is available.
