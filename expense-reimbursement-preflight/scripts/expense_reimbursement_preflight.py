#!/usr/bin/env python3
"""Preflight employee reimbursement reports before approval or payroll release."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


TRUE_VALUES = {"1", "true", "yes", "y", "attached", "present", "provided"}
FALSE_VALUES = {"0", "false", "no", "n", "missing", "none", ""}
DEFAULT_POLICY = {
    "receipt_required_over": "25.00",
    "itemized_required_over": "75.00",
    "attendees_required_over": "75.00",
    "max_submission_age_days": 60,
    "mileage_rate": "0.70",
    "allowed_currencies": ["USD"],
    "category_limits": {
        "meal": "100.00",
        "client_meal": "200.00",
        "lodging": "350.00",
        "airfare": "1200.00",
        "supplies": "500.00",
    },
    "receipt_required_categories": ["lodging", "airfare", "supplies"],
    "itemized_required_categories": ["meal", "client_meal", "lodging"],
    "attendee_required_categories": ["meal", "client_meal", "event"],
    "prohibited_categories": ["personal", "gift_card", "cash_advance"],
    "sensitive_terms": ["personal", "gift card", "cash advance"],
}


@dataclass(frozen=True)
class ExpenseRow:
    row_number: int
    report_id: str
    employee: str
    expense_date: date | None
    submitted_date: date | None
    category: str
    merchant: str
    amount: Decimal
    currency: str
    receipt_id: str
    receipt_attached: bool
    itemized_receipt: bool
    business_purpose: str
    attendees: str
    project: str
    gl_code: str
    miles: Decimal
    notes: str


@dataclass(frozen=True)
class Finding:
    row: ExpenseRow
    risk: str
    action: str
    flag: str
    evidence: str
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


def parse_bool(value: object) -> bool:
    raw = str(value or "").strip().lower()
    if raw in TRUE_VALUES:
        return True
    if raw in FALSE_VALUES:
        return False
    return False


def norm(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def money(value: Decimal, currency: str) -> str:
    return f"{currency} {value:.2f}"


def load_policy(path: Path | None) -> dict[str, object]:
    policy = dict(DEFAULT_POLICY)
    if path:
        if not path.exists():
            raise SystemExit(f"Policy file not found: {path}")
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise SystemExit("Policy JSON must be an object.")
        for key, value in loaded.items():
            if key == "category_limits" and isinstance(value, dict):
                merged_limits = dict(policy["category_limits"])  # type: ignore[arg-type]
                merged_limits.update(value)
                policy[key] = merged_limits
            else:
                policy[key] = value
    return policy


def load_records(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"Expense report not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            for key in ("expenses", "rows", "claims", "report"):
                if isinstance(payload.get(key), list):
                    return list(payload[key])
            raise SystemExit("JSON input must contain expenses, rows, claims, or report.")
        if isinstance(payload, list):
            return list(payload)
        raise SystemExit("JSON input must be a list or an object containing expense rows.")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_rows(path: Path) -> list[ExpenseRow]:
    rows: list[ExpenseRow] = []
    for offset, raw in enumerate(load_records(path), start=2):
        row = {str(key).strip().lower(): value for key, value in dict(raw).items()}
        category = norm(row.get("category") or row.get("expense_type"))
        amount = parse_decimal(row.get("amount") or row.get("reimbursement_amount"))
        miles = parse_decimal(row.get("miles") or row.get("distance_miles"))
        rows.append(
            ExpenseRow(
                row_number=offset,
                report_id=str(row.get("report_id") or row.get("claim_id") or "").strip(),
                employee=str(row.get("employee") or row.get("employee_name") or "").strip(),
                expense_date=parse_date(row.get("expense_date") or row.get("date")),
                submitted_date=parse_date(row.get("submitted_date") or row.get("submission_date")),
                category=category,
                merchant=str(row.get("merchant") or row.get("vendor") or "").strip(),
                amount=amount,
                currency=str(row.get("currency") or "USD").strip().upper() or "USD",
                receipt_id=str(row.get("receipt_id") or row.get("receipt_number") or "").strip(),
                receipt_attached=parse_bool(row.get("receipt_attached") or row.get("receipt")),
                itemized_receipt=parse_bool(row.get("itemized_receipt") or row.get("itemized")),
                business_purpose=str(row.get("business_purpose") or row.get("purpose") or "").strip(),
                attendees=str(row.get("attendees") or row.get("participants") or "").strip(),
                project=str(row.get("project") or row.get("client") or row.get("job") or "").strip(),
                gl_code=str(row.get("gl_code") or row.get("account") or "").strip(),
                miles=miles,
                notes=str(row.get("notes") or row.get("memo") or "").strip(),
            )
        )
    if not rows:
        raise SystemExit("No expense rows found.")
    return rows


def as_decimal(policy: dict[str, object], key: str) -> Decimal:
    return parse_decimal(policy.get(key))


def as_int(policy: dict[str, object], key: str) -> int:
    try:
        return int(policy.get(key, 0))
    except (TypeError, ValueError):
        return 0


def as_set(policy: dict[str, object], key: str) -> set[str]:
    values = policy.get(key, [])
    if not isinstance(values, list):
        return set()
    return {norm(value) for value in values}


def charge_key(row: ExpenseRow) -> tuple[str, str, str, str, str]:
    amount_key = f"{row.amount:.2f}"
    date_key = row.expense_date.isoformat() if row.expense_date else ""
    return (norm(row.employee), date_key, norm(row.merchant), amount_key, row.currency)


def classify(rows: list[ExpenseRow], policy: dict[str, object], today: date) -> list[Finding]:
    receipt_required_over = as_decimal(policy, "receipt_required_over")
    itemized_required_over = as_decimal(policy, "itemized_required_over")
    attendees_required_over = as_decimal(policy, "attendees_required_over")
    mileage_rate = as_decimal(policy, "mileage_rate")
    max_age_days = as_int(policy, "max_submission_age_days")
    allowed_currencies = as_set(policy, "allowed_currencies")
    receipt_required_categories = as_set(policy, "receipt_required_categories")
    itemized_required_categories = as_set(policy, "itemized_required_categories")
    attendee_required_categories = as_set(policy, "attendee_required_categories")
    prohibited_categories = as_set(policy, "prohibited_categories")
    sensitive_terms = as_set(policy, "sensitive_terms")
    raw_limits = policy.get("category_limits", {})
    category_limits = {norm(key): parse_decimal(value) for key, value in raw_limits.items()} if isinstance(raw_limits, dict) else {}

    receipt_counts = Counter(norm(row.receipt_id) for row in rows if row.receipt_id.strip())
    charge_counts = Counter(charge_key(row) for row in rows if row.amount > 0)
    findings: list[Finding] = []

    def add(row: ExpenseRow, risk: str, action: str, flag: str, evidence: str, next_step: str) -> None:
        findings.append(Finding(row, risk, action, flag, evidence, next_step))

    for row in rows:
        category_text = norm(f"{row.category} {row.notes}")

        receipt_required = row.amount >= receipt_required_over or row.category in receipt_required_categories
        if receipt_required and not row.receipt_attached and not row.receipt_id:
            add(
                row,
                "high",
                "hold_reimbursement",
                "missing_receipt",
                f"{money(row.amount, row.currency)} requires receipt support.",
                "Attach receipt or missing-receipt affidavit before approval.",
            )

        if row.receipt_id and receipt_counts[norm(row.receipt_id)] > 1:
            add(
                row,
                "high",
                "hold_reimbursement",
                "duplicate_receipt_or_charge",
                f"Receipt ID {row.receipt_id} appears more than once.",
                "Confirm one reimbursable claim and remove or explain duplicates.",
            )
        elif charge_counts[charge_key(row)] > 1:
            add(
                row,
                "high",
                "hold_reimbursement",
                "duplicate_receipt_or_charge",
                "Same employee, date, merchant, amount, and currency appears more than once.",
                "Compare receipts and card charges before reimbursement.",
            )

        if row.category in prohibited_categories or any(term and term in category_text for term in sensitive_terms):
            add(
                row,
                "high",
                "hold_reimbursement",
                "prohibited_or_sensitive_category",
                f"Category or notes include restricted term: {row.category or row.notes}.",
                "Route to finance owner for exception approval or employee correction.",
            )

        limit = category_limits.get(row.category)
        if limit is not None and row.amount > limit:
            add(
                row,
                "medium",
                "manager_review",
                "category_limit_exceeded",
                f"{money(row.amount, row.currency)} exceeds {row.category} limit {money(limit, row.currency)}.",
                "Capture manager approval, client/event context, or reduce reimbursable amount.",
            )

        if row.category in itemized_required_categories and row.amount >= itemized_required_over and not row.itemized_receipt:
            add(
                row,
                "medium",
                "manager_review",
                "itemized_receipt_missing",
                "Receipt is present but not marked itemized for a policy-sensitive category.",
                "Attach itemized receipt or documented exception.",
            )

        if row.category in attendee_required_categories and row.amount >= attendees_required_over and not row.attendees:
            add(
                row,
                "medium",
                "manager_review",
                "meal_attendees_missing",
                "Meal, event, or client entertainment expense lacks attendee names.",
                "Add attendee list and business relationship before approval.",
            )

        if not row.business_purpose:
            add(
                row,
                "medium",
                "employee_correction",
                "business_purpose_missing",
                "Business purpose is blank.",
                "Add concise purpose tied to customer, project, trip, or role.",
            )

        if not row.gl_code or not row.project:
            add(
                row,
                "low",
                "coding_review",
                "coding_context_missing",
                "Project/client or GL code is missing.",
                "Add accounting code before export to payroll or ERP.",
            )

        if allowed_currencies and norm(row.currency) not in allowed_currencies:
            add(
                row,
                "medium",
                "finance_review",
                "currency_not_allowed",
                f"Currency {row.currency} is not in the local policy allowlist.",
                "Confirm FX support and reimbursable amount before approval.",
            )

        if max_age_days and row.expense_date:
            submitted = row.submitted_date or today
            age_days = (submitted - row.expense_date).days
            if age_days > max_age_days:
                add(
                    row,
                    "medium",
                    "manager_review",
                    "late_submission",
                    f"Submitted {age_days} days after expense date; policy limit is {max_age_days}.",
                    "Capture late-submission exception approval or reject per policy.",
                )

        if row.category == "mileage" and row.miles > 0 and mileage_rate > 0:
            claimed_rate = row.amount / row.miles
            if claimed_rate > mileage_rate:
                add(
                    row,
                    "high",
                    "hold_reimbursement",
                    "mileage_rate_exceeds_policy",
                    f"Claimed {money(claimed_rate, row.currency)}/mile exceeds policy {money(mileage_rate, row.currency)}/mile.",
                    "Recalculate mileage reimbursement or document approved exception.",
                )

    return findings


def render(rows: list[ExpenseRow], findings: list[Finding]) -> str:
    hold_count = sum(1 for finding in findings if finding.action == "hold_reimbursement")
    review_count = sum(1 for finding in findings if finding.action != "hold_reimbursement")
    if hold_count:
        decision = "Hold reimbursement: high-risk exceptions need correction before approval."
    elif review_count:
        decision = "Review before reimbursement: policy or coding exceptions need owner disposition."
    else:
        decision = "No material reimbursement exceptions found."

    lines = [
        "## Expense Reimbursement Decision",
        decision,
        "",
        "## Exception Summary",
        f"- Rows reviewed: {len(rows)}",
        f"- Hold exceptions: {hold_count}",
        f"- Review/correction exceptions: {review_count}",
        "",
        "## Expense Exceptions",
        "| Risk | Action | Row | Employee | Category | Merchant | Amount | Flag | Evidence | Next step |",
        "|---|---|---:|---|---|---|---:|---|---|---|",
    ]
    if not findings:
        lines.append("| low | release | - | - | - | - | - | none | No policy exceptions found. | Archive report with approval evidence. |")
    else:
        for finding in findings:
            row = finding.row
            lines.append(
                "| {risk} | {action} | {row_number} | {employee} | {category} | {merchant} | {amount} | {flag} | {evidence} | {next_step} |".format(
                    risk=finding.risk,
                    action=finding.action,
                    row_number=row.row_number,
                    employee=row.employee or "-",
                    category=row.category or "-",
                    merchant=row.merchant or "-",
                    amount=money(row.amount, row.currency),
                    flag=finding.flag,
                    evidence=finding.evidence,
                    next_step=finding.next_step,
                )
            )
    lines.extend(
        [
            "",
            "## Guardrails",
            "- Treat findings as reimbursement-control exceptions, not fraud conclusions.",
            "- Do not approve, reject, or edit live expense-system records without explicit authority.",
            "- Preserve receipts, policy exceptions, manager approval, and reimbursement export evidence.",
            "- Apply the user's local policy when it is stricter than the bundled defaults.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preflight employee reimbursement reports.")
    parser.add_argument("--expenses", required=True, type=Path, help="CSV or JSON expense report export.")
    parser.add_argument("--policy", type=Path, help="JSON reimbursement policy.")
    parser.add_argument("--today", help="Review date in YYYY-MM-DD format.")
    args = parser.parse_args(argv)

    today = parse_date(args.today) if args.today else date.today()
    if today is None:
        raise SystemExit("--today must use YYYY-MM-DD, YYYY/MM/DD, MM/DD/YYYY, or DD/MM/YYYY.")
    policy = load_policy(args.policy)
    rows = parse_rows(args.expenses)
    findings = classify(rows, policy, today)
    print(render(rows, findings))
    return 2 if any(finding.action == "hold_reimbursement" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
