# Hermes Runtime Notes

Status: blocked-for-runtime-verification.

This skill does not include a native Hermes handler because local Hermes help shows `hermes skills install` expects a registry identifier or direct HTTP(S) URL to a `SKILL.md` file, and `hermes skills inspect ./flaky-ci-forensics` did not resolve the local directory. To avoid inventing unsupported runtime APIs, this directory documents the blocker instead of shipping a fake adapter.

## Portable Invocation

Use the local script from the skill root:

```bash
python3 scripts/flaky_ci_forensics.py \
  --junit scripts/fixtures/junit.xml \
  --log scripts/fixtures/ci.log \
  --history scripts/fixtures/history.csv
```

## Needed To Complete Native Hermes Support

- Published direct URL or supported registry identifier for this `SKILL.md`.
- Current Hermes native skill schema if a handler is required.
- Handler entrypoint contract.
- Filesystem permissions model.
- Successful `hermes skills inspect` or `hermes skills audit` after installation.
