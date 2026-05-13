# OpenClaw Installation Notes

Status: blocked-for-runtime-verification.

## Install

Copy this skill directory into the OpenClaw workspace skills directory:

```bash
cp -R flaky-ci-forensics /path/to/openclaw/workspace/skills/
```

Then run the closest available OpenClaw validation command:

```bash
openclaw skills check
openclaw skills info flaky-ci-forensics --json
```

## Blocker

The `openclaw` CLI is available, but `openclaw skills install` installs by ClawHub slug and `openclaw skills info flaky-ci-forensics --json` returned `not found` before publication. This repository does not claim successful OpenClaw runtime execution until the skill is published or copied into an OpenClaw-recognized workspace and `openclaw skills check` reports it as visible.
