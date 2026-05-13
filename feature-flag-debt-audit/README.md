# Feature Flag Debt Audit

Find stale feature flags without deleting your kill switches.

`feature-flag-debt-audit` is a local-first agent skill for engineering and platform teams that need to clean up release toggles, experiments, migration gates, and operational flags without guessing from code snippets.

## Problem

Teams often add release toggles, experiments, and kill switches faster than they remove them. Stale flags increase branching complexity, make tests harder to reason about, and can turn cleanup into a risky guessing exercise.

This skill combines a repeatable cleanup workflow with a deterministic local scanner so an agent can separate likely delete candidates from flags that need owner review or must remain permanent.

## Why Use This Instead Of A Prompt

- Normalizes CSV/JSON flag exports and scans source references locally.
- Separates `delete_candidate`, `owner_review`, `instrument_first`, and `keep_permanent`.
- Preserves guardrails for kill switches, billing/auth/security paths, migrations, and entitlement flags.
- Produces cleanup tickets with owner, evidence, verification, and rollback steps.

## Contents

- `SKILL.md` - agent instructions and acceptance checks.
- `agents/openai.yaml` - OpenAI/Codex style metadata.
- `references/cleanup-rules.md` - classification rules and failure modes.
- `templates/cleanup-ticket.md` - owner-ready ticket template.
- `examples/sample-report.md` - expected output shape.
- `scripts/feature_flag_debt_audit.py` - local scanner for CSV/JSON flag exports and code references.
- `scripts/fixtures/` - smoke-test flag export and sample app.
- `openclaw/README.md` and `hermes/README.md` - runtime notes and current verification limits.

## Run

```bash
python3 feature-flag-debt-audit/scripts/feature_flag_debt_audit.py \
  --flags feature-flag-debt-audit/scripts/fixtures/flags.csv \
  --code-dir feature-flag-debt-audit/scripts/fixtures/sample_app \
  --stale-days 90 \
  --today 2026-05-12
```

The script prints Markdown to stdout. It writes a file only when `--output` is provided.

## Inputs

CSV columns are matched case-insensitively. Preferred fields:

```csv
key,name,status,kind,owner,created_at,last_seen,expires_at,permanent,description
```

JSON exports may be either a list of flag objects or an object with a `flags` list.

## Install Notes

Codex/OpenAI-style agents can use the skill directory directly. Claude Code can copy the mirrored `.claude/skills/feature-flag-debt-audit/SKILL.md` or the whole directory into its skills folder.

OpenClaw and Hermes support is documented but not claimed as fully verified unless the matching local CLI/spec is available.
