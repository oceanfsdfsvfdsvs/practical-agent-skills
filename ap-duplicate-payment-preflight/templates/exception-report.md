# AP Duplicate Payment Exception Report

## Payment Run Decision

[Hold payment run / Release after AP review / No material duplicate risk found]

## Duplicate Exceptions

| Risk | Action | Rows | Vendor | Invoice | Amount | Evidence | Reviewer next step |
|---|---|---|---|---|---:|---|---|
| [high/medium/low] | [hold_payment/ap_review/allow_with_note] | [row ids] | [vendor] | [invoice] | [amount] | [matched controls] | [specific next step] |

## Controls Checked

- Exact invoice and amount match.
- Normalized invoice-number match.
- Vendor alias match.
- Same amount within review date window.
- Paid-versus-pending collision.
- Purchase-order collision.

## Safe Release Steps

1. Hold high-risk rows from the payment run.
2. Assign AP owner review for medium-risk rows.
3. Record dispositions for recurring, credit, reversal, void, or corrected-bill exceptions.
4. Re-export the final payment run and archive this report with the approval package.

## Open Questions

- [Only questions that affect payment release safety.]
