#!/usr/bin/env python3
"""Review vendor bank-change requests for payment-redirection risk."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable


TRUSTED_CALLBACK_SOURCES = {
    "vendor_master",
    "contract",
    "prior_invoice",
    "known_contact",
    "procurement_record",
    "erp_record",
}
UNTRUSTED_CALLBACK_SOURCES = {
    "request_email",
    "current_email",
    "invoice",
    "email_signature",
    "request_attachment",
    "unknown",
    "",
}
URGENT_HINTS = (
    "urgent",
    "asap",
    "today",
    "immediately",
    "rush",
    "late fee",
    "wire now",
    "avoid delay",
)


@dataclass(frozen=True)
class BankChangeRequest:
    row_number: int
    request_id: str
    vendor_name: str
    vendor_id: str
    requester_email: str
    request_channel: str
    requested_at: str
    effective_date: str
    old_routing: str
    old_account_last4: str
    new_routing: str
    new_account_last4: str
    new_bank_country: str
    vendor_country: str
    amount_at_risk: Decimal
    invoice_id: str
    callback_status: str
    callback_contact_source: str
    callback_performed_by: str
    approver_count: int
    bank_letter_present: bool
    w9_present: bool
    first_payment: bool
    days_since_vendor_created: int | None
    memo: str


@dataclass(frozen=True)
class VendorRecord:
    vendor_id: str
    vendor_name: str
    trusted_domain: str
    country: str
    current_routing: str
    current_account_last4: str
    trusted_phone_present: bool


@dataclass(frozen=True)
class Finding:
    risk: str
    action: str
    request: BankChangeRequest
    flags: tuple[str, ...]
    reviewer_step: str


def clean_key(value: object) -> str:
    return str(value or "").strip().lower()


def parse_bool(value: object) -> bool:
    return clean_key(value) in {"1", "true", "yes", "y", "present", "available"}


def parse_int(value: object) -> int | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return int(float(raw))
    except ValueError:
        return None


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


def email_domain(email: str) -> str:
    if "@" not in email:
        return ""
    return email.rsplit("@", 1)[1].strip().lower()


def normalize_domain(domain: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", domain.lower())


def domain_similarity(a: str, b: str) -> float:
    left = normalize_domain(a)
    right = normalize_domain(b)
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


def changed_bank_details(row: BankChangeRequest) -> bool:
    if row.new_routing and row.old_routing and row.new_routing != row.old_routing:
        return True
    if row.new_account_last4 and row.old_account_last4 and row.new_account_last4 != row.old_account_last4:
        return True
    return bool(row.new_routing or row.new_account_last4)


def load_records(path: Path, top_level_keys: tuple[str, ...]) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"Input file not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            for key in top_level_keys:
                if isinstance(payload.get(key), list):
                    rows = payload[key]
                    break
            else:
                raise SystemExit(f"JSON input must contain one of: {', '.join(top_level_keys)}.")
        elif isinstance(payload, list):
            rows = payload
        else:
            raise SystemExit("JSON input must be a list or an object containing rows.")
        return [dict(row) for row in rows]
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_requests(path: Path) -> list[BankChangeRequest]:
    rows = load_records(path, ("requests", "bank_changes", "rows"))
    parsed: list[BankChangeRequest] = []
    for offset, row in enumerate(rows, start=2):
        lowered = {clean_key(key): value for key, value in row.items()}
        days_since_vendor_created = parse_int(lowered.get("days_since_vendor_created"))
        parsed.append(
            BankChangeRequest(
                row_number=offset,
                request_id=str(lowered.get("request_id") or lowered.get("id") or f"row-{offset}").strip(),
                vendor_name=str(lowered.get("vendor_name") or lowered.get("vendor") or "").strip(),
                vendor_id=str(lowered.get("vendor_id") or lowered.get("supplier_id") or "").strip(),
                requester_email=str(lowered.get("requester_email") or lowered.get("email") or "").strip(),
                request_channel=str(lowered.get("request_channel") or lowered.get("channel") or "").strip().lower(),
                requested_at=str(lowered.get("requested_at") or lowered.get("request_date") or "").strip(),
                effective_date=str(lowered.get("effective_date") or "").strip(),
                old_routing=str(lowered.get("old_routing") or lowered.get("current_routing") or "").strip(),
                old_account_last4=str(lowered.get("old_account_last4") or lowered.get("current_account_last4") or "").strip(),
                new_routing=str(lowered.get("new_routing") or "").strip(),
                new_account_last4=str(lowered.get("new_account_last4") or "").strip(),
                new_bank_country=str(lowered.get("new_bank_country") or lowered.get("bank_country") or "").strip().upper(),
                vendor_country=str(lowered.get("vendor_country") or "").strip().upper(),
                amount_at_risk=parse_amount(lowered.get("amount_at_risk") or lowered.get("payment_amount")),
                invoice_id=str(lowered.get("invoice_id") or lowered.get("invoice_number") or "").strip(),
                callback_status=str(lowered.get("callback_status") or "").strip().lower(),
                callback_contact_source=str(lowered.get("callback_contact_source") or "").strip().lower(),
                callback_performed_by=str(lowered.get("callback_performed_by") or "").strip(),
                approver_count=parse_int(lowered.get("approver_count")) or 0,
                bank_letter_present=parse_bool(lowered.get("bank_letter_present")),
                w9_present=parse_bool(lowered.get("w9_present")),
                first_payment=parse_bool(lowered.get("first_payment")),
                days_since_vendor_created=days_since_vendor_created,
                memo=str(lowered.get("memo") or lowered.get("notes") or "").strip(),
            )
        )
    if not parsed:
        raise SystemExit("No bank-change request rows found.")
    return parsed


def read_vendor_master(path: Path | None) -> dict[str, VendorRecord]:
    if path is None:
        return {}
    rows = load_records(path, ("vendors", "suppliers", "rows"))
    vendors: dict[str, VendorRecord] = {}
    for row in rows:
        lowered = {clean_key(key): value for key, value in row.items()}
        record = VendorRecord(
            vendor_id=str(lowered.get("vendor_id") or lowered.get("supplier_id") or "").strip(),
            vendor_name=str(lowered.get("vendor_name") or lowered.get("vendor") or "").strip(),
            trusted_domain=str(lowered.get("trusted_domain") or lowered.get("email_domain") or "").strip().lower(),
            country=str(lowered.get("country") or lowered.get("vendor_country") or "").strip().upper(),
            current_routing=str(lowered.get("current_routing") or "").strip(),
            current_account_last4=str(lowered.get("current_account_last4") or "").strip(),
            trusted_phone_present=parse_bool(lowered.get("trusted_phone_present")),
        )
        if record.vendor_id:
            vendors[record.vendor_id] = record
    return vendors


def days_between(left: str, right: str) -> int | None:
    left_date = parse_date(left)
    right_date = parse_date(right)
    if left_date is None or right_date is None:
        return None
    return abs((right_date - left_date).days)


def build_flags(row: BankChangeRequest, vendor: VendorRecord | None, vendors: Iterable[VendorRecord]) -> list[str]:
    flags: list[str] = []
    if changed_bank_details(row):
        flags.append("bank_details_changed")

    if row.callback_status not in {"complete", "verified", "passed"}:
        flags.append("callback_missing_or_incomplete")
    if row.callback_contact_source in UNTRUSTED_CALLBACK_SOURCES:
        flags.append("callback_used_untrusted_source")
    elif row.callback_contact_source not in TRUSTED_CALLBACK_SOURCES:
        flags.append("callback_source_needs_review")
    if row.approver_count < 2:
        flags.append("insufficient_dual_approval")

    if row.request_channel in {"email", "invoice", "portal_message"}:
        flags.append("request_arrived_outside_controlled_form")

    trusted_domain = vendor.trusted_domain if vendor else ""
    request_domain = email_domain(row.requester_email)
    if trusted_domain and request_domain:
        if request_domain != trusted_domain:
            if domain_similarity(request_domain, trusted_domain) >= 0.82:
                flags.append("lookalike_email_domain")
            else:
                flags.append("email_domain_mismatch")

    vendor_country = row.vendor_country or (vendor.country if vendor else "")
    if vendor_country and row.new_bank_country and vendor_country != row.new_bank_country:
        flags.append("bank_country_mismatch")

    if not row.bank_letter_present:
        flags.append("missing_bank_letter")
    if not row.w9_present:
        flags.append("missing_w9_or_tax_record")

    if row.first_payment:
        flags.append("first_payment_to_vendor")
    if row.days_since_vendor_created is not None and row.days_since_vendor_created <= 90:
        flags.append("new_vendor_under_90_days")

    if any(hint in row.memo.lower() for hint in URGENT_HINTS):
        flags.append("urgency_or_pressure_language")

    effective_gap = days_between(row.requested_at, row.effective_date)
    if effective_gap is not None and effective_gap <= 2:
        flags.append("same_week_effective_date")

    if row.amount_at_risk >= Decimal("50000"):
        flags.append("large_payment_exposure")

    new_account = (row.new_routing, row.new_account_last4)
    for other in vendors:
        if vendor and other.vendor_id == vendor.vendor_id:
            continue
        if row.new_routing and row.new_account_last4 and new_account == (
            other.current_routing,
            other.current_account_last4,
        ):
            flags.append("bank_account_reused_by_another_vendor")
            break

    return flags


def classify(row: BankChangeRequest, flags: list[str]) -> tuple[str, str, str]:
    high_flags = {
        "callback_missing_or_incomplete",
        "callback_used_untrusted_source",
        "lookalike_email_domain",
        "bank_account_reused_by_another_vendor",
    }
    medium_flags = {
        "email_domain_mismatch",
        "bank_country_mismatch",
        "insufficient_dual_approval",
        "first_payment_to_vendor",
        "new_vendor_under_90_days",
        "urgency_or_pressure_language",
        "large_payment_exposure",
        "same_week_effective_date",
    }
    high_hits = high_flags.intersection(flags)
    medium_hits = medium_flags.intersection(flags)

    if high_hits and ("bank_details_changed" in flags or row.amount_at_risk > 0):
        return (
            "high",
            "hold_change",
            "Do not update vendor bank details until independent callback, dual approval, and evidence are complete.",
        )
    if len(medium_hits) >= 2 or ("insufficient_dual_approval" in flags and row.amount_at_risk >= Decimal("10000")):
        return (
            "medium",
            "secondary_verification",
            "Route to a second reviewer and verify through a trusted contact source before releasing payment.",
        )
    if flags:
        return (
            "low",
            "document_and_monitor",
            "Record the evidence trail and confirm all required artifacts before the next payment run.",
        )
    return ("low", "ready_with_evidence", "No material red flags found in the supplied fields.")


def analyze(requests: list[BankChangeRequest], vendor_master: dict[str, VendorRecord]) -> list[Finding]:
    vendors = tuple(vendor_master.values())
    findings: list[Finding] = []
    for row in requests:
        vendor = vendor_master.get(row.vendor_id)
        flags = build_flags(row, vendor, vendors)
        risk, action, step = classify(row, flags)
        findings.append(Finding(risk, action, row, tuple(flags), step))
    risk_order = {"high": 0, "medium": 1, "low": 2}
    action_order = {"hold_change": 0, "secondary_verification": 1, "document_and_monitor": 2, "ready_with_evidence": 3}
    return sorted(findings, key=lambda item: (risk_order[item.risk], action_order[item.action], item.request.row_number))


def render(findings: list[Finding]) -> str:
    hold_count = sum(1 for finding in findings if finding.action == "hold_change")
    secondary_count = sum(1 for finding in findings if finding.action == "secondary_verification")
    if hold_count:
        decision = "Hold bank-change updates: high-risk payment-redirection signals require independent verification."
    elif secondary_count:
        decision = "Do not release automatically: secondary verification is required before payment."
    else:
        decision = "No high-risk bank-change signal found in the supplied rows."

    lines = [
        "## Bank Change Decision",
        "",
        decision,
        "",
        "## Request Findings",
        "",
        "| Risk | Action | Row | Request | Vendor | Amount at risk | Flags | Reviewer next step |",
        "|---|---|---:|---|---|---:|---|---|",
    ]
    for finding in findings:
        row = finding.request
        flags = ", ".join(finding.flags) if finding.flags else "none"
        lines.append(
            "| {risk} | {action} | {row_num} | {request_id} | {vendor} | {amount} | {flags} | {step} |".format(
                risk=finding.risk,
                action=finding.action,
                row_num=row.row_number,
                request_id=row.request_id,
                vendor=row.vendor_name or row.vendor_id or "(missing)",
                amount=f"{row.amount_at_risk:.2f}",
                flags=flags,
                step=finding.reviewer_step,
            )
        )

    lines.extend(
        [
            "",
            "## Controls Checked",
            "",
            "- Independent callback source, callback completion, and dual approval.",
            "- Email-domain mismatch or lookalike domain against the vendor master.",
            "- Bank country mismatch, reused bank details, new-vendor timing, and first-payment exposure.",
            "- Missing bank letter or tax record, urgency language, and same-week effective dates.",
            "",
            "## Safe Release Steps",
            "",
            "1. Hold all `hold_change` rows outside the ERP or bank portal until a trusted-contact callback is complete.",
            "2. Require a second internal approver for all bank-detail changes and high-value payments.",
            "3. Archive the callback source, reviewer names, bank evidence, and request packet with the vendor record.",
            "4. Re-run this preflight after evidence is corrected; do not rely on email-thread continuity as proof.",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review vendor bank-change requests for payment-redirection risk.")
    parser.add_argument("--requests", required=True, help="CSV or JSON file containing vendor bank-change requests.")
    parser.add_argument("--vendor-master", help="Optional CSV or JSON vendor master with trusted domains and current bank details.")
    parser.add_argument("--output", help="Optional Markdown output path. Defaults to stdout.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    requests = read_requests(Path(args.requests))
    vendor_master = read_vendor_master(Path(args.vendor_master)) if args.vendor_master else {}
    report = render(analyze(requests, vendor_master))
    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
