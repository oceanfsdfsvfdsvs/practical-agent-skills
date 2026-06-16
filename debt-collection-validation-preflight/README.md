# Debt Collection Validation Preflight

Local-first skill for checking debt collection validation and dispute packets before a user responds to a collector, debt buyer, collection agency, or collection law firm.

## Best For

- Consumers, caregivers, financial counselors, legal-aid intake helpers, and benefits advocates.
- Collection letters, validation notices, debt-buyer notices, medical collections, not-mine debts, paid or settled debts, wrong amounts, old debts, and continued collection after a written dispute.
- Pre-send packet review where a generic prompt might miss dates, notice defects, evidence gaps, or risky live actions.

## What It Produces

- Debt collection validation readiness decision.
- Validation-window and mailing timeline.
- Notice, collector identity, and evidence matrix.
- Blockers, review flags, and owner next steps.
- Redaction and no-live-action guardrails.

## Run The Fixture

```bash
python3 debt-collection-validation-preflight/scripts/debt_collection_validation_preflight.py \
  --cases debt-collection-validation-preflight/scripts/fixtures/debt_collection_cases.csv \
  --evidence-dir debt-collection-validation-preflight/scripts/fixtures/evidence \
  --today 2026-06-17
```

The fixture intentionally returns exit code `2` because several sample cases should be blocked pending evidence repair.

## Runtime Notes

- Codex/OpenAI-style agents: use `SKILL.md` and `agents/openai.yaml`.
- Claude Code: copy `.claude/skills/debt-collection-validation-preflight/SKILL.md` into the Claude skills directory, keeping this full folder nearby for scripts and references.
- OpenClaw: see `openclaw/README.md`.
- Hermes: see `hermes/README.md`; native Hermes execution is blocked pending a verified local runtime spec.

## Safety

The script reads only explicit input paths and makes no network calls. Do not include full SSNs, full ID scans, bank/card credentials, full account numbers, private keys, tokens, `.env` files, or unrelated consumer records.
