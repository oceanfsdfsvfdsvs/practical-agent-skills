## UTM Governance Decision
Block launch

## Summary
- Links reviewed: 6
- Block findings: 4
- Review findings: 8

## Findings
| Severity | Risk | Row | Link | Owner | Evidence | Next step |
|---|---|---:|---|---|---|---|
| review | mixed_case_utm_value | 3 | launch-paid-1 | Paid Social | utm_campaign=Spring Launch contains uppercase characters | Lowercase UTM values to prevent case-sensitive report fragmentation. |
| review | unsafe_utm_characters | 3 | launch-paid-1 | Paid Social | utm_campaign=Spring Launch contains spaces or surrounding whitespace | Use hyphenated slug values with no spaces. |
| review | unsafe_utm_characters | 3 | launch-paid-1 | Paid Social | utm_content=carousel ad contains spaces or surrounding whitespace | Use hyphenated slug values with no spaces. |
| review | mixed_case_utm_value | 3 | launch-paid-1 | Paid Social | utm_source=Facebook contains uppercase characters | Lowercase UTM values to prevent case-sensitive report fragmentation. |
| review | campaign_format_violation | 3 | launch-paid-1 | Paid Social | utm_campaign=Spring Launch does not match the approved structured pattern | Rebuild campaign name from the approved structured slots. |
| review | alias_to_canonical_source | 4 | launch-paid-2 | Paid Social | utm_source=fb should be facebook | Replace source alias with the canonical source value. |
| block | source_medium_swapped | 5 | launch-bad-1 | Agency | utm_source=cpc looks like a medium while utm_medium=facebook looks like a source | Swap source and medium, then re-check channel grouping. |
| block | sensitive_internal_term | 5 | launch-bad-1 | Agency | utm_content contains internal/sensitive launch language | Rename public UTM values so they do not leak private strategy or pressure. |
| block | missing_required_utm | 7 | launch-missing-1 | Events | utm_medium is missing or blank | Add utm_medium before launch. |

## Launch Gate
- Resolve all `block` findings before links go live.
- Review aliases and unknown values with marketing ops before changing reporting policy.
- Keep canonical source and medium lists near the link creation workflow, not only in a wiki.
