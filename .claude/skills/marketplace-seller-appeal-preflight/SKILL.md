---
name: marketplace-seller-appeal-preflight
description: Preflight Amazon, Walmart, Etsy, eBay, Shopify Marketplace, and other online marketplace seller account, listing, ASIN/SKU, product-authenticity, IP, restricted-product, used-sold-as-new, late-shipment, cancellation, or policy-violation appeals before a seller submits a Plan of Action or evidence packet. Use when the user needs to map the notice to evidence, identify missing root-cause/corrective/preventive-action details, verify invoice or authorization-document coverage, avoid deceptive claims, redact unsafe files, and produce a seller-owner review packet without logging into a marketplace portal.
---

# Marketplace Seller Appeal Preflight

Use the repository skill at `marketplace-seller-appeal-preflight/SKILL.md` for the complete workflow, bundled script, references, templates, and fixtures.

Quick validation:

```bash
python3 marketplace-seller-appeal-preflight/scripts/marketplace_seller_appeal_preflight.py \
  --cases marketplace-seller-appeal-preflight/scripts/fixtures/appeal_cases.csv \
  --evidence-dir marketplace-seller-appeal-preflight/scripts/fixtures/evidence \
  --today 2026-06-01
```

Core guardrails: do not invent marketplace evidence, supplier documents, root causes, customer messages, or remediation; do not submit live portal appeals without explicit authority; redact credentials and unrelated customer records before upload.
