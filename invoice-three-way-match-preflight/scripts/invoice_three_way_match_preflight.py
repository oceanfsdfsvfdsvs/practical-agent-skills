#!/usr/bin/env python3
"""Preflight invoice lines against purchase orders and receipts."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path


APPROVED_PO_STATUSES = {"approved", "open", "partially_received", "received", "released"}
CLOSED_PO_STATUSES = {"closed", "cancelled", "canceled", "void"}


@dataclass(frozen=True)
class InvoiceLine:
    row_number: int
    invoice_number: str
    vendor_id: str
    vendor_name: str
    po_number: str
    line_id: str
    item_sku: str
    description: str
    quantity: Decimal
    unit_price: Decimal
    line_amount: Decimal
    currency: str
    invoice_date: str
    approval_status: str
    tax_amount: Decimal
    shipping_amount: Decimal
    memo: str


@dataclass(frozen=True)
class PurchaseOrderLine:
    row_number: int
    po_number: str
    vendor_id: str
    vendor_name: str
    line_id: str
    item_sku: str
    description: str
    ordered_quantity: Decimal
    unit_price: Decimal
    line_amount: Decimal
    currency: str
    status: str
    approved: bool


@dataclass(frozen=True)
class ReceiptLine:
    row_number: int
    po_number: str
    line_id: str
    item_sku: str
    received_quantity: Decimal
    rejected_quantity: Decimal
    receipt_date: str
    status: str


@dataclass(frozen=True)
class Finding:
    risk: str
    action: str
    invoice: InvoiceLine
    flags: tuple[str, ...]
    owner: str
    reviewer_step: str


def parse_decimal(value: object) -> Decimal:
    raw = str(value or "").strip().replace(",", "").replace("$", "")
    if raw.startswith("(") and raw.endswith(")"):
        raw = f"-{raw[1:-1]}"
    try:
        return Decimal(raw or "0")
    except InvalidOperation:
        return Decimal("0")


def parse_bool(value: object) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "approved", "open", "released"}


def key(value: object) -> str:
    return str(value or "").strip()


def lower_key(row: dict[str, object]) -> dict[str, object]:
    return {str(name).strip().lower(): value for name, value in row.items()}


def load_records(path: Path, top_level_keys: tuple[str, ...]) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"Input file not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            for top_key in top_level_keys:
                if isinstance(payload.get(top_key), list):
                    return [dict(row) for row in payload[top_key]]
            raise SystemExit(f"JSON input must contain one of: {', '.join(top_level_keys)}.")
        if isinstance(payload, list):
            return [dict(row) for row in payload]
        raise SystemExit("JSON input must be a list or an object containing rows.")
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def read_invoices(path: Path) -> list[InvoiceLine]:
    rows = load_records(path, ("invoices", "invoice_lines", "rows"))
    parsed: list[InvoiceLine] = []
    for offset, raw in enumerate(rows, start=2):
        row = lower_key(raw)
        quantity = parse_decimal(row.get("quantity") or row.get("qty"))
        unit_price = parse_decimal(row.get("unit_price") or row.get("price"))
        amount = parse_decimal(row.get("line_amount") or row.get("amount"))
        if amount == 0 and quantity and unit_price:
            amount = quantity * unit_price
        parsed.append(
            InvoiceLine(
                row_number=offset,
                invoice_number=key(row.get("invoice_number") or row.get("invoice")),
                vendor_id=key(row.get("vendor_id") or row.get("supplier_id")),
                vendor_name=key(row.get("vendor_name") or row.get("vendor") or row.get("supplier")),
                po_number=key(row.get("po_number") or row.get("po")),
                line_id=key(row.get("line_id") or row.get("po_line_id") or row.get("line")),
                item_sku=key(row.get("item_sku") or row.get("sku") or row.get("item")),
                description=key(row.get("description") or row.get("memo")),
                quantity=quantity,
                unit_price=unit_price,
                line_amount=amount,
                currency=key(row.get("currency")).upper() or "USD",
                invoice_date=key(row.get("invoice_date") or row.get("date")),
                approval_status=key(row.get("approval_status") or row.get("status")).lower(),
                tax_amount=parse_decimal(row.get("tax_amount") or row.get("tax")),
                shipping_amount=parse_decimal(row.get("shipping_amount") or row.get("shipping")),
                memo=key(row.get("memo") or row.get("notes")),
            )
        )
    if not parsed:
        raise SystemExit("No invoice rows found.")
    return parsed


def read_purchase_orders(path: Path) -> list[PurchaseOrderLine]:
    rows = load_records(path, ("purchase_orders", "po_lines", "rows"))
    parsed: list[PurchaseOrderLine] = []
    for offset, raw in enumerate(rows, start=2):
        row = lower_key(raw)
        quantity = parse_decimal(row.get("ordered_quantity") or row.get("quantity") or row.get("qty"))
        unit_price = parse_decimal(row.get("unit_price") or row.get("price"))
        amount = parse_decimal(row.get("line_amount") or row.get("amount"))
        if amount == 0 and quantity and unit_price:
            amount = quantity * unit_price
        parsed.append(
            PurchaseOrderLine(
                row_number=offset,
                po_number=key(row.get("po_number") or row.get("po")),
                vendor_id=key(row.get("vendor_id") or row.get("supplier_id")),
                vendor_name=key(row.get("vendor_name") or row.get("vendor") or row.get("supplier")),
                line_id=key(row.get("line_id") or row.get("po_line_id") or row.get("line")),
                item_sku=key(row.get("item_sku") or row.get("sku") or row.get("item")),
                description=key(row.get("description") or row.get("memo")),
                ordered_quantity=quantity,
                unit_price=unit_price,
                line_amount=amount,
                currency=key(row.get("currency")).upper() or "USD",
                status=key(row.get("status")).lower(),
                approved=parse_bool(row.get("approved") or row.get("status")),
            )
        )
    if not parsed:
        raise SystemExit("No purchase-order rows found.")
    return parsed


def read_receipts(path: Path) -> list[ReceiptLine]:
    rows = load_records(path, ("receipts", "receipt_lines", "rows"))
    parsed: list[ReceiptLine] = []
    for offset, raw in enumerate(rows, start=2):
        row = lower_key(raw)
        parsed.append(
            ReceiptLine(
                row_number=offset,
                po_number=key(row.get("po_number") or row.get("po")),
                line_id=key(row.get("line_id") or row.get("po_line_id") or row.get("line")),
                item_sku=key(row.get("item_sku") or row.get("sku") or row.get("item")),
                received_quantity=parse_decimal(row.get("received_quantity") or row.get("quantity") or row.get("qty")),
                rejected_quantity=parse_decimal(row.get("rejected_quantity") or row.get("rejected") or 0),
                receipt_date=key(row.get("receipt_date") or row.get("date")),
                status=key(row.get("status")).lower(),
            )
        )
    return parsed


def match_key(po_number: str, line_id: str, item_sku: str) -> tuple[str, str, str]:
    return (po_number.strip().lower(), line_id.strip().lower(), item_sku.strip().lower())


def build_po_index(rows: list[PurchaseOrderLine]) -> dict[tuple[str, str, str], PurchaseOrderLine]:
    indexed: dict[tuple[str, str, str], PurchaseOrderLine] = {}
    for row in rows:
        indexed[match_key(row.po_number, row.line_id, row.item_sku)] = row
        if row.line_id:
            indexed.setdefault(match_key(row.po_number, row.line_id, ""), row)
        if row.item_sku:
            indexed.setdefault(match_key(row.po_number, "", row.item_sku), row)
    return indexed


def build_receipt_totals(rows: list[ReceiptLine]) -> dict[tuple[str, str, str], Decimal]:
    totals: dict[tuple[str, str, str], Decimal] = {}
    for row in rows:
        received = row.received_quantity - row.rejected_quantity
        keys = [
            match_key(row.po_number, row.line_id, row.item_sku),
            match_key(row.po_number, row.line_id, ""),
            match_key(row.po_number, "", row.item_sku),
        ]
        for item_key in keys:
            totals[item_key] = totals.get(item_key, Decimal("0")) + received
    return totals


def find_po(invoice: InvoiceLine, index: dict[tuple[str, str, str], PurchaseOrderLine]) -> PurchaseOrderLine | None:
    for item_key in (
        match_key(invoice.po_number, invoice.line_id, invoice.item_sku),
        match_key(invoice.po_number, invoice.line_id, ""),
        match_key(invoice.po_number, "", invoice.item_sku),
    ):
        if item_key in index:
            return index[item_key]
    return None


def receipt_quantity(invoice: InvoiceLine, totals: dict[tuple[str, str, str], Decimal]) -> Decimal:
    for item_key in (
        match_key(invoice.po_number, invoice.line_id, invoice.item_sku),
        match_key(invoice.po_number, invoice.line_id, ""),
        match_key(invoice.po_number, "", invoice.item_sku),
    ):
        if item_key in totals:
            return totals[item_key]
    return Decimal("0")


def classify(
    invoices: list[InvoiceLine],
    purchase_orders: list[PurchaseOrderLine],
    receipts: list[ReceiptLine],
    amount_tolerance: Decimal,
    percent_tolerance: Decimal,
) -> list[Finding]:
    po_index = build_po_index(purchase_orders)
    receipt_totals = build_receipt_totals(receipts)
    findings: list[Finding] = []

    for invoice in invoices:
        flags: list[str] = []
        owner = "AP"
        step = "Review invoice metadata before payment."
        po = find_po(invoice, po_index)
        received = receipt_quantity(invoice, receipt_totals)

        if not invoice.po_number:
            flags.append("missing_po_number")
            owner = "requester_or_procurement"
            step = "Find the requester, PO, contract, or retroactive approval before coding the invoice."
        elif po is None:
            flags.append("po_not_found")
            owner = "procurement"
            step = "Confirm the PO exists, is approved, and is available to AP before payment."
        else:
            if po.status in CLOSED_PO_STATUSES:
                flags.append("closed_or_cancelled_po")
                owner = "procurement"
                step = "Reopen/correct the PO or obtain documented exception approval."
            elif not po.approved or po.status not in APPROVED_PO_STATUSES:
                flags.append("po_not_approved")
                owner = "procurement"
                step = "Obtain PO approval or documented exception approval."
            if invoice.vendor_id and po.vendor_id and invoice.vendor_id != po.vendor_id:
                flags.append("vendor_mismatch")
                owner = "procurement"
                step = "Confirm supplier identity and correct either the invoice or PO vendor."
            if invoice.currency != po.currency:
                flags.append("currency_mismatch")
                owner = "AP"
                step = "Confirm currency before coding or payment."

            quantity_delta = invoice.quantity - po.ordered_quantity
            if quantity_delta > 0:
                flags.append("quantity_exceeds_po")
                owner = "procurement"
                step = "Confirm approved change order or corrected invoice quantity."

            unit_delta = invoice.unit_price - po.unit_price
            percent_delta = Decimal("0")
            if po.unit_price:
                percent_delta = abs(unit_delta / po.unit_price)
            if unit_delta > amount_tolerance and percent_delta > percent_tolerance:
                flags.append("unit_price_variance")
                owner = "procurement"
                step = "Confirm agreed price change or request a corrected invoice."

            expected_amount = invoice.quantity * po.unit_price
            if invoice.line_amount - expected_amount > amount_tolerance:
                flags.append("line_amount_variance")
                owner = "AP"
                step = "Recalculate line amount, tax, freight, and invoice math before approval."

            if received <= 0:
                flags.append("missing_receipt")
                owner = "receiving"
                step = "Confirm goods/services receipt before payment release."
            elif invoice.quantity > received:
                flags.append("invoice_quantity_exceeds_received")
                owner = "receiving"
                step = "Confirm partial receipt, backorder, or corrected invoice quantity."

        if invoice.approval_status in {"approved", "ready", "scheduled"} and flags:
            flags.append("approved_with_unresolved_exception")
            step = "Pause payment approval until the exception owner records a disposition."
        if invoice.tax_amount < 0 or invoice.shipping_amount < 0:
            flags.append("negative_tax_or_shipping")

        if not flags:
            continue

        high_flags = {
            "po_not_found",
            "closed_or_cancelled_po",
            "vendor_mismatch",
            "invoice_quantity_exceeds_received",
            "approved_with_unresolved_exception",
        }
        medium_flags = {
            "missing_po_number",
            "po_not_approved",
            "quantity_exceeds_po",
            "unit_price_variance",
            "line_amount_variance",
            "missing_receipt",
            "currency_mismatch",
        }
        if any(flag in high_flags for flag in flags):
            risk = "high"
            action = "hold_invoice"
        elif any(flag in medium_flags for flag in flags):
            risk = "medium"
            action = "route_exception"
        else:
            risk = "low"
            action = "review_note"

        findings.append(Finding(risk, action, invoice, tuple(flags), owner, step))

    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(findings, key=lambda item: (order[item.risk], item.invoice.invoice_number, item.invoice.row_number))


def money(value: Decimal, currency: str) -> str:
    return f"{currency} {value.quantize(Decimal('0.01'))}"


def render(findings: list[Finding], invoice_count: int) -> str:
    high = sum(1 for item in findings if item.risk == "high")
    medium = sum(1 for item in findings if item.risk == "medium")
    if high:
        decision = "Hold affected invoices"
    elif medium:
        decision = "Route exceptions before payment"
    else:
        decision = "No material three-way match exceptions found"

    lines = [
        "## Three-Way Match Decision",
        decision,
        "",
        f"Reviewed invoice lines: {invoice_count}",
        f"Exceptions: {len(findings)} ({high} high, {medium} medium)",
        "",
        "## Exceptions",
        "| Risk | Action | Invoice | PO | Vendor | Amount | Flags | Owner | Reviewer next step |",
        "|---|---|---|---|---|---:|---|---|---|",
    ]
    if not findings:
        lines.append("| low | no_exception | - | - | - | - | no_exception | AP | Archive evidence with payment run. |")
    for item in findings:
        inv = item.invoice
        lines.append(
            "| {risk} | {action} | row {row} `{invoice}` | `{po}` | {vendor} | {amount} | {flags} | {owner} | {step} |".format(
                risk=item.risk,
                action=item.action,
                row=inv.row_number,
                invoice=inv.invoice_number or "missing",
                po=inv.po_number or "missing",
                vendor=inv.vendor_name or inv.vendor_id or "missing",
                amount=money(inv.line_amount, inv.currency),
                flags=", ".join(item.flags),
                owner=item.owner,
                step=item.reviewer_step,
            )
        )
    lines.extend(
        [
            "",
            "## Controls Checked",
            "- PO presence and approved/open status.",
            "- Vendor, currency, quantity, unit price, and line amount variance.",
            "- Receipt coverage net of rejected quantity.",
            "- Already-approved invoices that still carry unresolved match exceptions.",
            "",
            "## Safe Release Gate",
            "Do not release high-risk invoice lines until AP records the exception owner, evidence, and disposition.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preflight invoice lines against purchase orders and receipts.")
    parser.add_argument("--invoices", required=True, type=Path, help="CSV or JSON invoice line export.")
    parser.add_argument("--purchase-orders", required=True, type=Path, help="CSV or JSON purchase-order line export.")
    parser.add_argument("--receipts", required=True, type=Path, help="CSV or JSON receipt line export.")
    parser.add_argument("--amount-tolerance", default="5.00", help="Allowed per-line currency variance.")
    parser.add_argument("--percent-tolerance", default="0.02", help="Allowed unit-price variance ratio, e.g. 0.02.")
    parser.add_argument("--output", type=Path, help="Optional Markdown output path.")
    args = parser.parse_args(argv)

    invoices = read_invoices(args.invoices)
    purchase_orders = read_purchase_orders(args.purchase_orders)
    receipts = read_receipts(args.receipts)
    findings = classify(
        invoices,
        purchase_orders,
        receipts,
        parse_decimal(args.amount_tolerance),
        parse_decimal(args.percent_tolerance),
    )
    report = render(findings, len(invoices))
    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
