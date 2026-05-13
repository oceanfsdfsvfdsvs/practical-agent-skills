---
name: security-questionnaire-triage
description: Triage B2B customer security questionnaires, vendor risk assessments, SIG/CAIQ/HECVAT-style requests, and due-diligence spreadsheets before a seller responds. Use when a user needs evidence-backed answers, reviewer routing, redaction guidance, or a safe response pack without inventing security claims or leaking sensitive details.
---

# Security Questionnaire Triage

## Overview

Use this skill when a team has to answer a customer, partner, procurement, GRC, or vendor-risk questionnaire and needs a defensible response plan. The goal is not to sound compliant; it is to separate answerable questions from evidence gaps, risky disclosures, stale claims, and questions that need security, legal, privacy, product, or infrastructure review.

## Use and Do Not Use

Use for:

- B2B customer security questionnaires, vendor risk assessments, due-diligence questionnaires, SIG, CAIQ, HECVAT, RFP security sections, trust-center follow-ups, and customer audit requests.
- Turning a spreadsheet or pasted questions into a domain-routed reviewer queue.
- Reusing an approved answer bank and evidence register while flagging stale or unsupported answers.
- Preparing a safe buyer response pack with citations to internal evidence labels, redaction notes, and open blockers.

Do not use for:

- Assessing whether a third-party vendor is secure for the user's organization; use a vendor-risk or security review workflow instead.
- Creating policies, SOC 2 controls, legal commitments, breach notices, insurance answers, or privacy terms from scratch.
- Sharing raw secrets, credentials, customer data samples, vulnerability details, production IP ranges, logs, or private architecture evidence directly in a worksheet.
- Treating previous answers as true when no current evidence is available.

## Required Inputs

Ask only for missing inputs that materially change the response decision:

- Questionnaire file path, pasted questions, or worksheet export.
- Seller/company context: product scope, deployment model, data categories, regions, and target customer.
- Approved source material: SOC 2 or ISO evidence labels, policy names, trust-center URLs, architecture notes, subprocessors, DPAs, prior answer bank, or an evidence register.
- Buyer constraints: deadline, required format, NDA status, procurement stage, and whether attachments are allowed.
- Reviewers and owners for security, legal, privacy, infrastructure, product, and sales.

If source material is missing, proceed with a triage-only pass and mark answers as "needs evidence" instead of drafting unsupported claims.

## Workflow

### 1. Classify The Request

Identify:

- Buyer and business stage.
- Questionnaire type and row count.
- Whether the user is the seller responding or the buyer evaluating a vendor.
- Which questions affect legal commitments, privacy claims, security posture, customer data, uptime, AI training, or regulated data.
- Whether the requested evidence can be shared under the current NDA and channel.

Do not answer as a vendor-risk evaluator unless the user explicitly asks for that different workflow.

### 2. Build The Evidence Boundary

Create or update an evidence register before drafting:

```csv
evidence_id,title,domain,owner,last_reviewed,confidentiality,status,location,notes
SOC2-001,SOC 2 Type II report,compliance_audit,GRC Lead,2026-04-10,confidential,approved,Trust portal,Share only under NDA
```

Use `templates/evidence-register.csv` as the starting point when the user does not have one.

Evidence rules:

- Treat only approved, current evidence as answer support.
- Record an owner for every evidence item.
- Mark stale evidence when it is older than the user's policy, usually 12 months unless the user provides a stricter rule.
- Use internal evidence labels or trust-center links in drafts; do not paste private attachments, secrets, raw logs, keys, customer data, or screenshots into the response.
- If evidence conflicts with a prior answer, route for review instead of smoothing over the conflict.

Read `references/response-rules.md` before drafting answers, especially for answer status rules, redaction gates, and domain routing.

### 3. Run Local Triage For File-Backed Questionnaires

For CSV, TSV, TXT, or Markdown question lists, run:

