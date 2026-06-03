# Rental Security Deposit Dispute Preflight

Check residential rental security deposit return and deduction disputes before a tenant, helper, or property owner sends a demand letter, agency complaint, or small-claims packet.

`rental-security-deposit-dispute-preflight` is a local-first agent skill for recurring deposit disputes where a plain prompt often misses jurisdiction deadlines, itemized-statement requirements, normal wear-and-tear boundaries, forwarding-address proof, receipts, photo evidence, or redaction risks.

## Use For

- Late or missing security deposit refunds.
- Itemized deductions for cleaning, painting, carpet, repairs, unpaid rent, or lease charges.
- Evidence review before demand letters, housing-agency complaints, legal-aid intake, or small claims.
- Batch review of deposit cases in CSV form plus local evidence folders.

## Why Use This Instead Of A Prompt

- Maps state-level deadline rules to dates instead of writing a generic demand letter.
- Separates blockers, review risks, and ready facts without making legal conclusions.
- Flags normal wear-and-tear, missing itemization, missing receipts, forwarding-address, and photo-evidence gaps.
- Runs a deterministic local fixture script with no credentials or network calls.

## Run

```bash
python3 rental-security-deposit-dispute-preflight/scripts/rental_security_deposit_dispute_preflight.py \
  --cases rental-security-deposit-dispute-preflight/scripts/fixtures/deposit_cases.csv \
  --rules rental-security-deposit-dispute-preflight/scripts/fixtures/state_rules.json \
  --evidence-dir rental-security-deposit-dispute-preflight/scripts/fixtures/evidence \
  --today 2026-06-04
```

## Runtime Notes

- Codex/OpenAI: use `SKILL.md` plus `agents/openai.yaml`.
- Claude Code: use `.claude/skills/rental-security-deposit-dispute-preflight/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.
- Hermes: see `hermes/README.md`; native runtime verification is blocked until the current Hermes skill spec is confirmed.

No validation step requires landlord portals, court systems, tenant accounts, credentials, or network access.
