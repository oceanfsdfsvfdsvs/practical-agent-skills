# Sample AP Duplicate Payment Report

## Payment Run Decision

Hold payment run: high-risk duplicate-payment exceptions exist.

## Duplicate Exceptions

| Risk | Action | Rows | Vendor | Invoice | Amount | Evidence | Reviewer next step |
|---|---|---|---|---|---:|---|---|
| high | hold_payment | 2, 3 | Acme Services LLC / Acme Services | INV-1007 / INV1007 | USD 1250.00 | normalized_invoice_match, same_vendor_id, same_amount, close_dates, same_po | Hold one row and confirm the intended invoice record. |
| high | hold_payment | 6, 7 | Cedar Labs | CL-77 / CL77 | USD 430.00 | paid_vs_pending_collision, normalized_invoice_match, same_vendor_id, same_amount | Remove pending row unless AP confirms a corrected rebill. |
| medium | ap_review | 4, 5 | Blue Harbor Consulting / Blue Harbour LLC | BH-220 / BH220 | USD 980.00 | vendor_alias_match, normalized_invoice_match, same_amount, same_po | Confirm whether duplicate vendor masters exist. |

## Controls Checked

Exact invoice match, normalized invoice match, vendor alias, same amount/date window, paid-versus-pending collision, and PO collision.
