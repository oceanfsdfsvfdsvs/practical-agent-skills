# OpenClaw Install Notes

Copy the full skill directory into your OpenClaw skills workspace so relative scripts, fixtures, references, and templates stay together.

```bash
mkdir -p ~/.openclaw/skills
cp -R employee-offboarding-access-preflight ~/.openclaw/skills/
```

Suggested validation when your OpenClaw CLI supports local skill checks:

```bash
openclaw skills check employee-offboarding-access-preflight
```

Local script smoke test:

```bash
python3 employee-offboarding-access-preflight/scripts/employee_offboarding_access_preflight.py \
  --departures employee-offboarding-access-preflight/scripts/fixtures/departures.csv \
  --accounts employee-offboarding-access-preflight/scripts/fixtures/accounts.csv \
  --groups employee-offboarding-access-preflight/scripts/fixtures/groups.csv \
  --assets employee-offboarding-access-preflight/scripts/fixtures/assets.csv \
  --secrets employee-offboarding-access-preflight/scripts/fixtures/secrets.csv
```

This repository does not claim OpenClaw native validation unless the skill is installed into an OpenClaw-managed skills directory and the CLI check passes.
