# Three-Way Match Rules

## Decision Boundary

This skill produces operational review evidence. It does not approve, post, cancel, or pay invoices in a live accounting system.

## High-Risk Exceptions

Use `hold_invoice` when any of these are present:

- `po_not_found`: invoice cites a PO that is absent from the provided PO export.
- `closed_or_cancelled_po`: PO is closed, cancelled, void, or otherwise unavailable for new invoices.
- `vendor_mismatch`: invoice vendor ID and PO vendor ID differ.
- `invoice_quantity_exceeds_received`: invoice quantity is greater than received quantity net of rejected goods.
- `approved_with_unresolved_exception`: invoice is already approved, ready, or scheduled while unresolved match exceptions remain.

High-risk rows need a named owner, evidence, and disposition before payment release.

## Medium-Risk Exceptions

Use `route_exception` when any of these are present:

- `missing_po_number`: invoice has no PO reference.
- `po_not_approved`: PO exists but is not approved/open/released.
- `quantity_exceeds_po`: invoice quantity exceeds the ordered quantity.
- `unit_price_variance`: invoice unit price exceeds PO unit price above tolerance.
- `line_amount_variance`: invoice line amount exceeds expected quantity times PO price above tolerance.
- `missing_receipt`: no receipt is available for the matched PO line or SKU.
- `currency_mismatch`: invoice and PO currencies differ.

Medium-risk rows may be payable later, but only after AP routes the exception to the correct owner.

## Low-Risk Exceptions

Use `review_note` for weak or policy-dependent signals such as negative tax/shipping, ambiguous SKU mapping, or metadata that needs a reviewer note but does not itself block payment under local policy.

## Owner Mapping

| Flag | Default Owner | Evidence Needed |
|---|---|---|
| `missing_po_number` | requester_or_procurement | requester, contract, budget approval, retroactive PO or exception approval |
| `po_not_found` | procurement | valid PO, corrected invoice, or documented no-PO approval |
| `closed_or_cancelled_po` | procurement | reopened PO, replacement PO, or documented exception |
| `vendor_mismatch` | procurement | corrected vendor, vendor master explanation, or corrected PO |
| `quantity_exceeds_po` | procurement | approved change order or corrected invoice |
| `unit_price_variance` | procurement | agreed price change, contract clause, or corrected invoice |
| `line_amount_variance` | AP | recalculation, tax/freight split, or corrected invoice |
| `missing_receipt` | receiving | goods receipt, service acceptance, or policy approval |
| `invoice_quantity_exceeds_received` | receiving | partial receipt disposition, backorder status, or corrected invoice |
| `approved_with_unresolved_exception` | AP | approval pause and exception disposition |

## Failure Modes To Prevent

- Treating OCR extraction as the whole invoice-processing problem.
- Paying against a closed or cancelled PO because the invoice amount looks normal.
- Paying the full invoice when only part of the PO was received.
- Letting an invoice stay approved after a match exception is discovered.
- Routing every exception to AP even when procurement or receiving owns the missing evidence.
