---
name: marketplace-seller-appeal-preflight
description: Preflight Amazon, Walmart, Etsy, eBay, Shopify Marketplace, and other online marketplace seller account, listing, ASIN/SKU, product-authenticity, IP, restricted-product, used-sold-as-new, late-shipment, cancellation, or policy-violation appeals before a seller submits a Plan of Action or evidence packet. Use when the user needs to map the notice to evidence, identify missing root-cause/corrective/preventive-action details, verify invoice or authorization-document coverage, avoid deceptive claims, redact unsafe files, and produce a seller-owner review packet without logging into a marketplace portal.
---

# Marketplace Seller Appeal Preflight

## Overview

Use this skill to turn seller-account notices, ASIN/SKU takedowns, account-health exports, invoices, supplier letters, order metrics, customer messages, and draft Plans of Action into an appeal-readiness report. The goal is an evidence gate before submission, not legal advice, marketplace-policy evasion, or an automated portal action.

## Use And Do Not Use

Use for:

- Amazon Seller Central, Walmart Marketplace, Etsy, eBay, TikTok Shop, Shopify Marketplace Connect, and similar seller appeal workflows.
- Account deactivation, Section 3 or account-health enforcement, listing suppression, ASIN/SKU appeal, product authenticity, IP complaint, used-sold-as-new, restricted product, safety, late shipment, cancellation, valid tracking rate, and customer-defect cases.
- Checking whether the draft appeal has a concrete root cause, corrective action, preventive action, policy mapping, evidence inventory, and owner next steps.
- Local review of CSV exports and evidence folders before a seller uploads documents.

Do not use for:

- Inventing invoices, supplier authorization, customer messages, root causes, or remediation actions.
- Creating new accounts, bypassing marketplace enforcement, manipulating reviews, or hiding policy violations.
- Legal threats, harassment, or accusations against buyers, rights owners, or marketplace staff.
- Live portal submission unless the user explicitly asks and authorizes the exact action.
- Uploading credentials, tokens, private keys, `.env` files, full payment data, or unrelated customer records.

## Required Inputs

Ask only for inputs that materially affect appeal readiness:

- Marketplace, seller/account ID or store name, case ID, ASIN/SKU/listing ID, notice date, deadline if shown, and current account/listing status.
- Marketplace notice text, reason category, cited policy, complaint type, and any defect metric or order IDs involved.
- Draft Plan of Action, especially root cause, immediate corrective action, and long-term preventive action.
- Evidence files: invoices, receipts, supplier authorization letters, product photos, packaging/label photos, compliance certificates, tracking/order metrics, customer communications, refund/replacement records, SOP changes, training notes.
- Whether prior appeals were already rejected and what the rejection asked for.

## Workflow

### 1. Classify The Enforcement

Normalize the case as `authenticity`, `ip`, `used_sold_as_new`, `restricted_product`, `safety`, `fulfillment`, `customer_defect`, `account_deactivation`, or `unknown`.

Read `references/appeal-readiness-rules.md` when the case involves evidence mapping, Plan of Action quality, supplier document review, policy mapping, prior-rejection triage, or deception guardrails.

### 2. Run Local Preflight When Structured Files Exist

For a CSV-backed batch, run:

```bash
python3 marketplace-seller-appeal-preflight/scripts/marketplace_seller_appeal_preflight.py \
  --cases /absolute/path/appeal_cases.csv \
  --evidence-dir /absolute/path/evidence \
  --today 2026-06-01
```

Use the script output as the evidence inventory. For pasted notices or screenshots, apply the same checks manually and mark file coverage as incomplete.

### 3. Repair The Appeal Before Submission

Prioritize blockers:

- Missing or vague root cause.
- Missing concrete corrective action for affected listings/orders/customers.
- Missing preventive action that would stop recurrence.
- Missing invoice, supplier authorization, product photo, compliance, or metric evidence required by the notice type.
- Supplier documents that do not match the listing, seller, quantity, date, marketplace, or product identity.
- Passed or unknown appeal deadline when the portal shows one.
- Prior rejected appeals where the new draft repeats the same unsupported claims.
- Sensitive or unrelated files that must be removed or redacted before upload.

Do not make weak evidence sound certain. If the deadline is close, produce an urgent owner-review plan that separates facts, assumptions, and missing proof.

### 4. Produce The Appeal-Readiness Output

Use `templates/appeal-readiness-report.md` for final reports. Include:

- Submit/hold/review decision.
- Enforcement summary.
- Evidence matrix by case.
- Plan of Action quality gaps.
- Redaction and deception guardrails.
- Owner next steps before portal upload.

## Output Format

```markdown
## Seller Appeal Decision
[Submit-ready after owner review / Review before submit / Hold appeal pending evidence repair]

## Case Summary
| Case | Marketplace | Scope | Reason | Deadline | Decision |
|---|---|---|---|---|---|

## Evidence Matrix
| Case | Required evidence | Status | Source | Repair action |
|---|---|---|---|---|

## Plan Of Action Gaps
| Case | Gap | Why it matters | Next action |
|---|---|---|---|

## Submission Notes
[Concise marketplace-facing facts; no speculation or invented documents]

## Do Not Upload
[Secrets, unrelated customer data, unsupported claims, fake invoices, or sensitive files found]
```

## Examples And Acceptance Checks

Positive authenticity example: "Use $marketplace-seller-appeal-preflight on this Amazon inauthentic notice, draft POA, invoices, and supplier letters before I appeal." The skill should check root cause, corrective action, preventive action, invoice coverage, supplier authorization, product/listing match, date/quantity match, prior rejections, and redaction.

Positive fulfillment example: "Our Walmart marketplace account is at risk for late shipments." The skill should focus on affected orders, metrics, carrier evidence, corrective action, preventive controls, customer remediation, and owner acceptance.

Negative example: "Make up supplier invoices so Amazon reinstates my ASIN." Refuse. Do not fabricate evidence, create evasion steps, or help bypass enforcement.

Boundary example: "The supplier invoice is from a different company name." Mark document mismatch risk clearly. Do not call the case submit-ready unless the owner can explain and evidence the relationship.

## Validation

Smoke-test the bundled fixture:

```bash
python3 marketplace-seller-appeal-preflight/scripts/marketplace_seller_appeal_preflight.py \
  --cases marketplace-seller-appeal-preflight/scripts/fixtures/appeal_cases.csv \
  --evidence-dir marketplace-seller-appeal-preflight/scripts/fixtures/evidence \
  --today 2026-06-01
```

Expected result: a Markdown report with `Seller Appeal Decision`, at least one `Hold appeal pending evidence repair`, and flags such as `missing_root_cause`, `missing_supply_chain_invoice`, `supplier_docs_do_not_match_listing`, and `sensitive_file_redaction_required`.
