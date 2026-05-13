# Duplicate Payment Rules

## High-Risk Holds

Hold payment or remove rows from the run when any condition is true:

- Same vendor ID or strong vendor alias, same normalized invoice number, same amount, and same currency.
- A row marked paid, cleared, processed, or reconciled matches a pending or approved row.
- Invoice numbers differ only by punctuation, spaces, OCR casing, leading zeros, or common prefixes such as `INV`, `BILL`, or `AP`.
- Same purchase order, same vendor, same amount, and close invoice or payment dates.

## AP Review

Route to AP review when:

- Vendor names are similar but vendor IDs differ.
- Invoice numbers are missing on one or both rows.
- Amount and currency match within the date window but invoice numbers differ.
- A memo, PO, or description suggests a rebill, corrected invoice, or partial shipment.
- One row is approved and another is pending, but neither is marked paid.

## Usually Allow With Note

Do not hold automatically when the evidence supports:

- Recurring rent, subscription, payroll, tax, utility, or insurance payments with expected periodicity.
- Credit memo, refund, reversal, void, or corrected-bill rows with negative amount or explicit credit status.
- Split payments where amounts differ and sum to the approved invoice total.
- Separate invoices from the same vendor for the same amount but different PO, service month, or project.

## Normalization Rules

- Vendor names: lowercase, remove punctuation, collapse whitespace, and drop common suffixes such as `inc`, `llc`, `ltd`, `corp`, `company`, `co`, `services`, and `the`.
- Invoice numbers: uppercase, remove punctuation and whitespace, then compare both the full normalized value and digit-only value.
- Amounts: parse as decimal currency values; compare exact amount unless the user explicitly asks for tolerance.
- Dates: compare invoice dates first, then payment dates. Missing dates lower confidence.
- Status: treat paid/pending collisions as higher risk than pending/pending duplicates.

## Failure Modes To Prevent

- Releasing a payment run when exact duplicates are still unresolved.
- Treating vendor alias matches as certain without reviewer confirmation.
- Blocking legitimate recurring charges because they share amount and vendor.
- Missing paid-versus-pending resubmissions because statuses were ignored.
- Ignoring credits, reversals, voids, and corrected invoices.
- Depending on a live ERP connection or private credential to run a local preflight.
