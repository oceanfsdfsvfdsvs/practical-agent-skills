#!/usr/bin/env python3
"""Prioritize vendor contract renewals before auto-renewal deadlines pass."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path


TRUE_VALUES = {"1", "true", "yes", "y", "auto", "automatic", "evergreen"}
FALSE_VALUES = {"0", "false", "no", "n", "manual", "none"}
MISSING_OWNER = {"", "unknown", "tbd", "former employee", "left company", "departed"}
LOW_USAGE_HINTS = {"low usage", "unused", "shelfware", "duplicate tool", "replacement planned", "cancel candidate"}
CRITICAL_METHOD_WORDS = {"certified", "written", "legal", "email", "portal", "account manager"}


@dataclass(frozen=True)
class ContractRow:
    row_number: int
    vendor: str
    contract_id: str
    owner: str
    department: str
    annual_cost: Decimal
    currency: str
    renewal_date: date | None
    notice_days: int | None
    notice_deadline: date | None
    auto_renew: bool | None
    renewal_term: str
    price_increase_cap: str
    termination_notice_method: str
    notice_address: str
    last_review_date: date | None
    usage_status: str
    notes: str


@dataclass(frozen=True)
class Finding:
    row: ContractRow
    risk: str
    action: str
    deadline_status: str
    evidence: tuple[str, ...]
    next_step: str


def parse_date(value: object) -> date | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def parse_decimal(value: object) -> Decimal:
    raw = str(value or "").strip().replace(",", "").replace("$", "")
    if not raw:
        return Decimal("0")
    try:
        return Decimal(raw)
    except InvalidOperation:
        return Decimal("0")


def parse_int(value: object) -> int | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def parse_bool(value: object) -> bool | None:
    raw = str(value or "").strip().lower()
    if raw in TRUE_VALUES:
        return True
    if raw in FALSE_VALUES:
        return False
    return None


def normalized_text(value: str) -> str:
    return " ".join(value.lower().split())


def load_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"Contract inventory not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            for key in ("contracts", "rows", "vendors", "agreements"):
                if isinstance(payload.get(key), list):
                    return list(payload[key])
            raise SystemExit("JSON input must contain contracts, rows, vendors, or agreements.")
        if isinstance(payload, list):
            return list(payload)
        raise SystemExit("JSON input must be a list or an object containing contract rows.")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_rows(path: Path) -> list[ContractRow]:
    parsed: list[ContractRow] = []
    for offset, raw in enumerate(load_rows(path), start=2):
        row = {str(key).strip().lower(): value for key, value in dict(raw).items()}
        renewal_date = parse_date(row.get("renewal_date") or row.get("end_date") or row.get("term_end"))
        notice_days = parse_int(row.get("notice_days") or row.get("cancellation_notice_days"))
        explicit_deadline = parse_date(row.get("notice_deadline") or row.get("cancellation_deadline"))
        derived_deadline = renewal_date - timedelta(days=notice_days) if renewal_date and notice_days is not None else None
        parsed.append(
            ContractRow(
                row_number=offset,
                vendor=str(row.get("vendor") or row.get("vendor_name") or row.get("supplier") or "").strip(),
                contract_id=str(row.get("contract_id") or row.get("agreement_id") or row.get("id") or "").strip(),
                owner=str(row.get("owner") or row.get("business_owner") or row.get("stakeholder") or "").strip(),
                department=str(row.get("department") or row.get("team") or "").strip(),
                annual_cost=parse_decimal(row.get("annual_cost") or row.get("annual_spend") or row.get("cost")),
                currency=str(row.get("currency") or "").strip().upper() or "USD",
                renewal_date=renewal_date,
                notice_days=notice_days,
                notice_deadline=explicit_deadline or derived_deadline,
                auto_renew=parse_bool(row.get("auto_renew") or row.get("auto_renewal") or row.get("evergreen")),
                renewal_term=str(row.get("renewal_term") or row.get("term") or "").strip(),
                price_increase_cap=str(row.get("price_increase_cap") or row.get("uplift_cap") or "").strip(),
                termination_notice_method=str(
                    row.get("termination_notice_method") or row.get("notice_method") or ""
                ).strip(),
                notice_address=str(row.get("notice_address") or row.get("notice_recipient") or "").strip(),
                last_review_date=parse_date(row.get("last_review_date") or row.get("reviewed_at")),
                usage_status=str(row.get("usage_status") or row.get("usage") or "").strip(),
                notes=str(row.get("notes") or row.get("memo") or "").strip(),
            )
        )
    if not parsed:
        raise SystemExit("No contract rows found.")
    return parsed


def format_money(row: ContractRow) -> str:
    return f"{row.currency} {row.annual_cost:.2f}"


def classify(row: ContractRow, today: date, urgent_days: int, high_spend: Decimal) -> Finding:
    evidence: list[str] = []
    risk_points = 0

    if row.auto_renew is True:
        evidence.append("auto_renewal")
        risk_points += 2
    elif row.auto_renew is None:
        evidence.append("auto_renewal_unknown")
        risk_points += 1

    if row.notice_deadline is None:
        evidence.append("missing_notice_deadline")
        risk_points += 3
        days_to_deadline = None
        deadline_status = "unknown_deadline"
    else:
        days_to_deadline = (row.notice_deadline - today).days
        if days_to_deadline < 0:
            evidence.append("notice_deadline_passed")
            risk_points += 5
            deadline_status = f"passed_{abs(days_to_deadline)}d_ago"
        elif days_to_deadline <= urgent_days:
            evidence.append("notice_deadline_imminent")
            risk_points += 4
            deadline_status = f"due_in_{days_to_deadline}d"
        elif days_to_deadline <= 45:
            evidence.append("notice_deadline_near")
            risk_points += 3
            deadline_status = f"due_in_{days_to_deadline}d"
        elif days_to_deadline <= 90:
            evidence.append("renewal_planning_window")
            risk_points += 1
            deadline_status = f"due_in_{days_to_deadline}d"
        else:
            deadline_status = f"due_in_{days_to_deadline}d"

    owner_key = normalized_text(row.owner)
    if owner_key in MISSING_OWNER:
        evidence.append("missing_or_stale_owner")
        risk_points += 2

    if row.annual_cost >= high_spend:
        evidence.append("high_spend")
        risk_points += 2

    if not row.termination_notice_method:
        evidence.append("missing_notice_method")
        risk_points += 1
    elif not any(word in normalized_text(row.termination_notice_method) for word in CRITICAL_METHOD_WORDS):
        evidence.append("ambiguous_notice_method")
        risk_points += 1

    if not row.notice_address:
        evidence.append("missing_notice_recipient")
        risk_points += 1

    if row.auto_renew is True and not row.price_increase_cap:
        evidence.append("uncapped_price_increase")
        risk_points += 1

    usage_text = normalized_text(f"{row.usage_status} {row.notes}")
    if any(hint in usage_text for hint in LOW_USAGE_HINTS):
        evidence.append("usage_or_value_concern")
        risk_points += 1

    if row.last_review_date is None:
        evidence.append("missing_last_review")
        risk_points += 1
    elif (today - row.last_review_date).days > 365:
        evidence.append("review_stale_over_1y")
        risk_points += 1

    if "notice_deadline_passed" in evidence and row.auto_renew is True:
        risk = "high"
        action = "escalate_missed_window"
        next_step = "Escalate to owner, procurement, and legal; confirm whether renewal already locked and preserve notice evidence."
    elif "notice_deadline_imminent" in evidence or risk_points >= 8:
        risk = "high"
        action = "send_or_escalate_notice"
        next_step = "Confirm cancellation authority and send compliant notice before the deadline if exit is possible."
    elif risk_points >= 5:
        risk = "medium"
        action = "owner_review"
        next_step = "Assign owner, verify notice instructions, and decide renew/renegotiate/cancel before the notice window."
    elif days_to_deadline is not None and days_to_deadline <= 120:
        risk = "medium"
        action = "renegotiate_window"
        next_step = "Start stakeholder review and vendor benchmark before negotiation leverage expires."
    else:
        risk = "low"
        action = "monitor"
        next_step = "Keep renewal fields current and schedule the next review checkpoint."

    return Finding(row, risk, action, deadline_status, tuple(evidence), next_step)


def render(findings: list[Finding], today: date) -> str:
    high = sum(1 for item in findings if item.risk == "high")
    medium = sum(1 for item in findings if item.risk == "medium")
    missing_deadline = sum(1 for item in findings if "missing_notice_deadline" in item.evidence)
    missed = sum(1 for item in findings if "notice_deadline_passed" in item.evidence)

    if missed:
        decision = "Immediate escalation: at least one auto-renewal notice window appears to have passed."
    elif high:
        decision = "Act this week: high-risk renewal or cancellation deadlines need owner action."
    elif medium:
        decision = "Owner review needed: renewal decisions should be made before leverage expires."
    else:
        decision = "No urgent renewal risk found in the supplied inventory."

    lines = [
        "## Renewal Portfolio Decision",
        "",
        decision,
        "",
        "## Renewal Risk Summary",
        "",
        f"- Review date: {today.isoformat()}",
        f"- Contracts reviewed: {len(findings)}",
        f"- High risk: {high}",
        f"- Medium risk: {medium}",
        f"- Missing notice deadline: {missing_deadline}",
        f"- Missed notice window: {missed}",
        "",
        "## Renewal Exceptions",
        "",
        "| Risk | Action | Vendor | Owner | Spend | Renewal | Notice deadline | Evidence | Next step |",
        "|---|---|---|---|---:|---|---|---|---|",
    ]
    for finding in findings:
        row = finding.row
        lines.append(
            "| {risk} | {action} | {vendor} | {owner} | {spend} | {renewal} | {deadline} ({status}) | {evidence} | {step} |".format(
                risk=finding.risk,
                action=finding.action,
                vendor=row.vendor or f"row {row.row_number}",
                owner=row.owner or "missing",
                spend=format_money(row),
                renewal=row.renewal_date.isoformat() if row.renewal_date else "missing",
                deadline=row.notice_deadline.isoformat() if row.notice_deadline else "missing",
                status=finding.deadline_status,
                evidence=", ".join(finding.evidence) or "none",
                step=finding.next_step,
            )
        )

    lines.extend(
        [
            "",
            "## Owner Action Plan",
            "",
        ]
    )
    for finding in findings:
        if finding.risk in {"high", "medium"}:
            row = finding.row
            lines.append(
                f"- {row.vendor or 'Unknown vendor'}: {finding.action}; owner={row.owner or 'assign owner'}; "
                f"deadline={row.notice_deadline.isoformat() if row.notice_deadline else 'calculate from contract'}."
            )

    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "- Treat this as procurement operations support, not legal advice.",
            "- Do not send cancellation or non-renewal notice until authority, method, recipient, and contract language are confirmed.",
            "- Preserve a copy of the contract clause, notice proof, owner decision, and vendor acknowledgement.",
            "- If only a spreadsheet was provided, mark clause extraction confidence as provisional.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preflight vendor contract renewals for auto-renewal risk.")
    parser.add_argument("--contracts", required=True, type=Path, help="CSV or JSON contract inventory.")
    parser.add_argument("--today", default=date.today().isoformat(), help="Review date in YYYY-MM-DD format.")
    parser.add_argument("--urgent-days", type=int, default=14, help="Days before notice deadline considered urgent.")
    parser.add_argument("--high-spend", default="25000", help="Annual spend threshold for high-spend evidence.")
    parser.add_argument("--output", type=Path, help="Optional Markdown report output path.")
    args = parser.parse_args(argv)

    today = parse_date(args.today)
    if today is None:
        raise SystemExit("--today must be a valid date.")
    high_spend = parse_decimal(args.high_spend)
    rows = parse_rows(args.contracts)
    findings = sorted(
        (classify(row, today, args.urgent_days, high_spend) for row in rows),
        key=lambda item: ({"high": 0, "medium": 1, "low": 2}[item.risk], item.row.notice_deadline or date.max, item.row.vendor),
    )
    report = render(findings, today)
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
