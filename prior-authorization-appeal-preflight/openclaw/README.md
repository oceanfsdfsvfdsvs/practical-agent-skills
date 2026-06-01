# OpenClaw Installation Notes

Copy `prior-authorization-appeal-preflight/` into your OpenClaw workspace skills directory, keeping the full directory tree so relative paths resolve:

```bash
cp -R prior-authorization-appeal-preflight /path/to/openclaw/workspace/skills/
```

Suggested check when your OpenClaw CLI supports local skill validation:

```bash
openclaw skills check prior-authorization-appeal-preflight
```

Local validation in this repository:

```bash
python3 prior-authorization-appeal-preflight/scripts/prior_authorization_appeal_preflight.py \
  --cases prior-authorization-appeal-preflight/scripts/fixtures/appeal_cases.csv \
  --evidence-dir prior-authorization-appeal-preflight/scripts/fixtures/evidence \
  --today 2026-06-02
```

This runtime was not verified with a local OpenClaw CLI in this automation run.
