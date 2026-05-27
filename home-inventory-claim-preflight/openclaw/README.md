# OpenClaw Installation Notes

Copy `home-inventory-claim-preflight/` into your OpenClaw workspace skills directory, keeping the full directory tree so relative paths resolve:

```bash
cp -R home-inventory-claim-preflight /path/to/openclaw/workspace/skills/
```

Suggested check when your OpenClaw CLI supports local skill validation:

```bash
openclaw skills check home-inventory-claim-preflight
```

Local validation in this repository:

```bash
python3 home-inventory-claim-preflight/scripts/home_inventory_claim_preflight.py \
  --inventory home-inventory-claim-preflight/scripts/fixtures/contents_inventory.csv \
  --policy home-inventory-claim-preflight/scripts/fixtures/policy.json
```

This runtime was not verified with a local OpenClaw CLI in this automation run.
