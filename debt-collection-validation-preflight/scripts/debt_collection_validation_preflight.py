#!/usr/bin/env python3
"""Preflight debt collection validation packets before responding to collectors."""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path


EVIDENCE_KEYWORDS = {
    "collection_notice": ("notice", "letter", "envelope", "collector"),
    "mailing_proof": ("certified", "mailing", "tracking", "postal", "delivery", "portal-confirmation"),
    "payment_or_settlement": ("payment", "paid", "settlement", "receipt", "cancelled-check", "zero-balance"),
    "identity_or_mismatch": ("identity", "idtheft", "fraud", "mismatch", "not-mine", "address-proof"),
    "itemization_or_billing": ("itemization", "statement", "eob", "bill", "invoice", "ledger"),
    "verification_response": ("verification", "validation-response", "collector-response", "original-creditor"),
    "post_dispute_collection": ("post-dispute", "continued", "demand", "credit-reporting", "call-log"),
    "court_or_lawsuit": ("summons", "complaint", "court", "lawsuit", "arbitration"),
}

ISSUE_ALIASES = {
    "unknown": "unknown_debt",
    "unknown debt": "unknown_debt",
    "unknown_debt": "unknown_debt",
    "not mine": "not_mine",
    "not_mine": "not_mine",
    "identity theft": "identity_theft",
    "identity_theft": "identity_theft",
    "fraud": "identity_theft",
    "paid": "paid_or_settled",
    "settled": "paid_or_settled",
    "paid_or_settled": "paid_or_settled",
    "wrong amount": "wrong_amount",
    "wrong_amount": "wrong_amount",
    "old": "old_debt",
    "old debt": "old_debt",
    "old_debt": "old_debt",
    "medical": "medical_collection",
    "medical_collection": "medical_collection",
    "original creditor": "original_creditor_request",
    "original_creditor_request": "original_creditor_request",
    "continued collection": "continued_collection_after_dispute",
    "continued_collection_after_dispute": "continued_collection_after_dispute",
}

VALID_ISSUES = set(ISSUE_ALIASES.values()) | {"mixed"}

SENSITIVE_FILENAME = re.compile(
    r"(token|secret|api[-_ ]?key|private[-_ ]?key|password|full[-_ ]?card|cvv|ssn|passport|driver[-_ ]?license|bank[-_ ]?login)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CollectionCase:
    row_number: int
    case_id: str
    collector_name: str
    collector_address: str
    current_creditor: str
    original_creditor: str
    masked_account: str
    first_contact_date: date | None
    validation_notice_date: date | None
    received_date: date | None
    dispute_sent_date: date | None
    verification_received_date: date | None
    debt_type: str
    issue_type: str
    amount_claimed: Decimal
    itemization_date: date | None
    last_payment_date: date | None
    has_validation_notice: bool
    dispute_instructions_present: bool
    original_creditor_requested: bool
    collection_continued_after_dispute: bool
    credit_reporting_threat: bool
    lawsuit_or_court_deadline: bool
    payment_requested: bool
    live_action_requested: bool
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


def truthy(value: str) -> bool:
    return value.strip().lower() in {"yes", "y", "true", "1", "present", "available", "attached", "sent"}


def normalize_issue(value: str) -> str:
    cleaned = value.strip().lower().replace("-", "_")
    return ISSUE_ALIASES.get(cleaned, cleaned)


def read_cases(path: Path) -> list[CollectionCase]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        cases: list[CollectionCase] = []
        for index, raw in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw.items() if key}
            cases.append(
                CollectionCase(
                    row_number=index,
                    case_id=row.get("case_id") or f"row-{index}",
                    collector_name=row.get("collector_name", ""),
                    collector_address=row.get("collector_address", ""),
                    current_creditor=row.get("current_creditor", ""),
                    original_creditor=row.get("original_creditor", ""),
                    masked_account=row.get("masked_account", ""),
                    first_contact_date=parse_date(row.get("first_contact_date", "")),
                    validation_notice_date=parse_date(row.get("validation_notice_date", "")),
                    received_date=parse_date(row.get("received_date", "")),
                    dispute_sent_date=parse_date(row.get("dispute_sent_date", "")),
                    verification_received_date=parse_date(row.get("verification_received_date", "")),
                    debt_type=row.get("debt_type", ""),
                    issue_type=normalize_issue(row.get("issue_type", "")),
                    amount_claimed=parse_decimal(row.get("amount_claimed", "")),
                    itemization_date=parse_date(row.get("itemization_date", "")),
                    last_payment_date=parse_date(row.get("last_payment_date", "")),
                    has_validation_notice=truthy(row.get("has_validation_notice", "")),
                    dispute_instructions_present=truthy(row.get("dispute_instructions_present", "")),
                    original_creditor_requested=truthy(row.get("original_creditor_requested", "")),
                    collection_continued_after_dispute=truthy(row.get("collection_continued_after_dispute", "")),
                    credit_reporting_threat=truthy(row.get("credit_reporting_threat", "")),
                    lawsuit_or_court_deadline=truthy(row.get("lawsuit_or_court_deadline", "")),
                    payment_requested=truthy(row.get("payment_requested", "")),
                    live_action_requested=truthy(row.get("live_action_requested", "")),
                    fields=row,
                )
            )
        return cases


