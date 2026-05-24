# UTM Risk Rules

## Required Parameters

Every launch link should include:

- `utm_source`: canonical platform, publisher, partner, or list source.
- `utm_medium`: canonical channel or intent bucket.
- `utm_campaign`: structured launch, offer, or program identifier.

`utm_content` and `utm_term` are optional and should have one job each: creative/test variant and paid-search keyword/audience.

## Block Findings

- Missing or blank required UTM.
- `utm_source` contains a medium value while `utm_medium` contains a source value.
- Public UTM values leak sensitive internal labels, competitor attack names, employee-pressure language, private strategy, or unreleased confidential wording.
- A launch-critical link cannot be mapped to a reportable source and medium before launch.

## Review Findings

- Source or medium alias should be converted to canonical value.
- Mixed case would create case-sensitive reporting splits.
- Spaces or free text should be replaced with lowercase hyphenated slugs.
- Campaign name does not match the approved slot format.
- Unknown source or medium may be legitimate but needs a deliberate policy update.

## Guardrails

- Do not rewrite historical reporting values without a mapping table and cutoff date.
- Do not claim causal attribution from clean UTMs alone.
- Keep policy enforcement near link creation, not only in a wiki.
- Preserve partner and agency owner context so fixes can be routed before launch.
