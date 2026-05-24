# UTM Governance Preflight

Catch UTM and campaign-naming drift before launch so marketing, analytics, RevOps, and agency teams do not ship links that fragment GA4, CRM, CDP, warehouse, or BI reporting.

This skill is for campaign URL spreadsheets, ad launch QA, email links, partner links, QR-code links, and agency submissions. It produces a local Markdown launch-gate report without calling ad platforms, analytics APIs, or URL shorteners.

## What It Catches

- Missing `utm_source`, `utm_medium`, or `utm_campaign`.
- Source/medium swaps that break channel grouping.
- Alias drift such as `fb` versus `facebook`.
- Mixed-case and spaced values that create duplicate report buckets.
- Campaign names that do not match the approved structured format.
- Sensitive internal terms accidentally exposed in public URL parameters.

## Quick Start

```bash
python3 utm-governance-preflight/scripts/utm_governance_preflight.py \
  --links utm-governance-preflight/scripts/fixtures/campaign_links.csv \
  --policy utm-governance-preflight/scripts/fixtures/policy.json
```

Preferred link fields:

```text
link_id, owner, channel, url
```

Preferred policy fields:

```text
required_parameters, allowed_sources, source_aliases, allowed_media,
medium_aliases, campaign_pattern, sensitive_terms
```

## Output

The script produces a Markdown report with:

- UTM governance decision.
- Block and review finding counts.
- Row-level fixes for each link.
- Launch gate and owner next steps.

## Runtime Files

- `SKILL.md` - canonical skill instructions.
- `agents/openai.yaml` - Codex/OpenAI-style metadata.
- `.claude/skills/utm-governance-preflight/SKILL.md` - Claude Code mirror in the repository root.
- `openclaw/README.md` and `hermes/README.md` - runtime notes and current verification limits.
- `scripts/fixtures/` - local smoke-test inputs.

## Safety

- This is marketing operations support, not legal, privacy, or causal attribution advice.
- The script does not call network services, mutate live campaigns, create short links, or require credentials.
- Do not paste private unreleased campaign strategy, customer identifiers, or credentials into public prompts or fixtures.
- Treat provisional policies as drafts until the marketing-ops owner approves the canonical taxonomy.