def evidence_index(evidence_dir: Path) -> dict[str, list[Path]]:
    files: dict[str, list[Path]] = {}
    if not evidence_dir.exists():
        return files
    for path in evidence_dir.rglob("*"):
        if path.is_file():
            files.setdefault(path.name.lower(), []).append(path)
    return files


def evidence_present(case: CollectionCase, evidence: dict[str, list[Path]], evidence_type: str) -> tuple[bool, list[str]]:
    field_name = {
        "collection_notice": "collection_notice",
        "mailing_proof": "mailing_proof",
        "payment_or_settlement": "payment_or_settlement",
        "identity_or_mismatch": "identity_or_mismatch",
        "itemization_or_billing": "itemization_or_billing",
        "verification_response": "verification_response",
        "post_dispute_collection": "post_dispute_collection",
        "court_or_lawsuit": "court_or_lawsuit",
    }[evidence_type]
    if truthy(case.fields.get(field_name, "")):
        return True, [f"csv:{field_name}"]

    case_key = case.case_id.lower()
    keywords = EVIDENCE_KEYWORDS[evidence_type]
    hits: list[str] = []
    for name, paths in evidence.items():
        name_without_case = name.replace(case_key, "")
        if case_key in name and any(keyword in name_without_case for keyword in keywords):
            hits.extend(str(path) for path in paths)
    return bool(hits), hits[:3]


def sensitive_hits(evidence: dict[str, list[Path]]) -> list[str]:
    hits: list[str] = []
    for paths in evidence.values():
        for path in paths:
            if SENSITIVE_FILENAME.search(path.name):
                hits.append(str(path))
    return sorted(hits)


def validation_due(case: CollectionCase) -> date | None:
    anchor = case.received_date or case.validation_notice_date
    if not anchor:
        return None
    return anchor + timedelta(days=30)


def required_evidence_types(case: CollectionCase) -> list[str]:
    required = ["collection_notice"]
    if case.dispute_sent_date:
        required.append("mailing_proof")
    if case.issue_type in {"not_mine", "identity_theft"}:
        required.append("identity_or_mismatch")
    if case.issue_type in {"paid_or_settled"}:
        required.append("payment_or_settlement")
    if case.issue_type in {"wrong_amount", "medical_collection"}:
        required.append("itemization_or_billing")
    if case.collection_continued_after_dispute:
        required.extend(["mailing_proof", "post_dispute_collection"])
    if case.verification_received_date:
        required.append("verification_response")
    if case.lawsuit_or_court_deadline:
        required.append("court_or_lawsuit")
    return list(dict.fromkeys(required))


