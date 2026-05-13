#!/usr/bin/env python3
"""Find duplicate-payment risk in a local accounts payable export."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable


PAID_STATUSES = {"paid", "cleared", "processed", "reconciled", "settled"}
PENDING_STATUSES = {"pending", "approved", "ready", "scheduled", "open"}
ALLOW_HINTS = ("recurring", "monthly", "utility", "tax", "rent", "subscription", "insurance")
NEGATIVE_HINTS = ("credit", "refund", "reversal", "void", "rebill", "corrected")


@dataclass(frozen=True)
class PaymentRow:
    row_number: int
    vendor_name: str
    vendor_id: str
    invoice_number: str
    invoice_date: str
    payment_date: str
    amount: Decimal
    currency: str
    status: str
    po_number: str
    memo: str


@dataclass(frozen=True)
class ExceptionFinding:
    risk: str
    action: str
    rows: tuple[PaymentRow, PaymentRow]
    evidence: tuple[str, ...]
    reviewer_step: str


def normalized_vendor(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", " ", value.lower())
    stopwords = {"the", "inc", "llc", "ltd", "corp", "corporation", "company", "co", "services", "service"}
    tokens = [token for token in cleaned.split() if token and token not in stopwords]
    return " ".join(tokens)


def normalized_invoice(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", value.upper())


def invoice_digits(value: str) -> str:
    return re.sub(r"[^0-9]+", "", value)


def parse_amount(value: object) -> Decimal:
    raw = str(value or "").strip().replace(",", "").replace("$", "")
    if raw.startswith("(") and raw.endswith(")"):
        raw = f"-{raw[1:-1]}"
    try:
        return Decimal(raw or "0")
    except InvalidOperation:
        return Decimal("0")


def parse_date(value: str) -> datetime | None:
    raw = value.strip()
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def close_dates(a: PaymentRow, b: PaymentRow, window_days: int) -> bool:
    for left in (a.invoice_date, a.payment_date):
        left_date = parse_date(left)
        if left_date is None:
            continue
        for right in (b.invoice_date, b.payment_date):
            right_date = parse_date(right)
            if right_date is not None and abs((left_date - right_date).days) <= window_days:
                return True
    return False


def read_rows(path: Path) -> list[PaymentRow]:
    if not path.exists():
        raise SystemExit(f"Payment export not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            for key in ("payments", "invoices", "bills", "rows"):
                if isinstance(payload.get(key), list):
                    rows = payload[key]
                    break
            else:
                raise SystemExit("JSON export must contain payments, invoices, bills, or rows.")
        elif isinstance(payload, list):
            rows = payload
        else:
            raise SystemExit("JSON export must be a list or object containing rows.")
    else:
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

    parsed: list[PaymentRow] = []
    for offset, row in enumerate(rows, start=2):
        lowered = {str(key).strip().lower(): value for key, value in dict(row).items()}
        parsed.append(
            PaymentRow(
                row_number=offset,
                vendor_name=str(lowered.get("vendor_name") or lowered.get("vendor") or "").strip(),
                vendor_id=str(lowered.get("vendor_id") or lowered.get("supplier_id") or "").strip(),
                invoice_number=str(lowered.get("invoice_number") or lowered.get("invoice") or "").strip(),
                invoice_date=str(lowered.get("invoice_date") or lowered.get("bill_date") or "").strip(),
                payment_date=str(lowered.get("payment_date") or lowered.get("due_date") or "").strip(),
                amount=parse_amount(lowered.get("amount")),
                currency=str(lowered.get("currency") or "").strip().upper() or "USD",
                status=str(lowered.get("status") or "").strip().lower(),
                po_number=str(lowered.get("po_number") or lowered.get("po") or "").strip(),
                memo=str(lowered.get("memo") or lowered.get("description") or "").strip(),
            )
        )
    if not parsed:
        raise SystemExit("No payment rows found.")
    return parsed


def has_allow_hint(row: PaymentRow) -> bool:
    text = f"{row.vendor_name} {row.invoice_number} {row.memo} {row.status}".lower()
    return any(hint in text for hint in ALLOW_HINTS + NEGATIVE_HINTS) or row.amount < 0


def compare_rows(a: PaymentRow, b: PaymentRow, window_days: int) -> ExceptionFinding | None:
    if a.currency != b.currency or a.amount != b.amount:
        return None

    same_vendor_id = bool(a.vendor_id and a.vendor_id == b.vendor_id)
    vendor_alias = normalized_vendor(a.vendor_name) and normalized_vendor(a.vendor_name) == normalized_vendor(b.vendor_name)
    inv_a = normalized_invoice(a.invoice_number)
    inv_b = normalized_invoice(b.invoice_number)
    digits_a = invoice_digits(a.invoice_number)
    digits_b = invoice_digits(b.invoice_number)
    invoice_match = bool(inv_a and inv_a == inv_b) or bool(digits_a and digits_a == digits_b)
    same_po = bool(a.po_number and a.po_number == b.po_number)
    dates_close = close_dates(a, b, window_days)
    paid_pending = (a.status in PAID_STATUSES and b.status in PENDING_STATUSES) or (
        b.status in PAID_STATUSES and a.status in PENDING_STATUSES
    )

    evidence: list[str] = []
    if paid_pending:
        evidence.append("paid_vs_pending_collision")
    if invoice_match:
        evidence.append("normalized_invoice_match")
    if same_vendor_id:
        evidence.append("same_vendor_id")
    elif vendor_alias:
        evidence.append("vendor_alias_match")
    if same_po:
        evidence.append("same_po")
    if dates_close:
        evidence.append("close_dates")
    evidence.append("same_amount")

    if invoice_match and (same_vendor_id or vendor_alias) and (paid_pending or same_po or dates_close):
        risk = "high" if paid_pending or same_vendor_id else "medium"
        action = "hold_payment" if risk == "high" else "ap_review"
        step = "Hold one row and confirm the intended invoice record." if action == "hold_payment" else "Confirm whether duplicate vendor masters or invoice variants exist."
        return ExceptionFinding(risk, action, (a, b), tuple(evidence), step)

    if invoice_match and same_po and dates_close:
        return ExceptionFinding(
            "medium",
            "ap_review",
            (a, b),
            tuple(evidence),
            "Confirm whether duplicate vendor masters or invoice variants exist.",
        )

    if same_po and (same_vendor_id or vendor_alias) and dates_close:
        return ExceptionFinding(
            "medium",
            "ap_review",
            (a, b),
            tuple(evidence),
            "Review same-PO same-amount rows before release.",
        )

    if dates_close and (same_vendor_id or vendor_alias) and not (has_allow_hint(a) or has_allow_hint(b)):
        return ExceptionFinding(
            "low",
            "ap_review",
            (a, b),
            tuple(evidence),
            "Confirm this is not a recurring or split payment.",
        )
    return None


def find_exceptions(rows: list[PaymentRow], window_days: int) -> list[ExceptionFinding]:
    findings: list[ExceptionFinding] = []
    for index, left in enumerate(rows):
        for right in rows[index + 1 :]:
            finding = compare_rows(left, right, window_days)
            if finding is not None:
                findings.append(finding)
    risk_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(findings, key=lambda item: (risk_order[item.risk], item.rows[0].row_number, item.rows[1].row_number))


def format_amount(row: PaymentRow) -> str:
    return f"{row.currency} {row.amount:.2f}"


def render(rows: list[PaymentRow], findings: list[ExceptionFinding]) -> str:
    high_count = sum(1 for finding in findings if finding.risk == "high")
    medium_count = sum(1 for finding in findings if finding.risk == "medium")
    if high_count:
        decision = "Hold payment run: high-risk duplicate-payment exceptions exist."
    elif medium_count:
        decision = "Release after AP review: medium-risk exceptions need reviewer disposition."
    else:
        decision = "No material duplicate risk found in the supplied export."

    lines = [
        "## Payment Run Decision",
        "",
        decision,
        "",
        "## Duplicate Exceptions",
        "",
        "| Risk | Action | Rows | Vendor | Invoice | Amount | Evidence | Reviewer next step |",
        "|---|---|---|---|---|---:|---|---|",
    ]
    if findings:
        for finding in findings:
            left, right = finding.rows
            lines.append(
                "| {risk} | {action} | {rows} | {vendors} | {invoices} | {amount} | {evidence} | {step} |".format(
                    risk=finding.risk,
                    action=finding.action,
                    rows=f"{left.row_number}, {right.row_number}",
                    vendors=f"{left.vendor_name} / {right.vendor_name}",
                    invoices=f"{left.invoice_number or '(missing)'} / {right.invoice_number or '(missing)'}",
                    amount=format_amount(left),
                    evidence=", ".join(finding.evidence),
                    step=finding.reviewer_step,
                )
            )
    else:
        lines.append("| low | no_exception | - | - | - | - | No duplicate controls triggered. | Archive export with reviewer note. |")

    recurring_rows = [row for row in rows if has_allow_hint(row)]
    lines.extend(
        [
            "",
            "## Controls Checked",
            "",
            "Exact invoice match, normalized invoice match, vendor alias, same amount/date window, paid-versus-pending collision, and PO collision.",
            "",
            "## Safe Release Steps",
            "",
        ]
    )
    if high_count:
        lines.append("- Remove or hold high-risk rows before releasing payment.")
    if medium_count:
        lines.append("- Record AP reviewer disposition for medium-risk rows.")
    if recurring_rows:
        row_numbers = ", ".join(str(row.row_number) for row in recurring_rows)
        lines.append(f"- Rows with recurring/credit context to allow only with note: {row_numbers}.")
    lines.append("- Archive the export and this exception report with the payment-run approval record.")

    lines.extend(["", "## Open Questions", ""])
    if findings:
        lines.append("- Which row is the intended payable record for each high-risk pair?")
        lines.append("- Are any vendor aliases duplicate vendor masters that should be merged?")
    else:
        lines.append("- None from the supplied export.")
    return "\n".join(lines) + "\n"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payments", required=True, type=Path, help="CSV or JSON AP export path.")
    parser.add_argument("--date-window-days", type=int, default=14, help="Close-date window for same-amount review.")
    parser.add_argument("--output", type=Path, help="Optional Markdown output path.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    rows = read_rows(args.payments)
    findings = find_exceptions(rows, args.date_window_days)
    report = render(rows, findings)
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
