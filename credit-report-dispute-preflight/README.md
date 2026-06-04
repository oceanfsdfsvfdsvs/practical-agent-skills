# Credit Report Dispute Preflight

Check credit report error dispute packets before a consumer, helper, or intake team sends bureau disputes, furnisher disputes, identity-theft packets, CFPB complaints, or follow-up letters.

`credit-report-dispute-preflight` is a local-first agent skill for recurring credit report errors where a plain prompt often misses bureau-specific item identity, furnisher routing, identity-theft report needs, repeat-dispute risks, reinserted-item evidence, official report pages, and redaction boundaries.

## Use For

- Equifax, Experian, TransUnion, or furnisher-specific report errors.
- Fraudulent accounts, not-mine accounts, wrong balances/statuses, duplicate tradelines, obsolete collections, mixed files, and personal-information errors.
- Evidence review before dispute letters, furnisher letters, CFPB complaints, housing or lending deadline packets, or legal-aid intake.
- Batch review of credit report issue rows in CSV form plus local evidence folders.

## Why Use This Instead Of A Prompt

- Separates bureau disputes, furnisher disputes, identity-theft packets, and CFPB complaint readiness.
- Requires the exact disputed field, bureau report page, and evidence link instead of generic deletion language.
- Flags repeat disputes without new evidence, reinserted items, live-action requests, and sensitive-file risks.
- Runs a deterministic local fixture script with no credentials or network calls.

## Run

```bash
python3 credit-report-dispute-preflight/scripts/credit_report_dispute_preflight.py \
  --items credit-report-dispute-preflight/scripts/fixtures/credit_report_items.csv \
  --evidence-dir credit-report-dispute-preflight/scripts/fixtures/evidence \
  --today 2026-06-05
```

## Runtime Notes

- Codex/OpenAI: use `SKILL.md` plus `agents/openai.yaml`.
- Claude Code: use `.claude/skills/credit-report-dispute-preflight/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.
- Hermes: see `hermes/README.md`; native runtime verification is blocked until the current Hermes skill spec is confirmed.

No validation step requires bureau portals, CFPB filing, creditor accounts, credentials, paid credit-repair services, or network access.