def evaluate(case: CollectionCase, evidence: dict[str, list[Path]], today: date) -> tuple[str, list[str], list[str]]:
    blockers: list[str] = []
    reviews: list[str] = []

    if not case.collector_name or not case.collector_address:
        blockers.append("collector_identity_or_address_missing")
    if not case.current_creditor:
        blockers.append("current_creditor_missing")
    if case.amount_claimed <= Decimal("0"):
        blockers.append("amount_missing_or_invalid")
    if not case.issue_type:
        blockers.append("missing_issue_type")
    elif case.issue_type not in VALID_ISSUES:
        reviews.append("unrecognized_issue_type_verify_before_send")

    if not case.has_validation_notice:
        blockers.append("validation_notice_missing")
    else:
        if not case.dispute_instructions_present:
            blockers.append("dispute_instructions_missing")
        if not case.itemization_date and case.issue_type in {"wrong_amount", "medical_collection", "unknown_debt", "mixed"}:
            reviews.append("itemization_date_or_amount_basis_missing")

    due = validation_due(case)
    if case.has_validation_notice and due:
        days_left = (due - today).days
        if not case.dispute_sent_date:
            if days_left < 0:
                reviews.append("validation_period_likely_missed_verify_options")
            elif days_left <= 7:
                blockers.append("timely_dispute_window_at_risk")
            else:
                reviews.append("written_dispute_not_yet_sent")
        elif case.dispute_sent_date > due:
            reviews.append("dispute_sent_after_validation_period")
    elif case.has_validation_notice:
        reviews.append("received_date_missing_cannot_compute_validation_window")

    for evidence_type in required_evidence_types(case):
        present, _ = evidence_present(case, evidence, evidence_type)
        if present:
            continue
        if evidence_type == "collection_notice":
            blockers.append("collection_notice_file_missing")
        elif evidence_type == "mailing_proof":
            blockers.append("written_dispute_mailing_proof_missing")
        elif evidence_type == "payment_or_settlement":
            blockers.append("payment_or_settlement_proof_missing")
        elif evidence_type == "identity_or_mismatch":
            blockers.append("identity_or_not_mine_evidence_missing")
        elif evidence_type == "itemization_or_billing":
            blockers.append("amount_itemization_or_billing_evidence_missing")
        elif evidence_type == "verification_response":
            reviews.append("verification_response_file_missing")
        elif evidence_type == "post_dispute_collection":
            blockers.append("post_dispute_collection_evidence_missing")
        elif evidence_type == "court_or_lawsuit":
            blockers.append("court_or_lawsuit_documents_missing")

    if case.collection_continued_after_dispute and case.dispute_sent_date and not case.verification_received_date:
        blockers.append("collection_after_timely_dispute_without_verification")

    if case.original_creditor_requested and not case.original_creditor:
        reviews.append("original_creditor_response_missing")

    if case.issue_type == "old_debt":
        if not case.last_payment_date:
            blockers.append("last_payment_or_charge_date_missing")
        reviews.append("time_barred_debt_review_no_admission_or_payment")

    if case.lawsuit_or_court_deadline:
        blockers.append("legal_deadline_owner_review_required")
    if case.credit_reporting_threat:
        reviews.append("credit_reporting_threat_review")
    if case.payment_requested and case.issue_type in {"unknown_debt", "old_debt", "not_mine", "identity_theft", "wrong_amount"}:
        reviews.append("payment_request_do_not_admit_or_pay_without_owner_review")
    if case.live_action_requested:
        blockers.append("live_action_requested")

    if blockers:
        return "hold", sorted(set(blockers)), sorted(set(reviews))
    if reviews:
        return "review", [], sorted(set(reviews))
    return "ready", [], []


