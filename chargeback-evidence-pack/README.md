# Chargeback Evidence Pack

Build a cleaner chargeback response before the dispute deadline.

`chargeback-evidence-pack` is a local-first agent skill for merchants, ecommerce operators, SaaS founders, and payment operations teams that need to assemble dispute evidence without leaking secrets or uploading irrelevant customer data.

## Use For

- Product-not-received, digital-goods, subscription, and service disputes.
- Reviewing order receipts, delivery/tracking records, terms acceptance, support logs, and customer communication.
- Producing a challenge/accept recommendation with evidence gaps.

## Why Use This Instead Of A Prompt

- Maps evidence to dispute reason-code expectations.
- Flags missing proof before a weak response is submitted.
- Redacts or blocks unsafe material such as full card data, credentials, raw private logs, or unrelated customer records.
- Produces a structured evidence inventory instead of a generic appeal paragraph.

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
