#!/usr/bin/env python3
"""Preflight rental security deposit disputes before demand letters or small claims."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


EVIDENCE_KEYWORDS = {
    "lease": ("lease", "rental-agreement", "agreement"),
    "deposit_receipt": ("deposit", "receipt", "ledger"),
    "move_in_condition": ("move-in", "movein", "condition", "initial-inspection"),
    "move_out_condition": ("move-out", "moveout", "photo", "video", "walkthrough"),
    "itemized_statement": ("itemized", "deduction", "statement"),
    "receipts_estimates": ("receipt", "invoice", "estimate", "quote"),
    "forwarding_address": ("forwarding", "address"),
    "demand_letter": ("demand", "letter"),
    "communications": ("email", "message", "text", "communication"),
}

NORMAL_WEAR_HINTS = (
    "paint",
    "painting",
    "repaint",
    "nail",
    "scuff",
    "minor",
    "clean",
    "cleaning",
    "carpet cleaning",
    "routine",
    "turnover",
    "wear",
    "tear",
)

SENSITIVE_FILENAME = re.compile(
    r"(token|secret|api[-_ ]?key|private[-_ ]?key|password|full[-_ ]?card|cvv|ssn|passport|driver[-_ ]?license)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class DepositCase:
    row_number: int
    case_id: str
    state: str
    city: str
    monthly_rent: Decimal
    deposit_amount: Decimal
    amount_withheld: Decimal
    move_out_date: date | None
    keys_returned_date: date | None
    itemized_statement_date: date | None
    refund_date: date | None
    fields: dict[str, str]


def parse_date(value: str) -> date | None:
    value = value.strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"invalid date '{value}', expected YYYY-MM-DD")


def parse_decimal(value: str) -> Decimal:
    value = value.strip().replace(",", "")
    if not value:
        return Decimal("0")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid money value '{value}'") from exc


def money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01'))} USD"


def truthy(value: str) -> bool:
    return value.strip().lower() in {"yes", "y", "true", "1", "present", "available", "attached", "sent"}


def read_cases(path: Path) -> list[DepositCase]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        cases: list[DepositCase] = []
        for index, raw in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw.items() if key}
            case_id = row.get("case_id") or f"row-{index}"
            cases.append(
                DepositCase(
                    row_number=index,
                    case_id=case_id,
                    state=row.get("state", "").upper(),
                    city=row.get("city", ""),
                    monthly_rent=parse_decimal(row.get("monthly_rent", "")),
                    deposit_amount=parse_decimal(row.get("deposit_amount", "")),
                    amount_withheld=parse_decimal(row.get("amount_withheld", "")),
                    move_out_date=parse_date(row.get("move_out_date", "")),
                    keys_returned_date=parse_date(row.get("keys_returned_date", "")),
                    itemized_statement_date=parse_date(row.get("itemized_statement_date", "")),
                    refund_date=parse_date(row.get("refund_date", "")),
                    fields=row,
                )
            )
        return cases


def read_rules(path: Path) -> dict[str, dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        raise ValueError("rules file must contain a JSON object keyed by state code")
    return {str(key).upper(): value for key, value in raw.items() if isinstance(value, dict)}


def evidence_index(evidence_dir: Path) -> dict[str, list[Path]]:
    files: dict[str, list[Path]] = {}
    if not evidence_dir.exists():
        return files
    for path in evidence_dir.rglob("*"):
        if path.is_file():
            files.setdefault(path.name.lower(), []).append(path)
    return files


def evidence_present(case: DepositCase, evidence: dict[str, list[Path]], evidence_type: str) -> tuple[bool, list[str]]:
    field_name = {
        "move_in_condition": "move_in_condition_record",
        "move_out_condition": "move_out_photos",
        "deposit_receipt": "deposit_receipt_uploaded",
        "receipts_estimates": "landlord_receipts_provided",
        "itemized_statement": "itemized_statement_date",
        "demand_letter": "demand_letter_sent",
    }.get(evidence_type, evidence_type)

    if evidence_type == "forwarding_address" and truthy(case.fields.get("forwarding_address_sent", "")):
        return True, ["csv:forwarding_address_sent"]
    if case.fields.get(field_name) and (truthy(case.fields.get(field_name, "")) or evidence_type == "itemized_statement"):
        return True, [f"csv:{field_name}"]

    case_key = case.case_id.lower()
    keywords = EVIDENCE_KEYWORDS[evidence_type]
    hits: list[str] = []
    for name, paths in evidence.items():
        if case_key in name and any(keyword in name for keyword in keywords):
            hits.extend(str(path) for path in paths)
    return bool(hits), hits[:3]


def trigger_date(case: DepositCase) -> date | None:
    dates = [value for value in (case.move_out_date, case.keys_returned_date) if value]
    if not dates:
        return None
    return max(dates)


def deadline_for(case: DepositCase, rule: dict[str, Any]) -> date | None:
    start = trigger_date(case)
    days = rule.get("deadline_days")
    if start is None or not isinstance(days, int):
        return None
    return start + timedelta(days=days)


def split_deductions(value: str) -> list[str]:
    return [item.strip().lower() for item in re.split(r"[;\n|]+", value or "") if item.strip()]


def evaluate(case: DepositCase, rules: dict[str, dict[str, Any]], evidence: dict[str, list[Path]], today: date) -> tuple[str, list[str], list[str], date | None]:
    blockers: list[str] = []
    reviews: list[str] = []
    rule = rules.get(case.state, {})
    deadline = deadline_for(case, rule)

    if not case.state:
        blockers.append("missing_jurisdiction")
    elif not rule:
        reviews.append("state_rule_not_in_fixture_verify_locally")

    if trigger_date(case) is None:
        blockers.append("missing_move_out_or_key_return_date")
    elif deadline is None:
        reviews.append("deadline_rule_unverified")
    elif today > deadline:
        if case.amount_withheld > 0 and case.itemized_statement_date is None:
            blockers.append("missing_itemized_statement")
        if case.refund_date is None and case.amount_withheld < case.deposit_amount:
            blockers.append("refund_status_missing_after_deadline")

    if deadline and case.itemized_statement_date and case.itemized_statement_date > deadline:
        blockers.append("late_itemized_statement")

    if case.amount_withheld > 0 and rule.get("itemization_required_if_withheld", True):
        present, _ = evidence_present(case, evidence, "itemized_statement")
        if not present:
            blockers.append("missing_itemized_statement")

    if rule.get("forwarding_address_required") and not evidence_present(case, evidence, "forwarding_address")[0]:
        blockers.append("forwarding_address_proof_missing")

    required_evidence = ["lease", "deposit_receipt", "move_in_condition", "move_out_condition"]
    for evidence_type in required_evidence:
        present, _ = evidence_present(case, evidence, evidence_type)
        if not present:
            if evidence_type == "move_out_condition":
                blockers.append("missing_move_out_condition_evidence")
            else:
                reviews.append(f"{evidence_type}_missing")

    deductions = split_deductions(case.fields.get("deductions", ""))
    if case.amount_withheld > 0 and deductions:
        if any(any(hint in deduction for hint in NORMAL_WEAR_HINTS) for deduction in deductions):
            reviews.append("normal_wear_tear_deduction_review")
        if not evidence_present(case, evidence, "receipts_estimates")[0]:
            blockers.append("deduction_receipts_or_estimates_missing")
    elif case.amount_withheld > 0:
        blockers.append("deduction_rows_missing")

    if case.deposit_amount and case.monthly_rent and isinstance(rule.get("deposit_cap_months"), (int, float)):
        cap = case.monthly_rent * Decimal(str(rule["deposit_cap_months"]))
        if case.deposit_amount > cap:
            reviews.append("deposit_amount_exceeds_sample_cap_verify_locally")

    if rule.get("pre_move_out_inspection_material") and not truthy(case.fields.get("pre_move_out_inspection_requested", "")):
        reviews.append("pre_move_out_inspection_not_documented")

    if truthy(case.fields.get("live_portal_action_requested", "")):
        blockers.append("live_action_requested")

    sensitive_hits = [
        name for name in evidence if case.case_id.lower() in name and SENSITIVE_FILENAME.search(name)
    ]
    if sensitive_hits:
        blockers.append("sensitive_file_redaction_required")

    if blockers:
        decision = "Hold dispute packet pending evidence repair"
    elif reviews:
        decision = "Review before escalation"
    else:
        decision = "Ready for owner review"
    return decision, sorted(set(blockers)), sorted(set(reviews)), deadline


def build_report(cases: list[DepositCase], rules: dict[str, dict[str, Any]], evidence: dict[str, list[Path]], today: date) -> tuple[str, bool]:
    lines = ["# Security Deposit Dispute Preflight Report", "", f"Run date: {today.isoformat()}", ""]
    any_blocker = False
    summary: dict[str, int] = {}
    details: list[tuple[DepositCase, str, list[str], list[str], date | None]] = []

    for case in cases:
        decision, blockers, reviews, deadline = evaluate(case, rules, evidence, today)
        summary[decision] = summary.get(decision, 0) + 1
        any_blocker = any_blocker or bool(blockers)
        details.append((case, decision, blockers, reviews, deadline))

    if any_blocker:
        overall = "Hold dispute packet pending evidence repair"
    elif any("Review" in decision for _, decision, _, _, _ in details):
        overall = "Review before escalation"
    else:
        overall = "Ready for owner review"

    lines.extend(["## Security Deposit Dispute Decision", overall, ""])
    lines.extend(["## Decision Counts", "| Decision | Count |", "|---|---:|"])
    for decision, count in sorted(summary.items()):
        lines.append(f"| {decision} | {count} |")
    lines.append("")

    lines.extend(["## Case Summary", "| Case | State | Deposit | Withheld | Deadline | Decision |", "|---|---|---:|---:|---|---|"])
    for case, decision, _, _, deadline in details:
        lines.append(
            f"| {case.case_id} | {case.state or 'unknown'} | {money(case.deposit_amount)} | "
            f"{money(case.amount_withheld)} | {deadline.isoformat() if deadline else 'unverified'} | {decision} |"
        )
    lines.append("")

    lines.extend(["## Evidence Matrix", "| Case | Evidence | Status | Source | Repair action |", "|---|---|---|---|---|"])
    for case, _, _, _, _ in details:
        for evidence_type in EVIDENCE_KEYWORDS:
            present, sources = evidence_present(case, evidence, evidence_type)
            status = "present" if present else "missing_or_unverified"
            source = "; ".join(sources) if sources else "-"
            action = "Attach or cite this evidence before escalation." if not present else "Keep with the packet."
            lines.append(f"| {case.case_id} | {evidence_type} | {status} | {source} | {action} |")
    lines.append("")

    lines.extend(["## Blockers", "| Case | Blocker | Why it matters | Next action |", "|---|---|---|---|"])
    blocker_rows = 0
    for case, _, blockers, _, _ in details:
        for blocker in blockers:
            blocker_rows += 1
            lines.append(f"| {case.case_id} | {blocker} | May weaken or block a demand/complaint packet. | Repair evidence, verify local rule, or get owner acceptance before escalation. |")
    if blocker_rows == 0:
        lines.append("| - | None | No blocking gaps found by the local fixture rules. | Owner review still required. |")
    lines.append("")

    lines.extend(["## Review Flags", "| Case | Flag | Why it matters | Next action |", "|---|---|---|---|"])
    review_rows = 0
    for case, _, _, reviews, _ in details:
        for review in reviews:
            review_rows += 1
            lines.append(f"| {case.case_id} | {review} | Needs human or jurisdiction-specific review. | Add support or mark as verify-locally before sending. |")
    if review_rows == 0:
        lines.append("| - | None | No review flags found by the local fixture rules. | Owner review still required. |")
    lines.append("")

    lines.extend(
        [
            "## Demand Packet Notes",
            "- Use dates, amounts, itemized lines, and attachment names; avoid threats or unsupported accusations.",
            "- Verify state and city rules before sending a legal demand or filing in small claims.",
            "- Do not upload full SSNs, bank details, full IDs, credentials, private keys, or unrelated records.",
        ]
    )
    return "\n".join(lines) + "\n", any_blocker


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", required=True, type=Path, help="CSV of deposit dispute cases")
    parser.add_argument("--rules", required=True, type=Path, help="JSON state rules file")
    parser.add_argument("--evidence-dir", required=True, type=Path, help="Directory of local evidence files")
    parser.add_argument("--today", type=parse_date, default=date.today(), help="Run date in YYYY-MM-DD format")
    parser.add_argument("--output", type=Path, help="Optional path for the Markdown report")
    args = parser.parse_args()

    cases = read_cases(args.cases)
    rules = read_rules(args.rules)
    evidence = evidence_index(args.evidence_dir)
    report, has_blockers = build_report(cases, rules, evidence, args.today)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 2 if has_blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