BLOCKER_HELP = {
    "collector_identity_or_address_missing": ("A durable written request needs a known collector and mailing route.", "Add full collector name and mailing address from the notice."),
    "current_creditor_missing": ("The user cannot tell what account is being collected.", "Attach or transcribe the current creditor field from the validation notice."),
    "amount_missing_or_invalid": ("A validation request must identify the claimed amount.", "Add the claimed amount from the notice or itemization."),
    "missing_issue_type": ("The packet needs a clear dispute or request theory.", "Classify the case as unknown, not mine, paid, wrong amount, old debt, or mixed."),
    "validation_notice_missing": ("The notice is the anchor for rights, dates, and requested validation.", "Attach the validation notice or document that no notice was received."),
    "dispute_instructions_missing": ("The packet may be missing required response instructions.", "Ask for the page showing dispute instructions or collector reply method."),
    "timely_dispute_window_at_risk": ("The 30-day validation period is close.", "Prepare a dated written dispute and mailing proof plan now."),
    "collection_notice_file_missing": ("The packet needs the actual collection contact.", "Attach the letter, envelope, text, email, or call log."),
    "written_dispute_mailing_proof_missing": ("Continued-collection review depends on proving the written dispute was sent.", "Attach certified mail, tracking, portal receipt, or equivalent proof."),
    "payment_or_settlement_proof_missing": ("Paid or settled claims need account-tied proof.", "Attach settlement letter, receipt, canceled check, or creditor acknowledgment."),
    "identity_or_not_mine_evidence_missing": ("Not-mine claims need more than a denial.", "Attach identity-theft report, account mismatch proof, or credit-report evidence."),
    "amount_itemization_or_billing_evidence_missing": ("Wrong-amount claims need a basis for recalculation.", "Attach itemization, statement, EOB, invoice, or ledger."),
    "post_dispute_collection_evidence_missing": ("The later collection activity must be shown.", "Attach post-dispute demand, call log, credit-reporting notice, or lawsuit threat."),
    "court_or_lawsuit_documents_missing": ("Court deadlines cannot be assessed from notes alone.", "Attach summons, complaint, arbitration notice, or court docket date."),
    "collection_after_timely_dispute_without_verification": ("Collection may need owner/legal review when no verification was provided.", "Separate the dispute proof, later collector activity, and lack of verification."),
    "last_payment_or_charge_date_missing": ("Old-debt analysis depends on date facts.", "Add last payment, last charge, charge-off, and state for owner/legal review."),
    "legal_deadline_owner_review_required": ("A lawsuit or court deadline is not handled by a validation letter alone.", "Route to legal owner review and preserve response deadlines."),
    "live_action_requested": ("The skill must not make live calls, payments, complaints, or filings.", "Prepare local packet only; user/owner decides live action."),
}

REVIEW_HELP = {
    "unrecognized_issue_type_verify_before_send": ("Issue type is outside the known matrix.", "Use a supported label or explain the mixed theory."),
    "itemization_date_or_amount_basis_missing": ("The amount may be hard to verify.", "Ask for itemization date, statements, or balance basis."),
    "validation_period_likely_missed_verify_options": ("The strongest written-dispute window may have passed.", "Mark current options as owner/legal review, not guaranteed rights."),
    "written_dispute_not_yet_sent": ("No written response has been sent yet.", "Draft a concise validation/dispute request if facts support it."),
    "dispute_sent_after_validation_period": ("Late disputes may not trigger the same protections.", "Verify options before relying on stop-collection rules."),
    "received_date_missing_cannot_compute_validation_window": ("The due date cannot be computed reliably.", "Add envelope, delivery, or received date."),
    "verification_response_file_missing": ("Verification was marked received but not attached.", "Attach the collector response or mark as unavailable."),
    "original_creditor_response_missing": ("Original-creditor request lacks a response.", "Track the request and attach the response when received."),
    "time_barred_debt_review_no_admission_or_payment": ("Old-debt facts can affect legal risk.", "Avoid admissions or payment promises until owner/legal review."),
    "credit_reporting_threat_review": ("Credit reporting threats may change escalation priority.", "Attach any credit-report page or collector threat language."),
    "payment_request_do_not_admit_or_pay_without_owner_review": ("Payment can change strategy or rights.", "Keep drafts factual and avoid admissions."),
}


def format_date(value: date | None) -> str:
    return value.isoformat() if value else ""


