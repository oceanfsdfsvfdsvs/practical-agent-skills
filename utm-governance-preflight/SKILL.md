---
name: utm-governance-preflight
description: Use when marketing, growth, RevOps, agency, analytics, or data teams need to review campaign URLs, UTM parameters, campaign naming, source/medium values, or attribution hygiene before launch, dashboard refresh, handoff, or agency approval.
---

# UTM Governance Preflight

## Overview

Use this skill to catch UTM and campaign-naming drift before campaign links go live or before dirty attribution data reaches GA4, CRM, CDP, warehouse, or BI reports. The goal is to enforce a small canonical taxonomy and produce owner-ready fixes, not to invent a new attribution model.

## Use And Do Not Use

Use for:

- Campaign URL spreadsheets, ad-launch checklists, email links, QR-code links, partner links, agency submissions, or historical UTM exports.
- Finding missing required UTMs, source/medium swaps, aliases, mixed case, spaces, sensitive public labels, and campaign-name format violations.
- Turning a naming standard into a repeatable launch gate and cleanup report.
- Producing canonical source/medium/campaign fixes before a launch or reporting freeze.

Do not use for:

- Claiming exact multi-touch attribution or incrementality.
- Changing live ad platform, email, CRM, or analytics settings without explicit authorization.
- Sending private campaign data to third-party services.
- Legal, privacy, or brand approval advice.
- Replacing a full marketing data warehouse governance program when live integrations, approvals, lineage, and audit trails are required.

## Required Inputs

Ask only for missing inputs that materially change the decision:

- Campaign link export path or pasted table with `url` or `link`; useful optional fields are `link_id`, `owner`, and `channel`.
- UTM policy JSON, naming convention document, or source/medium/campaign rules. If absent, use the bundled reference rules as a starting point and mark policy assumptions.
- Launch deadline or reporting freeze date, if relevant.
- Canonical source and medium lists, especially when agencies or multiple teams create links.
- Terms that must never appear in public UTMs, such as internal strategy, competitor attack labels, employee-pressure wording, or sensitive promo codes.

## Workflow

### 1. Preserve Scope And Evidence

Record:

- Whether the review is pre-launch, historical cleanup, agency approval, or handoff.
- Which systems consume the UTMs: GA4, CRM, CDP, ad platform, warehouse, BI, or spreadsheet.
- Whether the policy is authoritative, inherited, or inferred.
- Whether old values must be mapped for reporting continuity instead of renamed.

Read `references/utm-risk-rules.md` before classifying source/medium aliases, campaign format drift, and sensitive terms.

### 2. Run The Local Audit When Files Exist

Use explicit relative or absolute paths:

```bash
python3 utm-governance-preflight/scripts/utm_governance_preflight.py \
  --links /absolute/path/campaign_links.csv \
  --policy /absolute/path/policy.json
```

CSV and JSON inputs are supported. Preferred fields:

```text
links: link_id, owner, channel, url
policy: required_parameters, allowed_sources, source_aliases, allowed_media,
        medium_aliases, campaign_pattern, sensitive_terms
```

### 3. Classify Launch Risk

Use one primary decision:

- `Block launch`: required UTM missing, source/medium swapped, public UTM leaks sensitive/internal wording, or a launch-critical channel cannot be mapped.
- `Fix before launch`: aliases, mixed case, unsafe spaces, unknown values, or campaign format drift need owner correction but do not prove attribution will be unrecoverable.
- `Pass`: links meet the policy and no material governance finding appears.

Do not silently normalize values without showing the owner which public link or report bucket changes.

### 4. Produce The Governance Report

Return:

```markdown
## UTM Governance Decision
[Block launch / Fix before launch / Pass]

## Summary
[Links reviewed, block findings, review findings, source/medium health]

## Findings
| Severity | Risk | Row | Link | Owner | Evidence | Next step |
|---|---|---:|---|---|---|---|

## Launch Gate
[Owner-specific fixes and policy updates]
```

Use `templates/launch-gate-report.md` when the user asks for a reusable artifact.

## Examples And Acceptance Checks

Positive example: "Use $utm-governance-preflight on this agency link spreadsheet before next week's paid social launch." The skill should flag missing UTMs, source aliases, source/medium swaps, mixed case, unsafe values, sensitive terms, and campaign format drift.

Positive cleanup example: "Audit these GA4 source/medium rows and tell me what policy changes we need." The skill should distinguish historical mapping from pre-launch link changes and avoid claiming exact attribution recovery.

Negative example: "Tell me which campaign truly caused the revenue." Do not claim causal attribution; ask for experiment/incrementality context and scope this skill to UTM hygiene.

Boundary example: "We have no policy." Use the reference policy as a draft, label it as provisional, and recommend marketing-ops approval before enforcement.

## Validation

Smoke-test the bundled fixture:

```bash
python3 utm-governance-preflight/scripts/utm_governance_preflight.py \
  --links utm-governance-preflight/scripts/fixtures/campaign_links.csv \
  --policy utm-governance-preflight/scripts/fixtures/policy.json
```

Expected result: exit code `2` and a Markdown report with `UTM Governance Decision`, `Block launch`, `missing_required_utm`, `source_medium_swapped`, `sensitive_internal_term`, and `alias_to_canonical_source`.
