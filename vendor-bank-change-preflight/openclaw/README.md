# OpenClaw Notes

This skill is local-first and can be installed by copying the `vendor-bank-change-preflight/` directory into the OpenClaw workspace skills directory.

Suggested manual check when the OpenClaw CLI is available:

```bash
openclaw skills check --json
```

Runtime status for this workspace: OpenClaw CLI was available, but this repo-local skill was not installed into `/Users/ocean/.openclaw/skills`, so no per-skill OpenClaw runtime validation is claimed. Do not claim OpenClaw registry or ClawHub support until the skill is installed and visible in `openclaw skills check`.