def render_report(cases: list[CollectionCase], evidence: dict[str, list[Path]], today: date) -> tuple[str, int]:
    evaluations = [(case, *evaluate(case, evidence, today)) for case in cases]
    any_hold = any(decision == "hold" for _, decision, _, _ in evaluations)
    any_review = any(decision == "review" for _, decision, _, _ in evaluations)
    decision_text = (
        "Hold validation packet pending evidence repair"
        if any_hold
        else "Review before send"
        if any_review
        else "Ready for owner review"
    )

    lines: list[str] = [
        f"Run date: {today.isoformat()}",
        "",
        "## Debt Collection Validation Decision",
        decision_text,
        "",
        "## Case Summary",
        "| Case | Collector | Current Creditor | Issue Type | Decision |",
        "|---|---|---|---|---|",
    ]
    for case, decision, _, _ in evaluations:
        lines.append(f"| {case.case_id} | {case.collector_name or 'MISSING'} | {case.current_creditor or 'MISSING'} | {case.issue_type or 'MISSING'} | {decision} |")

    lines.extend(
        [
            "",
            "## Timeline",
            "| Case | First Contact | Notice Received | Dispute Due | Dispute Sent | Status |",
            "|---|---|---|---|---|---|",
        ]
    )
    for case, _, _, _ in evaluations:
        due = validation_due(case)
        if not case.has_validation_notice:
            status = "validation notice missing"
        elif due and case.dispute_sent_date and case.dispute_sent_date <= due:
            status = "timely written dispute sent"
        elif due and not case.dispute_sent_date and due < today:
            status = "validation period likely missed"
        elif due and not case.dispute_sent_date:
            status = f"{(due - today).days} day(s) left"
        else:
            status = "date incomplete"
        lines.append(
            f"| {case.case_id} | {format_date(case.first_contact_date)} | {format_date(case.received_date)} | {format_date(due)} | {format_date(case.dispute_sent_date)} | {status} |"
        )

    lines.extend(
        [
            "",
            "## Evidence Matrix",
            "| Case | Evidence | Status | Source | Repair action |",
            "|---|---|---|---|---|",
        ]
    )
    for case, _, _, _ in evaluations:
        for evidence_type in required_evidence_types(case):
            present, sources = evidence_present(case, evidence, evidence_type)
            status = "present" if present else "missing"
            source = ", ".join(sources) if sources else ""
            repair = "Keep attached and label clearly." if present else f"Add {evidence_type.replace('_', ' ')}."
            lines.append(f"| {case.case_id} | {evidence_type} | {status} | {source} | {repair} |")

    lines.extend(["", "## Blockers", "| Case | Blocker | Why it matters | Next action |", "|---|---|---|---|"])
    blocker_count = 0
    for case, _, blockers, _ in evaluations:
        for blocker in blockers:
            why, action = BLOCKER_HELP.get(blocker, ("This issue can make the packet unreliable.", "Repair before sending."))
            lines.append(f"| {case.case_id} | {blocker} | {why} | {action} |")
            blocker_count += 1
    if blocker_count == 0:
        lines.append("| - | - | No blockers detected. | - |")

    lines.extend(["", "## Review Flags", "| Case | Flag | Why it matters | Next action |", "|---|---|---|---|"])
    review_count = 0
    for case, _, _, reviews in evaluations:
        for review in reviews:
            why, action = REVIEW_HELP.get(review, ("This issue needs owner judgment.", "Verify before sending."))
            lines.append(f"| {case.case_id} | {review} | {why} | {action} |")
            review_count += 1
    if review_count == 0:
        lines.append("| - | - | No review flags detected. | - |")

    sensitive = sensitive_hits(evidence)
    if sensitive:
        lines.extend(["", "## Sensitive Filename Review"])
        for path in sensitive:
            lines.append(f"- Review before sharing: {path}")

    lines.extend(
        [
            "",
            "## Packet Notes",
            "- Keep drafts factual: identify the collector, current creditor, masked account, dates, disputed portion, requested validation, and attachments.",
            "- Do not admit the debt, promise payment, authorize payment, or negotiate settlement unless the user explicitly chooses that after owner/legal review.",
            "- Treat court papers, arbitration demands, and lawsuit deadlines as legal owner review, not ordinary validation-letter work.",
            "",
            "## Do Not Upload",
            "Full SSNs, full ID scans, bank/card credentials, full account numbers, private keys, tokens, `.env` files, or unrelated consumer records.",
        ]
    )
    return "\n".join(lines) + "\n", 2 if any_hold else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", required=True, type=Path, help="CSV of debt collection cases.")
    parser.add_argument("--evidence-dir", required=True, type=Path, help="Directory containing supporting evidence files.")
    parser.add_argument("--today", type=parse_date, default=date.today(), help="Run date as YYYY-MM-DD.")
    parser.add_argument("--output", type=Path, help="Optional Markdown output path.")
    args = parser.parse_args()

    cases = read_cases(args.cases)
    evidence = evidence_index(args.evidence_dir)
    report, exit_code = render_report(cases, evidence, args.today)
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
