---
name: utm-governance-preflight
description: Use when marketing, growth, RevOps, agency, analytics, or data teams need to review campaign URLs, UTM parameters, campaign naming, source/medium values, or attribution hygiene before launch, dashboard refresh, handoff, or agency approval.
---

# UTM Governance Preflight

## Overview

Use this skill to catch UTM and campaign-naming drift before campaign links go live or before dirty attribution data reaches GA4, CRM, CDP, warehouse, or BI reports. The goal is to enforce a small canonical taxonomy and produce owner-ready fixes, not to invent a new attribution model.

## Use And Do Not Use

Use for campaign URL spreadsheets, ad-launch checklists, email links, QR-code links, partner links, agency submissions, or historical UTM exports.

Do not use for exact multi-touch attribution, legal/privacy advice, live campaign mutations without authorization, or sending private campaign data to third-party services.

## Required Inputs

- Campaign link export path or pasted table with `url` or `link`; useful optional fields are `link_id`, `owner`, and `channel`.
- UTM policy JSON, naming convention document, or source/medium/campaign rules.
- Launch deadline or reporting freeze date, if relevant.
- Canonical source and medium lists, especially when agencies or multiple teams create links.
- Terms that must never appear in public UTMs.

## Workflow

1. Record whether this is pre-launch, historical cleanup, agency approval, or handoff.
2. Read `references/utm-risk-rules.md` before classifying findings.
3. Run the local audit when files exist:

```bash
python3 utm-governance-preflight/scripts/utm_governance_preflight.py \
  --links /absolute/path/campaign_links.csv \
  --policy /absolute/path/policy.json
```

4. Classify the decision as `Block launch`, `Fix before launch`, or `Pass`.
5. Return a Markdown report with summary, row-level findings, owner next steps, and launch gate.

## Validation

```bash
python3 utm-governance-preflight/scripts/utm_governance_preflight.py \
  --links utm-governance-preflight/scripts/fixtures/campaign_links.csv \
  --policy utm-governance-preflight/scripts/fixtures/policy.json
```

Expected result: exit code `2` with `UTM Governance Decision`, `Block launch`, `missing_required_utm`, `source_medium_swapped`, `sensitive_internal_term`, and `alias_to_canonical_source`.
