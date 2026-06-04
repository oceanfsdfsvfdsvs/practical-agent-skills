---
name: credit-report-dispute-preflight
description: Preflight credit report error disputes before a consumer, caregiver, housing or financial counselor, benefits advocate, or legal-aid intake helper sends a bureau dispute, furnisher dispute, identity-theft packet, CFPB complaint, or follow-up letter. Use when the user needs to check Equifax, Experian, TransUnion, or furnisher-specific report items, evidence gaps, identity-theft report needs, repeat-dispute risks, reinserted items, deadline tracking, redaction risks, and owner next steps without filing live disputes or giving legal conclusions.
---

# Credit Report Dispute Preflight

## Overview

Use this skill to turn credit report pages, account rows, bureau responses, creditor records, identity-theft reports, and correspondence into a dispute-readiness report. The goal is an evidence and deadline gate before a user sends a dispute letter, furnisher letter, CFPB complaint, or follow-up packet. It is not legal advice, credit repair, or a guarantee that a bureau or furnisher will remove an item.

## Use And Do Not Use

Use for:

- Credit report errors involving Equifax, Experian, TransUnion, other consumer reporting agencies, or furnishers.
- Consumers, caregivers, housing counselors, financial coaches, benefits advocates, and legal-aid intake helpers preparing a dispute packet.
- Fraudulent accounts, mixed files, duplicate tradelines, wrong balance/status, paid debt still reported, stale collection dates, wrong personal information, and bureau-vs-bureau mismatch review.
- Local file review where evidence is in CSV rows, pasted notes, screenshots, PDFs, letters, or mail receipts.

Do not use for:

- Live bureau portal submission, live CFPB complaint filing, paid credit-repair tactics, guaranteed deletion claims, or advice to dispute accurate debts in bad faith.
- Inventing payment records, identity-theft reports, creditor responses, dates, addresses, or bureau outcomes.
- Jurisdiction-specific legal certainty when facts, report source, current law, or bureau response status is uncertain. Mark rules as "verify before send."
- Uploading full SSNs, full ID scans, bank credentials, full card numbers, private keys, tokens, `.env` files, or unrelated consumer records.

## Required Inputs

Ask only for missing inputs that materially affect the decision:

- Report source and bureau: Equifax, Experian, TransUnion, another CRA, or furnisher response.
- Item identity: account or collection name, furnisher, masked account number if available, report date, bureau-specific item label, and page/screenshot reference.
- Error type: not mine, identity theft, paid/settled but still showing, wrong balance, wrong status, duplicate, obsolete/stale, authorized-user issue, mixed file, personal information error, or investigation response problem.
- Evidence: highlighted report page, government or FTC identity-theft report when applicable, payment or payoff proof, creditor/furnisher letter, account statements, police report if available, mailing receipt, bureau response, prior dispute packet, and proof of address/name correction.
- Timeline: date report pulled, dispute sent, bureau response received, furnisher response received, item reappeared, and target deadline.

## Workflow

### 1. Classify The Dispute

Normalize each item as `identity_theft`, `not_mine`, `paid_or_settled`, `wrong_balance_or_status`, `duplicate_or_mixed_file`, `obsolete_or_stale`, `personal_info`, `investigation_response`, or `mixed`. Identify whether the packet should go to the bureau, the furnisher, or both.

Read `references/credit-report-dispute-rules.md` when the case involves identity theft, repeat disputes, reinserted items, stale dates, furnisher routing, CFPB complaint readiness, or dispute-letter hygiene.

### 2. Run Local Preflight When Files Exist

For CSV-backed batches, run:

```bash
python3 credit-report-dispute-preflight/scripts/credit_report_dispute_preflight.py \
  --items /absolute/path/credit_report_items.csv \
  --evidence-dir /absolute/path/evidence \
  --today 2026-06-05
```

Use the script output as the evidence inventory. For pasted notes or screenshots, apply the same matrix manually and mark file coverage as incomplete.

### 3. Repair The Packet Before Sending

Prioritize blockers:

- The disputed item is not identified by bureau, furnisher/account, and specific error.
- No highlighted report page or bureau-specific copy supports the item.
- Identity-theft or fraud claims lack an FTC IdentityTheft.gov report, police report, or equivalent sworn report when needed.
- Payment, payoff, settlement, or account-status claims lack creditor/furnisher proof.
- The packet repeats a prior verified dispute without new evidence or a narrower error theory.
- The item reappeared after deletion but no prior deletion/response proof is attached.
- User asks the agent to file a live bureau dispute, CFPB complaint, freeze, or portal action without explicit authorization.

If a mortgage, rental, job, or benefits deadline is close, separate "send a narrow preservation packet now" from "evidence still missing." Do not turn weak facts into certainty.

### 4. Produce The Dispute-Readiness Output

Use `templates/dispute-readiness-report.md` for final reports. Include:

- Hold/review/ready decision.
- Bureau/furnisher routing.
- Item-by-item evidence matrix.
- Missing evidence and how to obtain or label it.
- Repeat-dispute, reinserted-item, identity-theft, and deadline risks.
- Redaction and live-action guardrails.

## Output Format

```markdown
## Credit Report Dispute Decision
[Ready for owner review / Review before send / Hold dispute packet pending evidence repair]

## Item Summary
| Item | Bureau | Furnisher | Error Type | Decision |
|---|---|---|---|---|

## Evidence Matrix
| Item | Evidence | Status | Source | Repair action |
|---|---|---|---|---|

## Blockers
| Item | Blocker | Why it matters | Next action |
|---|---|---|---|

## Review Flags
| Item | Flag | Why it matters | Next action |
|---|---|---|---|

## Packet Notes
[Concise facts, dates, disputed fields, requested correction, and attachments; no threats or unsupported deletion claims]

## Do Not Upload
[Full SSNs, full IDs, account credentials, full card/bank data, private keys, tokens, or unrelated records]
```

## Examples And Acceptance Checks

Positive example: "Use $credit-report-dispute-preflight on these three credit report pages, bureau response letters, and payoff proof before I send disputes." The skill should classify each item, check bureau/furnisher routing, require highlighted report pages, attach payment proof, and flag repeat-dispute risks.

Positive batch example: "Review these 20 credit report issue rows for a housing counselor intake clinic." The skill should produce row-level hold/review/ready decisions and identify which evidence is missing.

Negative example: "Write a letter that forces deletion of every negative item." Do not make guaranteed deletion claims. Produce a fact-grounded dispute packet or explain why the item should not be disputed.

Boundary example: "I only have a Credit Karma screenshot." Mark the source as incomplete, ask for the official bureau report page, and avoid bureau-specific conclusions until it is supplied.

## Validation

Smoke-test the bundled fixture:

```bash
python3 credit-report-dispute-preflight/scripts/credit_report_dispute_preflight.py \
  --items credit-report-dispute-preflight/scripts/fixtures/credit_report_items.csv \
  --evidence-dir credit-report-dispute-preflight/scripts/fixtures/evidence \
  --today 2026-06-05
```

Expected result: a Markdown report with `Credit Report Dispute Decision`, at least one `Hold dispute packet pending evidence repair`, and flags such as `identity_theft_report_missing`, `highlighted_report_page_missing`, `repeat_dispute_needs_new_evidence`, `reinserted_item_prior_deletion_missing`, and `live_action_requested`.
