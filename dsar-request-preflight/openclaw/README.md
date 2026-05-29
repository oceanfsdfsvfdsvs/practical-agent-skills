# OpenClaw Install Notes

Copy the full `dsar-request-preflight/` directory into your OpenClaw workspace skills directory.

Suggested check when your OpenClaw CLI supports local skill checks:

```bash
openclaw skills check dsar-request-preflight
```

If your OpenClaw installation expects a registry package or ClawHub metadata, use this directory as source material until that packaging path is configured.

Local validation that does not require OpenClaw:

```bash
python3 dsar-request-preflight/scripts/dsar_request_preflight.py \
  --requests dsar-request-preflight/scripts/fixtures/requests.csv \
  --systems dsar-request-preflight/scripts/fixtures/systems.csv \
  --policy dsar-request-preflight/scripts/fixtures/policy.json \
  --today 2026-05-30
```

This run was not claimed as OpenClaw-native verification unless `openclaw skills check` is available and run successfully on the target machine.
