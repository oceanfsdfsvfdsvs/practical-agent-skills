# OpenClaw Install Notes

Copy the full skill directory into your OpenClaw skills workspace so relative scripts, fixtures, references, and templates stay together.

```bash
mkdir -p ~/.openclaw/skills
cp -R fsa-claim-substantiation-preflight ~/.openclaw/skills/
```

Suggested validation when your OpenClaw CLI supports local skill checks:

```bash
openclaw skills check fsa-claim-substantiation-preflight
```

Local script smoke test:

```bash
python3 fsa-claim-substantiation-preflight/scripts/fsa_claim_substantiation_preflight.py \
  --claims fsa-claim-substantiation-preflight/scripts/fixtures/fsa_claims.csv \
  --evidence-dir fsa-claim-substantiation-preflight/scripts/fixtures/evidence \
  --today 2026-06-03
```

This repository does not claim OpenClaw native validation unless the skill is installed into an OpenClaw-managed skills directory and the CLI check passes.