```bash
python3 security-questionnaire-triage/scripts/security_questionnaire_triage.py /absolute/path/questions.csv --evidence-register /absolute/path/evidence-register.csv --answer-bank /absolute/path/answer-bank.csv
```

The evidence register and answer bank are optional. If omitted, the script still groups questions, flags sensitive disclosures, and produces a reviewer queue.

For `.xlsx` workbooks, export the relevant worksheet to CSV first or use a local conversion tool already available in the user's environment. Preserve the original workbook unchanged, record the worksheet name, and do not flatten hidden sheets, comments, formulas, or attachments into answers unless the user explicitly asks for that review. See `references/response-rules.md` for the Excel intake checklist.

Supported answer bank columns:

```csv
domain,question_pattern,answer,evidence_id,owner,last_reviewed,confidence
identity_access,mfa|multi-factor,Access to production systems requires MFA and role-based approval.,MFA-001,Security Lead,2026-04-10,high
```

### 4. Assign Response Status

Use these statuses:

- `ready_with_cited_answer`: approved answer plus current evidence exists.
- `draft_needs_answer_owner`: current evidence exists, but the exact wording needs an owner-approved answer.
- `needs_evidence`: question is answerable, but current proof is missing or stale.
- `sme_or_legal_review`: answer may create a legal, privacy, commercial, incident, AI, or regulated-data commitment.
- `do_not_answer_in_sheet`: request asks for secrets, raw vulnerabilities, credentials, detailed production network data, raw logs, customer data samples, or private evidence that belongs in a controlled channel.
- `not_applicable_candidate`: the question appears outside product scope; confirm before marking N/A.

Never convert a missing answer into "yes" just because the claim is common in SaaS. Use "not confirmed", "planned", "not applicable", or "available under NDA" only when the source material supports it.

### 5. Produce The Buyer Response Pack

Return:

```markdown
## Response Decision
[Ready to submit / Submit after owner review / Blocked by evidence gaps / Do not submit in current format]

## Triage Summary
| Status | Count | Action |
|---|---:|---|

## Reviewer Queue
| Owner | Questions | Reason | Due |
|---|---:|---|---|

## High-Risk Rows
| Question ID | Domain | Risk | Safe next step |
|---|---|---|---|

## Draftable Answers
| Question ID | Draft | Evidence label | Reviewer |
|---|---|---|---|

## Evidence Requests
| Evidence needed | Domain | Owner | Why it blocks submission |
|---|---|---|---|

## Redaction And Sharing Notes
[NDA/channel/attachment restrictions and anything that must not go into the worksheet]
```

## Examples And Acceptance Checks

Positive customer questionnaire example: "Use $security-questionnaire-triage on this 120-row customer security spreadsheet. We have a SOC 2 report, encryption architecture note, and prior answer bank." The skill should run the local triage script, group questions by control domain, draft only answers backed by approved evidence, and route legal/privacy questions.

Positive RFP example: "The sales team needs the security section answered by Friday. We have old answers but no evidence register." The skill should create a triage table, mark old answers as unverified, request evidence by owner, and block unsupported yes/no claims.

Negative example: "Is Vendor X safe enough for us to buy?" Do not trigger this skill; that is buyer-side vendor risk assessment, not seller-side questionnaire response.

Boundary example: "I only have pasted questions and no approved evidence." The skill should classify domains and reviewers, but it must not produce final yes/no answers.

## Validation

Smoke-test the bundled fixture:

```bash
python3 security-questionnaire-triage/scripts/security_questionnaire_triage.py security-questionnaire-triage/scripts/fixtures/security_questions.csv --evidence-register security-questionnaire-triage/scripts/fixtures/evidence_register.csv --answer-bank security-questionnaire-triage/scripts/fixtures/answer_bank.csv
```

Expected result: a Markdown report that marks MFA and encryption as ready with cited answers, treats the SOC 2 report as shareable only through the approved NDA/trust channel, routes AI claims for controlled review, blocks production IP details from being answered in the worksheet, and flags unsupported or stale claims instead of inventing compliance language.
