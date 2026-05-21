# Invoice Three-Way Match Preflight

Catch invoice, PO, and receipt mismatches before supplier payments are released.

`invoice-three-way-match-preflight` is a local-first agent skill for AP, procurement, receiving, operations, and founder-led teams that review invoices before payment.

It helps an agent inspect structured exports, classify three-way match exceptions, and produce a payment-review packet without connecting to an ERP or handling credentials.

## Problem

Invoice capture tools can extract fields, but AP exceptions usually happen after extraction: no PO, closed PO, missing receipt, partial receipt, vendor mismatch, wrong unit price, quantity overbilling, or an invoice that is already approved even though the match failed.

This skill combines AP-specific exception rules with a deterministic local scanner so an agent can produce a repeatable exception report and owner-specific next steps.

## Why Use This Instead Of A Prompt

- Compares invoice lines against PO lines and receipt quantities.
- Separates `hold_invoice`, `route_exception`, and `review_note`.
- Assigns exceptions to AP, procurement, receiving, or requester/procurement.
- Encodes common failure modes: missing PO, closed or unapproved PO, vendor mismatch, quantity above receipt, unit-price variance, and approved-with-exception state.
- Keeps the agent inside an operational review boundary instead of approving or posting live invoices.

## Contents

- `SKILL.md` - agent instructions and acceptance checks.
- `agents/openai.yaml` - OpenAI/Codex style metadata.
- `references/three-way-match-rules.md` - classification rules and failure modes.
- `templates/exception-report.md` - reviewer-ready report template.
- `examples/sample-report.md` - expected output shape.
- `scripts/invoice_three_way_match_preflight.py` - local scanner for CSV/JSON exports.
- `scripts/fixtures/` - smoke-test invoice, PO, and receipt exports.
- `openclaw/README.md` and `hermes/README.md` - runtime notes and current verification limits.

## Run

```bash
python3 invoice-three-way-match-preflight/scripts/invoice_three_way_match_preflight.py \
  --invoices invoice-three-way-match-preflight/scripts/fixtures/invoices.csv \
  --purchase-orders invoice-three-way-match-preflight/scripts/fixtures/purchase_orders.csv \
  --receipts invoice-three-way-match-preflight/scripts/fixtures/receipts.csv
```

The script prints Markdown to stdout. It writes a file only when `--output` is provided.

## Inputs

CSV columns are matched case-insensitively. Preferred invoice fields:

```csv
invoice_number,vendor_id,vendor_name,po_number,line_id,item_sku,quantity,unit_price,line_amount,currency,approval_status
```

Preferred PO fields:

```csv
po_number,vendor_id,vendor_name,line_id,item_sku,ordered_quantity,unit_price,line_amount,currency,status,approved
```

Preferred receipt fields:

```csv
po_number,line_id,item_sku,received_quantity,rejected_quantity,receipt_date,status
```

JSON exports may be lists or objects containing `invoices`, `invoice_lines`, `purchase_orders`, `po_lines`, `receipts`, `receipt_lines`, or `rows`.

## Install Notes

Codex/OpenAI-style agents can use the skill directory directly. Claude Code can copy the mirrored `.claude/skills/invoice-three-way-match-preflight/SKILL.md` or the whole directory into its skills folder.

OpenClaw and Hermes support is documented but not claimed as fully verified unless the matching local CLI/spec is available.
