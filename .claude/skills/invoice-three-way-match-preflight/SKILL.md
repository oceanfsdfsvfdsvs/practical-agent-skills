---
name: invoice-three-way-match-preflight
description: Review supplier invoice lines against purchase orders and receiving records before payment release. Use when AP, procurement, receiving, operations, or founders need a local three-way match exception report that flags missing POs, unapproved or closed POs, vendor mismatches, quantity/price variance, missing receipts, and already-approved invoices with unresolved exceptions.
---

# Invoice Three-Way Match Preflight

Use the repository skill at `invoice-three-way-match-preflight/SKILL.md`.

When installed as a Claude Code skill mirror, keep the full repository available so relative paths to `scripts/`, `references/`, `templates/`, and `examples/` resolve correctly.

Run the fixture smoke test:

```bash
python3 invoice-three-way-match-preflight/scripts/invoice_three_way_match_preflight.py \
  --invoices invoice-three-way-match-preflight/scripts/fixtures/invoices.csv \
  --purchase-orders invoice-three-way-match-preflight/scripts/fixtures/purchase_orders.csv \
  --receipts invoice-three-way-match-preflight/scripts/fixtures/receipts.csv
```

Follow the canonical workflow in the root skill file: preserve the AP review boundary, compare invoice lines against purchase orders and receipts, classify exceptions by risk/action/owner, and do not approve, post, cancel, or pay live invoices.
