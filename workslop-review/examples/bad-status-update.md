# Bad Status Update Example

## User Prompt

Use `$workslop-review` on this AI-generated customer update. Is it safe to send?

## Draft

Hi Alex,

Everything is on track and the migration should be completed soon. The team has made great progress on the data cleanup and we are confident the final import will work smoothly. We will keep monitoring and follow up if anything changes.

Best,
Maya

## Source Notes

- 18,240 customer records are ready for test import.
- 412 rows still have duplicate external IDs.
- Billing address normalization is incomplete.
- Customer wants a go/no-go decision by Friday 15:00.
- Priya owns dedupe; Mateo owns billing address cleanup.
- No production import has run yet.

## Expected Review

## Delivery Decision
Repair first

## Score

| Dimension | Score | Reason |
|---|---:|---|
| Context fit | 1 | It addresses the customer but does not answer the go/no-go need. |
| Grounding | 0 | "Everything is on track" and "confident" contradict unresolved blockers. |
| Actionability | 0 | No owners, dates, or decision path. |
| Completeness | 1 | Mentions migration but omits row counts and blockers. |
| Specificity | 0 | Generic status language. |
| Risk control | 0 | Hides duplicate ID and billing cleanup risks. |

## Main Problems

1. The draft claims the migration is on track without evidence and despite known blockers.
2. It does not give the customer the requested go/no-go path.
3. It hides owners and deadlines, so the recipient cannot judge accountability.

## Minimal Repair

Hi Alex,

We are not ready for the production import yet. The test set has 18,240 customer records ready, but two blockers remain: 412 rows have duplicate external IDs, and billing address normalization is still incomplete.

Priya owns the duplicate-ID cleanup and Mateo owns billing address normalization. We will send a go/no-go recommendation by Friday 15:00 after those checks complete and the test import report is reviewed.

Best,
Maya
