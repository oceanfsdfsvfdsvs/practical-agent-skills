#!/usr/bin/env python3
"""Preflight IRS/state tax notice response packets before live action."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


TRUE_VALUES = {"1", "true", "yes", "y", "present", "included", "signed"}
FALSE_VALUES = {"0", "false", "no", "n", "missing", "absent", ""}
DEFAULT_POLICY = {
    "urgent_days": 10,
    "professional_review_amount": "5000.00",
    "high_risk_notice_terms": [
        "cp3219a",
        "notice of deficiency",
        "tax court",
        "levy",
        "lien",
        "summons",
        "passport",
        "criminal",
        "identity theft",
        "fraud",
    ],
}


@dataclass(frozen=True)
class Notice:
    row_number: int
    notice_id: str
    agency: str
    notice_type: str
    tax_year: str
    notice_date: date | None
    response_due_date: date | None
    amount: Decimal
    issue: str
    taxpayer_agrees: str
    response_form_included: bool
    requested_action: str
    delivery_channel: str
    notes: str


@dataclass(frozen=True)
class Evidence:
    row_number: int
    notice_id: str
    evidence_type: str
    description: str
    present: bool
    evidence_date: date | None
    notes: str


@dataclass(frozen=True)
class Finding:
    notice: Notice
    risk: str
    action: str
    flags: tuple[str, ...]
    next_step: str


def norm(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def parse_bool(value: object) -> bool:
    raw = norm(value)
    if raw in TRUE_VALUES:
        return True
    if raw in FALSE_VALUES:
        return False
    return False


def parse_decimal(value: object) -> Decimal:
    raw = str(value or "").strip().replace(",", "").replace("$", "")
    if not raw:
        return Decimal("0")
    try:
        return Decimal(raw)
    except InvalidOperation:
        return Decimal("0")


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


def money(value: Decimal, currency: str = "USD") -> str:
    return f"{currency} {value:.2f}"


def load_records(path: Path, keys: tuple[str, ...]) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"Input file not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            for key in keys:
                if isinstance(payload.get(key), list):
                    return list(payload[key])
            raise SystemExit(f"JSON input must contain one of: {', '.join(keys)}.")
        if isinstance(payload, list):
            return list(payload)
        raise SystemExit("JSON input must be a list or an object containing rows.")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_policy(path: Path | None) -> dict[str, object]:
    policy = dict(DEFAULT_POLICY)
    if not path:
        return policy
    if not path.exists():
        raise SystemExit(f"Policy file not found: {path}")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise SystemExit("Policy JSON must be an object.")
    policy.update(loaded)
    return policy


def parse_notices(path: Path) -> list[Notice]:
    notices: list[Notice] = []
    for offset, raw in enumerate(load_records(path, ("notices", "rows", "cases")), start=2):
        row = {str(key).strip().lower(): value for key, value in dict(raw).items()}
        notices.append(
            Notice(
                row_number=offset,
                notice_id=str(row.get("notice_id") or row.get("case_id") or row.get("id") or "").strip(),
                agency=str(row.get("agency") or row.get("tax_agency") or "").strip(),
                notice_type=str(row.get("notice_type") or row.get("type") or row.get("letter") or "").strip(),
                tax_year=str(row.get("tax_year") or row.get("period") or "").strip(),
                notice_date=parse_date(row.get("notice_date") or row.get("date")),
                response_due_date=parse_date(
                    row.get("response_due_date") or row.get("deadline") or row.get("due_date")
                ),
                amount=parse_decimal(row.get("amount") or row.get("balance") or row.get("proposed_amount")),
                issue=str(row.get("issue") or row.get("reason") or row.get("description") or "").strip(),
                taxpayer_agrees=norm(row.get("taxpayer_agrees") or row.get("position") or row.get("agrees")),
                response_form_included=parse_bool(row.get("response_form_included") or row.get("response_form")),
                requested_action=str(row.get("requested_action") or row.get("action") or "").strip(),
                delivery_channel=str(row.get("delivery_channel") or row.get("response_method") or "").strip(),
                notes=str(row.get("notes") or row.get("memo") or "").strip(),
            )
        )
    if not notices:
        raise SystemExit("No notice rows found.")
    return notices


def parse_evidence(path: Path | None) -> list[Evidence]:
    if not path:
        return []
    evidence: list[Evidence] = []
    for offset, raw in enumerate(load_records(path, ("evidence", "documents", "rows")), start=2):
        row = {str(key).strip().lower(): value for key, value in dict(raw).items()}
        evidence.append(
            Evidence(
                row_number=offset,
                notice_id=str(row.get("notice_id") or row.get("case_id") or row.get("id") or "").strip(),
                evidence_type=norm(row.get("evidence_type") or row.get("document_type") or row.get("type")),
                description=str(row.get("description") or row.get("document") or "").strip(),
                present=parse_bool(row.get("present") or row.get("available") or row.get("included")),
                evidence_date=parse_date(row.get("date") or row.get("evidence_date")),
                notes=str(row.get("notes") or "").strip(),
            )
        )
    return evidence


def evidence_map(evidence: list[Evidence]) -> dict[str, set[str]]:
    present: dict[str, set[str]] = defaultdict(set)
    for item in evidence:
        if item.present:
            present[item.notice_id].add(item.evidence_type)
    return present


def missing(present: set[str], *required: str) -> list[str]:
    return [item for item in required if item not in present]


def high_risk_terms(policy: dict[str, object]) -> set[str]:
    value = policy.get("high_risk_notice_terms", [])
    if not isinstance(value, list):
        return set()
    return {norm(item) for item in value}


def classify_notice(
    notice: Notice,
    present: set[str],
    today: date,
    policy: dict[str, object],
) -> Finding:
    flags: list[str] = []
    text = " ".join([notice.notice_type, notice.issue, notice.requested_action, notice.notes]).lower()
    urgent_days = int(policy.get("urgent_days", 10))
    professional_amount = parse_decimal(policy.get("professional_review_amount"))

    if notice.response_due_date is None:
        flags.append("response_deadline_missing")
    else:
        days_left = (notice.response_due_date - today).days
        if days_left < 0 or days_left <= urgent_days:
            flags.append("deadline_passed_or_imminent")

    if notice.taxpayer_agrees in {"no", "disagree", "disagrees", "partial", "partly", "unsure", "unknown"}:
        flags.append("taxpayer_disagrees")

    notice_type = norm(notice.notice_type)
    if any(term in text for term in high_risk_terms(policy)) or notice.amount >= professional_amount:
        flags.append("professional_review_recommended")

    if "cp2000" in notice_type or "underreported" in text or "proposed" in text:
        required = ["notice_copy", "income_document", "delivery_proof"]
        if notice.taxpayer_agrees not in {"yes", "agree", "agrees"}:
            required.extend(["cost_basis_support"])
        if missing(present, *required):
            flags.append("cp2000_supporting_documents_missing")
        if not notice.response_form_included or "response_form" not in present:
            flags.append("response_form_or_signature_missing")

    if "cp14" in notice_type or "balance due" in text or "payment mismatch" in text:
        if missing(present, "payment_proof"):
            flags.append("payment_proof_missing")
        if missing(present, "account_status"):
            flags.append("account_status_or_call_log_missing")

    if "cp53e" in notice_type or "direct deposit" in text or "bank" in text:
        if "official_account_status" not in present or "refund" not in text or "qr" in text:
            flags.append("cp53e_authenticity_or_account_status_review")
        if "bank_owner_check" not in present:
            flags.append("direct_deposit_owner_or_account_check_needed")

    if "cp3219a" in notice_type or "notice of deficiency" in text or "tax court" in text:
        flags.append("notice_of_deficiency_or_tax_court_deadline")
        if "prior_response_proof" not in present:
            flags.append("prior_response_proof_missing")
        if "professional_review" not in present:
            flags.append("professional_review_recommended")

    if "identity theft" in text or "fraud" in text:
        if "identity_theft_affidavit" not in present and "professional_review" not in present:
            flags.append("identity_theft_or_fraud_review_needed")

    if not notice.delivery_channel:
        flags.append("response_delivery_channel_missing")

    if "notice_copy" not in present:
        flags.append("notice_copy_missing")

    unique_flags = tuple(dict.fromkeys(flags))
    action = select_action(unique_flags)
    risk = select_risk(unique_flags)
    return Finding(notice=notice, risk=risk, action=action, flags=unique_flags, next_step=next_step_for(action))


def select_action(flags: tuple[str, ...]) -> str:
    if "notice_of_deficiency_or_tax_court_deadline" in flags or "professional_review_recommended" in flags:
        return "professional_review"
    if "deadline_passed_or_imminent" in flags or "response_deadline_missing" in flags:
        return "escalate_deadline"
    if any(flag.startswith("cp53e") for flag in flags) or "direct_deposit_owner_or_account_check_needed" in flags:
        return "verify_authenticity"
    if flags:
        return "repair_evidence_packet"
    return "reply_ready_after_owner_review"


def select_risk(flags: tuple[str, ...]) -> str:
    high_flags = {
        "deadline_passed_or_imminent",
        "notice_of_deficiency_or_tax_court_deadline",
        "professional_review_recommended",
        "cp53e_authenticity_or_account_status_review",
        "identity_theft_or_fraud_review_needed",
    }
    if any(flag in high_flags for flag in flags):
        return "high"
    if flags:
        return "medium"
    return "low"


def next_step_for(action: str) -> str:
    return {
        "professional_review": "Route to taxpayer or authorized tax professional before sending a substantive response.",
        "escalate_deadline": "Confirm deadline, request more time or status if available, and preserve all delivery proof.",
        "verify_authenticity": "Navigate directly to the official agency account or phone number on the notice before sensitive action.",
        "repair_evidence_packet": "Add missing evidence, signed forms, delivery proof, and account/payment status before replying.",
        "reply_ready_after_owner_review": "Owner should review the packet, sign if required, and preserve delivery confirmation.",
    }[action]


def render_report(notices: list[Notice], findings: list[Finding]) -> str:
    counts = Counter(f.risk for f in findings)
    blockers = sum(1 for f in findings if f.flags)
    evidence_blockers = sum(1 for f in findings if any("missing" in flag or "proof" in flag for flag in f.flags))
    professional = sum(1 for f in findings if f.action == "professional_review")
    if any(f.action == "professional_review" for f in findings):
        decision = "Hold response pending evidence repair and professional review."
    elif any(f.action == "escalate_deadline" for f in findings):
        decision = "Deadline escalation before response."
    elif any(f.action == "verify_authenticity" for f in findings):
        decision = "Authenticity check needed before sensitive action."
    elif any(f.flags for f in findings):
        decision = "Hold response pending evidence repair."
    else:
        decision = "Reply-ready after owner review."

    lines = [
        "## Tax Notice Response Decision",
        decision,
        "",
        "## Notice Summary",
        f"- Notices reviewed: {len(notices)}",
        f"- High risk: {counts.get('high', 0)}",
        f"- Medium risk: {counts.get('medium', 0)}",
        f"- Low risk: {counts.get('low', 0)}",
        f"- Deadline/action blockers: {blockers}",
        f"- Evidence blockers: {evidence_blockers}",
        f"- Professional-review flags: {professional}",
        "",
        "## Response Findings",
        "| Risk | Action | Notice | Agency | Type | Tax year | Due date | Amount | Flags | Next step |",
        "|---|---|---|---|---|---:|---|---:|---|---|",
    ]
    for finding in sorted(findings, key=lambda item: ({"high": 0, "medium": 1, "low": 2}[item.risk], item.notice.notice_id)):
        notice = finding.notice
        due = notice.response_due_date.isoformat() if notice.response_due_date else "missing"
        flags = ", ".join(finding.flags) if finding.flags else "none"
        lines.append(
            "| {risk} | {action} | {notice_id} | {agency} | {notice_type} | {tax_year} | {due} | {amount} | {flags} | {next_step} |".format(
                risk=finding.risk,
                action=finding.action,
                notice_id=notice.notice_id or f"row {notice.row_number}",
                agency=notice.agency or "unknown",
                notice_type=notice.notice_type or "unknown",
                tax_year=notice.tax_year or "unknown",
                due=due,
                amount=money(notice.amount),
                flags=flags,
                next_step=finding.next_step,
            )
        )

    lines.extend(
        [
            "",
            "## Packet Checklist",
            "- Notice copy and envelope if deadline/postmark matters.",
            "- Response form, signed and dated when required.",
            "- Plain-language agree/disagree/partial/unsure statement.",
            "- Evidence mapped to every disputed line.",
            "- Payment proof or refund/account status when money already moved.",
            "- Authorization form if someone else will contact the agency.",
            "- Upload, fax, mail, or call proof plus follow-up date.",
            "",
            "## Guardrails",
            "- This report is administrative workflow support, not tax, legal, accounting, investment, identity-theft recovery, or representation advice.",
            "- Do not submit, upload, fax, mail, pay, call, or update bank details unless the taxpayer explicitly authorizes the live action.",
            "- Redact SSNs, full EINs, bank account numbers, IRS online-account credentials, full transcripts, tokens, and secrets.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notices", required=True, type=Path, help="CSV or JSON notice summary input.")
    parser.add_argument("--evidence", type=Path, help="CSV or JSON evidence inventory input.")
    parser.add_argument("--policy", type=Path, help="Optional JSON policy thresholds.")
    parser.add_argument("--today", help="Review date in YYYY-MM-DD format. Defaults to current local date.")
    parser.add_argument("--output", type=Path, help="Optional path for the Markdown report.")
    args = parser.parse_args(argv)

    today = parse_date(args.today) if args.today else date.today()
    if today is None:
        raise SystemExit("--today must be YYYY-MM-DD.")

    policy = load_policy(args.policy)
    notices = parse_notices(args.notices)
    evidence = parse_evidence(args.evidence)
    present_by_notice = evidence_map(evidence)
    findings = [classify_notice(notice, present_by_notice.get(notice.notice_id, set()), today, policy) for notice in notices]
    report = render_report(notices, findings)
    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
    print(report)
    return 2 if any(f.flags for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
