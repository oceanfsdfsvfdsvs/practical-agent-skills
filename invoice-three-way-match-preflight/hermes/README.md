# Hermes Notes

Hermes-native packaging could not be claimed without a locally verified Hermes skill specification and CLI.

Use this skill as a Markdown workflow skill by pointing Hermes or a Hermes-compatible agent at:

```text
invoice-three-way-match-preflight/SKILL.md
```

The local script can be run directly:

```bash
python3 invoice-three-way-match-preflight/scripts/invoice_three_way_match_preflight.py \
  --invoices invoice-three-way-match-preflight/scripts/fixtures/invoices.csv \
  --purchase-orders invoice-three-way-match-preflight/scripts/fixtures/purchase_orders.csv \
  --receipts invoice-three-way-match-preflight/scripts/fixtures/receipts.csv
```

Status: `blocked-for-runtime-verification` for Hermes-native handler packaging. The local environment has `hermes`, but `hermes skills inspect ./invoice-three-way-match-preflight` did not accept this repository path as an installed or registry source during validation, so no Hermes-native success is claimed.
