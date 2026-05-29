---
name: dsar-request-preflight
description: Triage data subject access, deletion, correction, and portability requests against identity, authority, deadline, system-inventory, export, deletion-exception, and owner-routing checks before a privacy team fulfills or responds.
---

# DSAR Request Preflight

## Overview

Use this skill when a privacy, legal ops, support ops, security, or startup operations team needs to turn messy privacy-rights intake into a defensible fulfillment plan. It is designed for data subject access requests, deletion/erasure requests, correction requests, portability requests, and similar consumer privacy requests.

The goal is to prevent late responses, unsafe disclosures, unsupported deletions, missed systems, weak identity checks, and vague owner handoffs. This is privacy-operations workflow support, not legal advice.

## Use And Do Not Use

Use for:

- DSAR, DSR, GDPR access/erasure, CCPA/CPRA access/delete/correct, portability, and account-data export requests.
- Intake spreadsheets, ticket exports, privacy portal exports, or typed request tables.
- System inventory review before export, deletion, exception, or owner assignment.
- Producing a response-readiness report, owner task list, and exception checklist.

Do not use for:

- Legal conclusions about whether a request must be honored.
- Drafting binding privacy notices, regulator responses, or litigation strategy.
- Bypassing identity verification, authorization, retention, legal-hold, or security review.
- Uploading raw secrets, credentials, access tokens, full payment data, SSNs, or unrelated personal data.
- Performing live deletion, export, portal action, or customer communication without explicit user authorization.

## Required Inputs

Ask only for missing inputs that materially change the result:

- Request intake CSV/JSON. Preferred fields: `request_id`, `received_date`, `requester`, `jurisdiction`, `request_type`, `identity_status`, `authorized_agent`, `agent_proof`, `scope`, `match_keys`, `sensitive_context`, `notes`.
- System inventory CSV/JSON. Preferred fields: `system`, `owner`, `data_categories`, `match_keys`, `export_supported`, `deletion_supported`, `retention_lock`, `legal_hold`, `processor`.
- Optional policy JSON with SLA days, due-soon threshold, sensitive terms, and deletion-exception terms.
- Review date when deadlines matter.

If the user has only emails or tickets, first convert them to a small intake table. Do not infer identity or authorization status from tone.

## Workflow

### 1. Preserve Privacy And Authority Boundaries

Before analysis:

- Ask the user to redact secrets, credentials, full payment data, SSNs, and unrelated personal data.
- Keep final legal interpretation, exception approval, response language, disclosure, and deletion authorization with the responsible privacy/legal owner.
- Confirm whether the request is access, deletion/erasure, correction, portability, opt-out, or unclear.

Read `references/dsar-preflight-rules.md` before classifying a request as ready.

### 2. Run The Local Preflight

Use explicit paths:

```bash
python3 dsar-request-preflight/scripts/dsar_request_preflight.py \
  --requests /absolute/path/requests.csv \
  --systems /absolute/path/systems.csv \
  --policy /absolute/path/policy.json \
  --today 2026-05-30
```

The script accepts CSV or JSON. JSON may be a list or an object containing `requests`, `dsars`, `systems`, `inventory`, or `rows`.

### 3. Classify Fulfillment Risks

Use one primary action per finding:

- `verify_identity`: identity status is missing, pending, or not approved.
- `verify_agent_authority`: authorized agent proof is missing or incomplete.
- `accelerate_fulfillment`: statutory or internal deadline is due soon.
- `escalate_privacy_owner`: response deadline appears overdue.
- `map_system_scope`: requested scope does not match inventory.
- `route_owner_tasks`: multiple owners must export, delete, or approve exceptions.
- `manual_export_review`: access/export request touches systems without export support.
- `deletion_exception_review`: deletion request touches legal hold, retention lock, unsupported deletion, or exception context.
- `sensitive_data_review`: request mentions child, health, financial, biometric, location, or other sensitive context.

Never say that a company is legally compliant or noncompliant. Say which operational checks are complete, blocked, or need owner approval.

### 4. Produce The DSAR Preflight Report

Return:

```markdown
## DSAR Request Decision
[Hold fulfillment pending repair / Review before response / Ready for controlled fulfillment]

## Request Summary
[Requests reviewed, systems reviewed, blocker count, critical/high count]

## Action Summary
[Action counts and top routing needs]

## Request Findings
| Risk | Action | Row | Request | Type | Flag | Evidence | Next step |
|---|---|---:|---|---|---|---|---|

## Owner Routing
[Request-to-owner map]

## Guardrails
[Privacy, authority, legal boundary, no live deletion/export caveat]
```

Use `templates/response-readiness-report.md` when the user wants a reusable packet for a privacy owner.

## Examples And Acceptance Checks

Positive example: "Use dsar-request-preflight on this privacy portal export and data inventory before we respond to deletion requests." The skill should check deadlines, identity, authorized-agent proof, deletion support, retention or legal-hold exceptions, system coverage, and owner routing.

Positive startup example: "We have five GDPR/CPRA requests in a spreadsheet and a rough SaaS system list." The skill should turn the rough system list into a scoped owner plan and call out no-inventory gaps rather than claiming completion.

Negative example: "Tell me whether we can deny this DSAR." Do not provide legal advice; classify operational blockers and route exception approval.

Boundary example: "Delete this user's data in all systems." Do not perform live deletion; prepare a fulfillment checklist and require explicit owner authorization.

## Validation

Smoke-test the bundled fixture:

```bash
python3 dsar-request-preflight/scripts/dsar_request_preflight.py \
  --requests dsar-request-preflight/scripts/fixtures/requests.csv \
  --systems dsar-request-preflight/scripts/fixtures/systems.csv \
  --policy dsar-request-preflight/scripts/fixtures/policy.json \
  --today 2026-05-30
```

Expected result: exit code `2` with `DSAR Request Decision`, `Hold fulfillment pending repair`, `response_deadline_overdue`, `identity_verification_missing`, `authorized_agent_proof_missing`, `deletion_blocked_or_exception_needed`, `access_export_not_supported`, `sensitive_or_minor_data_context`, and `missing_received_date`.
