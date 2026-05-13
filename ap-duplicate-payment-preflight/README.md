# AP Duplicate Payment Preflight

Local-first skill for finding duplicate-payment risk in accounts payable exports before payment release.

## Problem

AP teams often rely on ERP warnings that catch only exact duplicates. Real duplicate payments often appear as vendor aliases, OCR invoice-number variants, resubmitted bills, or paid-versus-pending collisions that require a repeatable review process.

This skill combines AP-specific review rules with a deterministic local scanner so an agent can produce a payment-run exception report without connecting to accounting systems or handling credentials.

## Contents

- `SKILL.md` - agent instructions and acceptance checks.
- `agents/openai.yaml` - OpenAI/Codex style metadata.
- `references/duplicate-payment-rules.md` - classification rules and failure modes.
- `templates/exception-report.md` - reviewer-ready report template.
- `examples/sample-report.md` - expected output shape.
- `scripts/ap_duplicate_payment_preflight.py` - local scanner for CSV/JSON exports.
- `scripts/fixtures/` - smoke-test AP export.
- `openclaw/README.md` and `hermes/README.md` - runtime notes and current verification limits.

## Run

```bash
python3 ap-duplicate-payment-preflight/scripts/ap_duplicate_payment_preflight.py \
  --payments ap-duplicate-payment-preflight/scripts/fixtures/ap_payments.csv \
  --date-window-days 14
```

The script prints Markdown to stdout. It writes a file only when `--output` is provided.

## Inputs

CSV columns are matched case-insensitively. Preferred fields:

```csv
vendor_name,vendor_id,invoice_number,invoice_date,payment_date,amount,currency,status,po_number
```

JSON exports may be a list of payment objects or an object containing `payments`, `invoices`, `bills`, or `rows`.

## Install Notes

Codex/OpenAI-style agents can use the skill directory directly. Claude Code can copy the mirrored `.claude/skills/ap-duplicate-payment-preflight/SKILL.md` or the whole directory into its skills folder.

OpenClaw and Hermes support is documented but not claimed as fully verified unless the matching local CLI/spec is available.
