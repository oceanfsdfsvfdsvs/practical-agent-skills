---
name: contract-renewal-risk-preflight
description: Preflight vendor and SaaS contract renewals for auto-renewal, cancellation notice, stale owner, notice-method, spend, and usage-risk gaps. Use when procurement, finance, IT, ops, or founders need an owner-ready renewal action plan from local spreadsheets or contract extracts without contacting vendors or giving legal advice.
---

# Contract Renewal Risk Preflight

## Overview

Use this skill to turn vendor contract renewal data into a reviewable renewal action plan. The goal is to catch missed or imminent auto-renewal notice windows, owner gaps, notice-method gaps, high-spend renewals, and low-value renewals before the team loses cancellation or negotiation leverage.

## Use And Do Not Use

Use for:

- SaaS, software, telecom, agency, facilities, and other vendor contract renewals.
- Contract inventories from spreadsheets, CLM exports, SaaS management tools, shared drives, or manually extracted clauses.
- Calculating cancellation notice deadlines from renewal dates and required notice days.
- Prioritizing renew, renegotiate, cancel, or legal/procurement review actions.
- Producing an owner action plan and notice-proof checklist.

Do not use for:

- Legal advice or enforceability opinions.
- Sending cancellation, non-renewal, or termination notices without explicit user instruction and verified authority.
- Contacting vendors, logging into SaaS accounts, or modifying contract systems.
- Reviewing confidential full contracts unless the user provides local files and confirms they can be processed.
- Consumer subscription cancellation advice; this skill is for business vendor contracts.

## Required Inputs

Ask only for missing inputs that materially affect the decision:

- Contract inventory path, extracted clause JSON, or pasted table.
- Preferred fields: `vendor`, `contract_id`, `owner`, `department`, `annual_cost`, `currency`, `renewal_date`, `notice_days`, `notice_deadline`, `auto_renew`, `renewal_term`, `price_increase_cap`, `termination_notice_method`, `notice_address`, `last_review_date`, `usage_status`, `notes`.
- Review date if not today.
- Urgency threshold, such as 14 days before notice deadline.
- High-spend threshold, such as USD 25,000 annual spend.
- Whether spreadsheet fields came from contract clauses or human-entered reminders.

If only renewal dates are supplied, say that cancellation deadlines are not reliable until notice periods are extracted.

## Workflow

### 1. Preserve The Renewal Boundary

Before advising action, capture:

- Renewal date and notice deadline.
- How notice deadline was calculated or extracted.
- Auto-renewal status.
- Owner, department, and authority path.
- Required notice method and recipient.
- Annual cost, renewal term, price uplift cap, usage status, and last review date.

Read `references/renewal-risk-rules.md` before classifying a contract as safe to monitor.

### 2. Run The Local Preflight

Use the bundled script with explicit paths:

```bash
python3 contract-renewal-risk-preflight/scripts/contract_renewal_risk_preflight.py \
  --contracts /absolute/path/contracts.csv \
  --today 2026-05-16
```

For JSON input, the script accepts a list of contract objects or an object containing `contracts`, `rows`, `vendors`, or `agreements`.

### 3. Classify Renewal Risk

Use one primary action:

- `escalate_missed_window`: notice deadline appears to have passed for an auto-renewing contract.
- `send_or_escalate_notice`: notice deadline is imminent or risk signals are severe.
- `owner_review`: owner, notice, spend, value, or price evidence needs human decision.
- `renegotiate_window`: deadline is far enough away to benchmark, consolidate, or renegotiate.
- `monitor`: key fields are complete and no material deadline risk appears.

Use one primary risk:

- `high`: missed or imminent notice deadline, unknown notice deadline on auto-renewal, missing owner on a near-term contract, or high-spend renewal with multiple gaps.
- `medium`: deadline within 90 days, missing notice recipient/method, stale review, or value concerns.
- `low`: complete owner, notice, renewal, spend, and review fields with no near-term action.

Never treat a renewal date alone as the cancellation deadline.

### 4. Produce The Renewal Action Plan

Return:

```markdown
## Renewal Portfolio Decision
[Immediate escalation / Act this week / Owner review needed / No urgent renewal risk found]

## Renewal Risk Summary
[Counts by risk, missing deadline, missed window]

## Renewal Exceptions
| Risk | Action | Vendor | Owner | Spend | Renewal | Notice deadline | Evidence | Next step |
|---|---|---|---|---:|---|---|---|---|

## Owner Action Plan
[One action per high/medium contract]

## Guardrails
[Notice proof, legal review, authority, source confidence]
```

Use `templates/renewal-action-plan.md` when the user asks for a reusable artifact.

### 5. Apply Guardrails Before Recommending Notice

Do not say a notice has been validly sent or that a contract can legally be cancelled unless the user provides proof. Instead:

- Confirm the required method and recipient.
- Confirm who is authorized to send notice.
- Preserve a copy of the notice, delivery proof, and vendor acknowledgement.
- Mark spreadsheet-only clause extraction as provisional.
- Escalate legal questions instead of interpreting enforceability.

## Examples And Acceptance Checks

Positive example: "Use $contract-renewal-risk-preflight on this vendor renewal spreadsheet before Q3 renewals." The skill should calculate notice deadlines, prioritize urgent auto-renewals, and create owner actions.

Positive clause-extract example: "I extracted renewal clauses from five SaaS contracts into JSON." The skill should use the extracted fields but mark legal interpretation out of scope.

Negative example: "Cancel all contracts that look unused." Do not send or recommend cancellation without owner, clause, method, and authority checks.

Boundary example: "I only have renewal dates." Produce a missing-notice-period report and ask for notice clauses before ranking cancellation urgency.

## Validation

Smoke-test the bundled fixture:

```bash
python3 contract-renewal-risk-preflight/scripts/contract_renewal_risk_preflight.py \
  --contracts contract-renewal-risk-preflight/scripts/fixtures/contracts.csv \
  --today 2026-05-16
```

Expected result: a Markdown report with `Renewal Portfolio Decision`, at least one `escalate_missed_window`, at least one `send_or_escalate_notice`, `missing_notice_deadline`, and `uncapped_price_increase`.
