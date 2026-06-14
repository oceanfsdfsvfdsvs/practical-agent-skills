---
name: tax-notice-response-preflight
description: Preflight IRS or state tax notice response packets before a taxpayer, tax preparer, bookkeeper, clinic, or caregiver replies, pays, uploads documents, requests more time, or escalates. Use when the user has CP2000, CP14, CP53E, CP05, notice-of-deficiency, refund hold, balance-due, identity-theft, payment-mismatch, underreported-income, penalty, or confusing tax correspondence and needs deadline, authenticity, evidence, routing, privacy, and professional-help gates without live filing or tax advice.
---

# Tax Notice Response Preflight

Use the full skill directory at `tax-notice-response-preflight/` so references, templates, examples, and scripts stay available.

Core workflow:

1. Preserve privacy: redact SSNs, full EINs, bank account numbers, IRS online-account credentials, transcript control numbers, and unrelated tax files.
2. Read `tax-notice-response-preflight/references/tax-notice-rules.md` before classifying packet readiness.
3. Run the local script when notice/evidence files are available:

```bash
python3 tax-notice-response-preflight/scripts/tax_notice_response_preflight.py \
  --notices /absolute/path/notices.csv \
  --evidence /absolute/path/evidence.csv \
  --policy /absolute/path/policy.json \
  --today YYYY-MM-DD
```

4. Produce a response-readiness report with deadline, authenticity, evidence, professional-review, delivery-proof, and live-action guardrails.
5. Do not provide final tax, legal, accounting, investment, identity-theft recovery, or representation advice. Do not file, upload, fax, mail, pay, call, or update bank details unless the user explicitly authorizes the live action and remains in control.
