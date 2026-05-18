---
name: vendor-bank-change-preflight
description: Review vendor bank-account change requests for payment-redirection, vendor impersonation, and audit-trail risk before AP updates bank details or releases ACH/wire/check payments. Use when finance, accounting, procurement, founders, or operators need a local-first callback and evidence check without connecting to an ERP, bank portal, or supplier portal.
---

# Vendor Bank Change Preflight

Use the repository skill at `vendor-bank-change-preflight/SKILL.md` for the full workflow, scripts, fixtures, references, and runtime notes.

When using this Claude Code mirror:

1. Keep the full repository available so relative paths resolve.
2. Run the local scanner with explicit paths:

```bash
python3 vendor-bank-change-preflight/scripts/vendor_bank_change_preflight.py \
  --requests vendor-bank-change-preflight/scripts/fixtures/bank_change_requests.csv \
  --vendor-master vendor-bank-change-preflight/scripts/fixtures/vendor_master.csv
```

3. Classify rows as `hold_change`, `secondary_verification`, `document_and_monitor`, or `ready_with_evidence`.
4. Never update live vendor records, release payments, or request full bank account numbers from a prompt transcript.

Expected fixture evidence includes `Bank Change Decision`, `hold_change`, `secondary_verification`, `lookalike_email_domain`, and `bank_account_reused_by_another_vendor`.
