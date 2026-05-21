# Sample Three-Way Match Report

## Three-Way Match Decision
Hold affected invoices

Reviewed invoice lines: 6
Exceptions: 5 (3 high, 2 medium)

## Exceptions
| Risk | Action | Invoice | PO | Vendor | Amount | Flags | Owner | Reviewer next step |
|---|---|---|---|---|---:|---|---|---|
| high | hold_invoice | row 3 `INV-7802` | `PO-7002` | Metro Components | USD 432.00 | quantity_exceeds_po, invoice_quantity_exceeds_received, approved_with_unresolved_exception | receiving | Pause payment approval until the exception owner records a disposition. |
| high | hold_invoice | row 5 `INV-7804` | `PO-7004` | Acme Industrial | USD 320.00 | vendor_mismatch, approved_with_unresolved_exception | procurement | Pause payment approval until the exception owner records a disposition. |
| high | hold_invoice | row 7 `INV-7806` | `PO-7006` | West Plant Maintenance | USD 540.00 | closed_or_cancelled_po, missing_receipt, approved_with_unresolved_exception | receiving | Pause payment approval until the exception owner records a disposition. |
| medium | route_exception | row 4 `INV-7803` | `PO-7003` | Eastline Freight | USD 225.00 | unit_price_variance, line_amount_variance | AP | Recalculate line amount, tax, freight, and invoice math before approval. |
| medium | route_exception | row 6 `INV-7805` | `missing` | OfficePro | USD 120.00 | missing_po_number | requester_or_procurement | Find the requester, PO, contract, or retroactive approval before coding the invoice. |

## Safe Release Gate
Do not release high-risk invoice lines until AP records the exception owner, evidence, and disposition.
