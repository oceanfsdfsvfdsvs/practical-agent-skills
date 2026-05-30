# Parcel Claim Preflight

Check parcel loss, damage, missing-contents, and late-delivery claim packets before submitting them to a carrier, marketplace, or third-party shipping insurer.

`parcel-claim-preflight` is a local-first agent skill for ecommerce operators, warehouse/support teams, consumers, and claims helpers who need to avoid weak shipping claims caused by missing proof of value, tracking, photos, original packaging, deadlines, or redaction mistakes.

## Use For

- UPS, FedEx, USPS, regional carrier, marketplace, and third-party shipping insurance claim packets.
- Damaged packages, lost packages, missing contents, and late-delivery/service-failure claims.
- Batch review of shipment CSVs plus local evidence folders.

## Why Use This Instead Of A Prompt

- Maps claim type to required evidence instead of producing a generic complaint.
- Flags deadline, declared-value, packaging-retention, and redaction risks.
- Runs a deterministic local fixture script with no carrier credentials or network calls.
- Produces a structured hold/review/submit report for claim owners.

## Run

```bash
python3 parcel-claim-preflight/scripts/parcel_claim_preflight.py \
  --shipments parcel-claim-preflight/scripts/fixtures/shipments.csv \
  --evidence-dir parcel-claim-preflight/scripts/fixtures/evidence \
  --today 2026-05-31
```

## Runtime Notes

- Codex/OpenAI: use `SKILL.md` plus `agents/openai.yaml`.
- Claude Code: use `.claude/skills/parcel-claim-preflight/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.
- Hermes: see `hermes/README.md`; native runtime verification is blocked until the current Hermes skill spec is confirmed.

No validation step requires carrier credentials, live claim portals, or network access.
