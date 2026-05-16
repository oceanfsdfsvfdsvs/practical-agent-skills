#!/usr/bin/env python3
"""Audit SaaS licenses against HR and usage exports for rightsize actions."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


ACTIVE_LICENSE = {"active", "assigned", "paid", "enabled", "provisioned"}
INACTIVE_LICENSE = {"inactive", "disabled", "suspended", "cancelled", "canceled", "free"}
DEPARTED_EMPLOYEE = {"terminated", "departed", "left", "former", "inactive", "offboarded"}
ACTIVE_EMPLOYEE = {"active", "current", "employed"}
PREMIUM_PLAN_WORDS = {"pro", "business", "enterprise", "premium", "plus", "advanced", "creator"}
PRIVILEGED_ROLE_WORDS = {"admin", "owner", "super admin", "billing", "workspace admin"}
EXCEPTION_HINTS = {"service", "bot", "integration", "break-glass", "break glass", "legal", "audit", "seasonal"}


@dataclass(frozen=True)
class Employee:
    email: str
    status: str
    department: str
    manager: str
    termination_date: date | None


@dataclass(frozen=True)
class Usage:
    app: str
    email: str
    last_login_date: date | None
    activity_count_30d: int
    usage_minutes_30d: int
    feature_events_30d: int


@dataclass(frozen=True)
class LicenseSeat:
    row_number: int
    app: str
    email: str
    user_name: str
    plan: str
    status: str
    role: str
    annual_cost: Decimal
    currency: str
    department: str
    owner: str
    renewal_date: date | None
    contract_id: str


@dataclass(frozen=True)
class Finding:
    seat: LicenseSeat
    risk: str
    action: str
    annual_savings: Decimal
    evidence: tuple[str, ...]
    next_step: str


def normalized_text(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def normalize_email(value: object) -> str:
    return normalized_text(value)


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


def parse_int(value: object) -> int:
    raw = str(value or "").strip().replace(",", "")
    if not raw:
        return 0
    try:
        return int(float(raw))
    except ValueError:
        return 0


def parse_decimal(value: object) -> Decimal:
    raw = str(value or "").strip().replace(",", "").replace("$", "")
    if not raw:
        return Decimal("0")
    try:
        return Decimal(raw)
    except InvalidOperation:
        return Decimal("0")


def load_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"Input file not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [dict(item) for item in payload]
        if isinstance(payload, dict):
            for key in ("rows", "licenses", "employees", "usage", "users", "accounts"):
                if isinstance(payload.get(key), list):
                    return [dict(item) for item in payload[key]]
        raise SystemExit(f"JSON input must be a list or contain a row list: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def clean_row(raw: dict[str, object]) -> dict[str, object]:
    return {normalized_text(key).replace(" ", "_"): value for key, value in raw.items()}


def first(row: dict[str, object], *keys: str) -> object:
    for key in keys:
        if row.get(key) not in (None, ""):
            return row.get(key)
    return ""


def load_employees(path: Path | None) -> dict[str, Employee]:
    if path is None:
        return {}
    employees: dict[str, Employee] = {}
    for raw in load_rows(path):
        row = clean_row(raw)
        email = normalize_email(first(row, "email", "work_email", "user_email", "account_email"))
        if not email:
            continue
        employees[email] = Employee(
            email=email,
            status=normalized_text(first(row, "employee_status", "status", "employment_status")),
            department=str(first(row, "department", "team", "org")).strip(),
            manager=str(first(row, "manager", "owner")).strip(),
            termination_date=parse_date(first(row, "termination_date", "departed_date", "offboarded_at")),
        )
    return employees


def load_usage(path: Path | None) -> dict[tuple[str, str], Usage]:
    if path is None:
        return {}
    usage: dict[tuple[str, str], Usage] = {}
    for raw in load_rows(path):
        row = clean_row(raw)
        app = normalized_text(first(row, "app", "application", "tool", "vendor"))
        email = normalize_email(first(row, "email", "user_email", "account_email"))
        if not app or not email:
            continue
        usage[(app, email)] = Usage(
            app=app,
            email=email,
            last_login_date=parse_date(
                first(row, "last_login_date", "last_login", "last_seen", "last_activity_date")
            ),
            activity_count_30d=parse_int(first(row, "activity_count_30d", "logins_30d", "events_30d")),
            usage_minutes_30d=parse_int(first(row, "usage_minutes_30d", "minutes_30d")),
            feature_events_30d=parse_int(first(row, "feature_events_30d", "feature_events", "actions_30d")),
        )
    return usage


def load_licenses(path: Path) -> list[LicenseSeat]:
    seats: list[LicenseSeat] = []
    for offset, raw in enumerate(load_rows(path), start=2):
        row = clean_row(raw)
        monthly_cost = parse_decimal(first(row, "monthly_cost", "cost_per_month", "mrr"))
        annual_cost = parse_decimal(first(row, "annual_cost", "annual_spend", "yearly_cost"))
        if annual_cost == 0 and monthly_cost:
            annual_cost = monthly_cost * Decimal("12")
        email = normalize_email(first(row, "email", "user_email", "account_email", "login"))
        app = str(first(row, "app", "application", "tool", "vendor")).strip()
        if not email or not app:
            continue
        seats.append(
            LicenseSeat(
                row_number=offset,
                app=app,
                email=email,
                user_name=str(first(row, "user_name", "name", "display_name")).strip(),
                plan=str(first(row, "plan", "tier", "license_type", "sku")).strip(),
                status=normalized_text(first(row, "license_status", "status", "seat_status")),
                role=str(first(row, "role", "permission", "access_level")).strip(),
                annual_cost=annual_cost,
                currency=str(first(row, "currency")).strip().upper() or "USD",
                department=str(first(row, "department", "team")).strip(),
                owner=str(first(row, "owner", "app_owner", "manager")).strip(),
                renewal_date=parse_date(first(row, "renewal_date", "next_renewal", "contract_end")),
                contract_id=str(first(row, "contract_id", "agreement_id", "subscription_id")).strip(),
            )
        )
    if not seats:
        raise SystemExit("No license rows found. Required fields include app and email.")
    return seats


def is_active_license(status: str) -> bool:
    if not status:
        return True
    if status in INACTIVE_LICENSE:
        return False
    if status in ACTIVE_LICENSE:
        return True
    return True


def days_since(value: date | None, today: date) -> int | None:
    if value is None:
        return None
    return (today - value).days


def is_privileged(role: str) -> bool:
    role_key = normalized_text(role)
    return any(word in role_key for word in PRIVILEGED_ROLE_WORDS)


def has_exception_hint(seat: LicenseSeat) -> bool:
    text = normalized_text(f"{seat.email} {seat.user_name} {seat.role} {seat.plan}")
    return any(hint in text for hint in EXCEPTION_HINTS)


def is_premium_plan(plan: str) -> bool:
    plan_key = normalized_text(plan)
    return any(word in plan_key for word in PREMIUM_PLAN_WORDS)


def money(value: Decimal, currency: str) -> str:
    return f"{currency} {value:.2f}"


def choose_action(
    seat: LicenseSeat,
    employee: Employee | None,
    usage: Usage | None,
    duplicate_count: int,
    today: date,
    review_days: int,
    reclaim_days: int,
    high_cost: Decimal,
) -> Finding | None:
    if not is_active_license(seat.status):
        return None

    evidence: list[str] = []
    risk_points = 0
    action = "monitor"
    savings = Decimal("0")
    next_step = "Monitor at the next quarterly license review."

    employee_status = employee.status if employee else ""
    if employee_status in DEPARTED_EMPLOYEE:
        evidence.append("departed_employee_active_license")
        risk_points += 5
        action = "reclaim_now"
        savings = seat.annual_cost
        next_step = "Confirm HR/offboarding record, reclaim seat, and preserve approval evidence."
    elif employee is None:
        evidence.append("missing_hr_match")
        risk_points += 2
        action = "verify_identity_or_owner"
        next_step = "Verify whether this is a contractor, alias, service account, or orphaned paid user."
    elif employee_status and employee_status not in ACTIVE_EMPLOYEE:
        evidence.append(f"employee_status_{employee_status}")
        risk_points += 2
        action = "owner_review"
        next_step = "Confirm employee status and whether the seat should remain assigned."

    inactive_days = days_since(usage.last_login_date, today) if usage else None
    if usage is None:
        evidence.append("missing_usage_export")
        risk_points += 1
        if action == "monitor":
            action = "owner_review"
            next_step = "Ask the app owner for usage evidence before rightsizing."
    else:
        total_activity = usage.activity_count_30d + usage.feature_events_30d
        if usage.last_login_date is None and total_activity == 0:
            evidence.append("never_used_or_no_login")
            risk_points += 3
            if action not in {"reclaim_now"}:
                action = "reclaim_or_downgrade"
                savings = seat.annual_cost
                next_step = "Ask owner to confirm exception status, then reclaim or downgrade."
        elif inactive_days is not None and inactive_days >= reclaim_days:
            evidence.append(f"inactive_{inactive_days}d")
            risk_points += 3
            if action not in {"reclaim_now"}:
                action = "reclaim_or_downgrade"
                savings = seat.annual_cost
                next_step = "Confirm no seasonal or service-account exception, then reclaim or downgrade."
        elif inactive_days is not None and inactive_days >= review_days:
            evidence.append(f"inactive_{inactive_days}d")
            risk_points += 2
            if action == "monitor":
                action = "owner_review"
                next_step = "Ask owner whether this low-activity seat is still needed."

        if is_premium_plan(seat.plan) and total_activity <= 3 and usage.usage_minutes_30d <= 30:
            evidence.append("premium_tier_low_activity")
            risk_points += 2
            if action in {"monitor", "owner_review", "verify_identity_or_owner"}:
                action = "downgrade_review"
                savings = seat.annual_cost / Decimal("2")
                next_step = "Ask owner whether a viewer, basic, or lower tier is sufficient."

    if duplicate_count > 1:
        evidence.append("duplicate_account_same_app")
        risk_points += 3
        if action not in {"reclaim_now"}:
            action = "merge_or_reclaim_duplicate"
            savings = max(savings, seat.annual_cost / Decimal(duplicate_count))
            next_step = "Confirm the primary account, then merge or reclaim duplicate paid seats."

    if is_privileged(seat.role):
        evidence.append("privileged_role")
        if usage and inactive_days is not None and inactive_days >= 30:
            evidence.append("stale_privileged_role")
            risk_points += 4
            if action not in {"reclaim_now"}:
                action = "access_review"
                next_step = "Review privileged access and break-glass coverage before any change."
        else:
            risk_points += 1

    if seat.annual_cost >= high_cost:
        evidence.append("high_cost_seat")
        risk_points += 1

    if has_exception_hint(seat):
        evidence.append("exception_hint")
        if action in {"reclaim_now", "reclaim_or_downgrade"}:
            action = "owner_review"
            savings = Decimal("0")
            next_step = "Confirm service, seasonal, compliance, or break-glass exception before rightsizing."

    if action == "monitor" and not evidence:
        return None

    if risk_points >= 5:
        risk = "high"
    elif risk_points >= 3:
        risk = "medium"
    else:
        risk = "low"

    return Finding(
        seat=seat,
        risk=risk,
        action=action,
        annual_savings=savings,
        evidence=tuple(evidence),
        next_step=next_step,
    )


def render_report(findings: list[Finding], total_seats: int) -> str:
    potential_savings_by_currency: dict[str, Decimal] = {}
    high_risk = 0
    missing_hr = 0
    action_counts: dict[str, int] = {}

    for finding in findings:
        action_counts[finding.action] = action_counts.get(finding.action, 0) + 1
        if finding.risk == "high":
            high_risk += 1
        if "missing_hr_match" in finding.evidence:
            missing_hr += 1
        if finding.annual_savings:
            currency = finding.seat.currency
            potential_savings_by_currency[currency] = (
                potential_savings_by_currency.get(currency, Decimal("0")) + finding.annual_savings
            )

    if any(f.action in {"reclaim_now", "access_review"} and f.risk == "high" for f in findings):
        decision = "Immediate reclaim review"
    elif findings:
        decision = "Owner review needed"
    else:
        decision = "Monitor only"

    savings_text = ", ".join(
        money(amount, currency) for currency, amount in sorted(potential_savings_by_currency.items())
    ) or "USD 0.00"

    lines = [
        "## License Portfolio Decision",
        decision,
        "",
        "## Savings Summary",
        "",
        f"- Potential annual savings: {savings_text}",
        f"- Seats reviewed: {total_seats}",
        f"- Exceptions requiring action: {len(findings)}",
        f"- High-risk seats: {high_risk}",
        f"- Missing HR matches: {missing_hr}",
    ]
    for action, count in sorted(action_counts.items()):
        lines.append(f"- {action}: {count}")

    lines.extend(
        [
            "",
            "## Seat Exceptions",
            "",
            "| Risk | Action | App | Email | Plan | Role | Annual cost | Evidence | Next step |",
            "|---|---|---|---|---|---|---:|---|---|",
        ]
    )
    if findings:
        for finding in sorted(findings, key=lambda item: (item.risk != "high", item.action, item.seat.app, item.seat.email)):
            seat = finding.seat
            lines.append(
                "| {risk} | {action} | {app} | {email} | {plan} | {role} | {cost} | {evidence} | {next_step} |".format(
                    risk=finding.risk,
                    action=finding.action,
                    app=seat.app,
                    email=seat.email,
                    plan=seat.plan or "missing",
                    role=seat.role or "member",
                    cost=money(seat.annual_cost, seat.currency),
                    evidence=", ".join(finding.evidence),
                    next_step=finding.next_step,
                )
            )
    else:
        lines.append("| low | monitor | all | n/a | n/a | n/a | USD 0.00 | no_material_findings | Recheck next review cycle. |")

    lines.extend(["", "## Owner Action Plan", ""])
    if findings:
        for finding in findings:
            lines.append(f"- {finding.seat.app} / {finding.seat.email}: {finding.next_step}")
    else:
        lines.append("- No owner actions required from this fixture.")

    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "- Confirm HR status and app-owner approval before reclaiming or downgrading seats.",
            "- Do not remove executive, legal, audit, compliance, service, seasonal, or break-glass accounts without explicit review.",
            "- Treat savings as planning estimates until contract minimums and renewal timing are confirmed.",
            "- Preserve approval and change evidence outside this script.",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--licenses", required=True, type=Path, help="SaaS license CSV or JSON export.")
    parser.add_argument("--employees", type=Path, help="Optional HR roster CSV or JSON export.")
    parser.add_argument("--usage", type=Path, help="Optional app usage CSV or JSON export.")
    parser.add_argument("--today", default=date.today().isoformat(), help="Review date in YYYY-MM-DD format.")
    parser.add_argument("--review-days", type=int, default=60, help="Days inactive before owner review.")
    parser.add_argument("--reclaim-days", type=int, default=90, help="Days inactive before reclaim/downgrade candidate.")
    parser.add_argument("--high-cost-annual", default="500", help="Annual cost threshold for high-cost evidence.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    today = parse_date(args.today)
    if today is None:
        raise SystemExit("--today must be a valid date in YYYY-MM-DD format.")

    seats = load_licenses(args.licenses)
    employees = load_employees(args.employees)
    usage = load_usage(args.usage)
    high_cost = parse_decimal(args.high_cost_annual)

    duplicate_counts: dict[tuple[str, str], int] = {}
    for seat in seats:
        key = (normalized_text(seat.app), seat.email)
        duplicate_counts[key] = duplicate_counts.get(key, 0) + 1

    findings: list[Finding] = []
    for seat in seats:
        key = (normalized_text(seat.app), seat.email)
        finding = choose_action(
            seat=seat,
            employee=employees.get(seat.email),
            usage=usage.get(key),
            duplicate_count=duplicate_counts[key],
            today=today,
            review_days=args.review_days,
            reclaim_days=args.reclaim_days,
            high_cost=high_cost,
        )
        if finding:
            findings.append(finding)

    print(render_report(findings, total_seats=len(seats)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
