# OpenClaw Notes

Install by copying the full `invoice-three-way-match-preflight` directory into your OpenClaw workspace skills directory.

Suggested check after installation when your OpenClaw CLI supports workspace skill checks:

```bash
openclaw skills check --json
```

The local script uses only Python standard-library modules and explicit input paths. Keep the full directory available so `scripts/fixtures/`, `references/`, and `templates/` remain resolvable.

Current verification status: the local environment has `openclaw`, but this skill was not installed into the OpenClaw managed skills directory during this repository validation. Treat OpenClaw runtime execution as pending until the directory is copied into the target OpenClaw workspace and `openclaw skills check --json` reports it visible.
