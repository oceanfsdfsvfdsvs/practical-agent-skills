---
name: feature-flag-debt-audit
description: Audit stale feature flags, launch toggles, kill switches, and experiment gates from a flag export plus source tree. Use when a team needs to find expired or unreferenced flags, prevent risky deletes, assign owners, and produce a cleanup plan that is safer than asking an agent to guess from code snippets.
---

# Feature Flag Debt Audit

Use this skill to turn feature-flag debt into an owner-ready cleanup plan. The skill can run the repository scanner at `feature-flag-debt-audit/scripts/feature_flag_debt_audit.py` and then apply the guardrails from `feature-flag-debt-audit/references/cleanup-rules.md`.

## Inputs

- Flag export as CSV or JSON.
- Repository path to scan.
- Stale policy in days.
- Owner and rollout constraints when known.

## Workflow

1. Preserve flag metadata, owner, status, type, last-seen date, expiry, and code references.
2. Run the local scanner when files are available.
3. Classify each flag as `delete_candidate`, `owner_review`, `instrument_first`, or `keep_permanent`.
4. Refuse broad deletion plans without owner approval, production-state evidence, references, tests, and rollback instructions.
5. Return a Markdown cleanup report with guardrails, code references, cleanup tickets, and verification steps.

## Command

```bash
python3 feature-flag-debt-audit/scripts/feature_flag_debt_audit.py \
  --flags feature-flag-debt-audit/scripts/fixtures/flags.csv \
  --code-dir feature-flag-debt-audit/scripts/fixtures/sample_app \
  --stale-days 90 \
  --today 2026-05-12
```

Expected output includes `Flag Debt Decision`, at least one `delete_candidate`, at least one `keep_permanent`, and reference counts.
