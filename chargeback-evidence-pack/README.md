# Chargeback Evidence Pack

Local-first skill for assembling merchant chargeback/dispute evidence packs without exposing secrets or unrelated customer data.

## Use For

- Product-not-received, digital-goods, subscription, and service disputes.
- Reviewing order receipts, delivery/tracking records, terms acceptance, support logs, and customer communication.
- Producing a challenge/accept recommendation with evidence gaps.

## Run

```bash
python3 chargeback-evidence-pack/scripts/chargeback_evidence_pack.py \
  --case chargeback-evidence-pack/scripts/fixtures/case_product_not_received.json \
  --evidence-dir chargeback-evidence-pack/scripts/fixtures/evidence
```

## Runtime Notes

- Codex/OpenAI: use `SKILL.md` plus `agents/openai.yaml`.
- Claude Code: use `.claude/skills/chargeback-evidence-pack/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.

No validation step requires payment processor credentials or network access.
