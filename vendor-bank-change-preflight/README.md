# Vendor Bank Change Preflight

Stop unsafe vendor bank-detail changes before money moves.

`vendor-bank-change-preflight` is a local-first agent skill for finance, AP, accounting, procurement, operations, and founder-led teams that review supplier ACH, wire, routing, or remittance changes.

It helps an agent inspect exported request packets, compare them with a vendor master, classify payment-redirection risk, and produce an AP-reviewable hold/verification report without connecting to an ERP, bank portal, or supplier portal.

## Problem

Vendor bank-change requests are a high-risk AP control point. Real attacks often arrive inside plausible invoice threads, compromised vendor inboxes, lookalike domains, new-vendor first payments, or urgent payment requests. Teams can know the rule "call the vendor" but still miss evidence, source, approval, and audit-trail details under time pressure.

This skill combines AP fraud-control rules with a deterministic local scanner so an agent can produce a repeatable preflight report before anyone updates payment instructions.

## Why Use This Instead Of A Prompt

- Checks callback completion and whether the callback source was independent from the request.
- Flags lookalike or mismatched email domains against a vendor master.
- Detects bank country mismatch, reused bank details, first payments, new vendors, urgency language, and missing evidence.
- Separates `hold_change`, `secondary_verification`, `document_and_monitor`, and `ready_with_evidence`.
- Keeps the agent inside an operational review boundary instead of changing vendor records or releasing payments.

## Contents

- `SKILL.md` - agent instructions and acceptance checks.
- `agents/openai.yaml` - OpenAI/Codex style metadata.
- `references/bank-change-controls.md` - review rules, failure modes, and evidence checklist.
- `templates/bank-change-review.md` - reviewer-ready report template.
- `examples/sample-report.md` - expected output shape.
- `scripts/vendor_bank_change_preflight.py` - local scanner for CSV/JSON exports.
- `scripts/fixtures/` - smoke-test request and vendor-master exports.
- `openclaw/README.md` and `hermes/README.md` - runtime notes and current verification limits.

## Run

```bash
python3 vendor-bank-change-preflight/scripts/vendor_bank_change_preflight.py \
  --requests vendor-bank-change-preflight/scripts/fixtures/bank_change_requests.csv \
  --vendor-master vendor-bank-change-preflight/scripts/fixtures/vendor_master.csv
```

The script prints Markdown to stdout. It writes a file only when `--output` is provided.

## Inputs

CSV columns are matched case-insensitively. Preferred request fields:

```csv
request_id,vendor_name,vendor_id,requester_email,request_channel,requested_at,effective_date,old_routing,old_account_last4,new_routing,new_account_last4,new_bank_country,vendor_country,amount_at_risk,invoice_id,callback_status,callback_contact_source,callback_performed_by,approver_count,bank_letter_present,w9_present,first_payment,days_since_vendor_created,memo
```

Preferred vendor-master fields:

```csv
vendor_id,vendor_name,trusted_domain,country,current_routing,current_account_last4,trusted_phone_present
```

JSON exports may be a list of objects or an object containing `requests`, `bank_changes`, `vendors`, `suppliers`, or `rows`, depending on the file type.

## Install Notes

Codex/OpenAI-style agents can use the skill directory directly. Claude Code can copy the mirrored `.claude/skills/vendor-bank-change-preflight/SKILL.md` or the whole directory into its skills folder.

OpenClaw and Hermes support is documented but not claimed as fully verified unless the matching local CLI/spec is available.
