# Marketplace Seller Appeal Preflight

Check seller-account, listing, ASIN/SKU, product-authenticity, IP, fulfillment, and policy-violation appeal packets before submitting them to an online marketplace.

`marketplace-seller-appeal-preflight` is a local-first agent skill for marketplace sellers, ecommerce operators, agencies, account-health teams, and founders who need to avoid weak appeals caused by vague root causes, missing supplier invoices, unsupported authorization, document/listing mismatches, repeated rejected claims, deadline risk, or unsafe uploads.

## Use For

- Amazon, Walmart Marketplace, Etsy, eBay, TikTok Shop, Shopify Marketplace Connect, and similar seller appeal workflows.
- Account deactivation, listing suppression, ASIN/SKU appeal, authenticity, IP, restricted product, safety, used-sold-as-new, fulfillment, cancellation, and customer-defect cases.
- Batch review of appeal-case CSVs plus local evidence folders.

## Why Use This Instead Of A Prompt

- Maps enforcement type to required evidence instead of producing a generic apology letter.
- Checks the Plan of Action for root cause, corrective action, and preventive action.
- Flags supplier-document mismatches, prior rejected appeal risk, redaction risk, and deceptive-evidence boundaries.
- Runs a deterministic local fixture script with no marketplace credentials, portal login, telemetry, or network calls.

## Run

```bash
python3 marketplace-seller-appeal-preflight/scripts/marketplace_seller_appeal_preflight.py \
  --cases marketplace-seller-appeal-preflight/scripts/fixtures/appeal_cases.csv \
  --evidence-dir marketplace-seller-appeal-preflight/scripts/fixtures/evidence \
  --today 2026-06-01
```

## Runtime Notes

- Codex/OpenAI: use `SKILL.md` plus `agents/openai.yaml`.
- Claude Code: use `.claude/skills/marketplace-seller-appeal-preflight/SKILL.md`.
- OpenClaw: see `openclaw/README.md`.
- Hermes: see `hermes/README.md`; native runtime verification is blocked until the current Hermes skill spec is confirmed.

No validation step requires marketplace credentials, live seller portals, or network access.
