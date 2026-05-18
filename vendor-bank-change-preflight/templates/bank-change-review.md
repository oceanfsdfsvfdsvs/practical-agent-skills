# Vendor Bank Change Review

## Bank Change Decision

[Hold bank-change updates / Secondary verification required / No high-risk signal found]

## Request Findings

| Risk | Action | Row | Request | Vendor | Amount at risk | Flags | Reviewer next step |
|---|---|---:|---|---|---:|---|---|
|  |  |  |  |  |  |  |  |

## Controls Checked

- Independent callback source:
- Callback completion:
- Dual approval:
- Trusted domain comparison:
- Bank country comparison:
- Reused bank details:
- New vendor / first payment:
- Evidence packet:

## Safe Release Steps

1. Hold `hold_change` rows until trusted-source callback and second approval are complete.
2. Confirm `secondary_verification` rows with procurement, AP owner, or relationship owner.
3. Archive callback source, reviewer names, and evidence with the vendor record.
4. Rerun preflight after corrections and before releasing payment.

## Open Questions

- 
