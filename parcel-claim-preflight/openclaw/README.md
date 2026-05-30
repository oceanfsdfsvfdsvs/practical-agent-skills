# OpenClaw Installation Notes

Copy `parcel-claim-preflight/` into your OpenClaw workspace skills directory, keeping the full directory tree so relative paths resolve:

```bash
cp -R parcel-claim-preflight /path/to/openclaw/workspace/skills/
```

Suggested check when your OpenClaw CLI supports local skill validation:

```bash
openclaw skills check parcel-claim-preflight
```

Local validation in this repository:

```bash
python3 parcel-claim-preflight/scripts/parcel_claim_preflight.py \
  --shipments parcel-claim-preflight/scripts/fixtures/shipments.csv \
  --evidence-dir parcel-claim-preflight/scripts/fixtures/evidence \
  --today 2026-05-31
```

This runtime was not verified with a local OpenClaw CLI in this automation run.
