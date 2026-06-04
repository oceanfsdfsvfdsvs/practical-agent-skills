#!/usr/bin/env python3
"""Preflight credit report dispute packets before bureau or furnisher submission."""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


EVIDENCE_KEYWORDS = {
    "highlighted_report_page": ("credit-report", "report-page", "highlight", "bureau-page"),
    "identity_theft_report": ("identity-theft", "idtheft", "ftc-report", "police-report", "fraud-affidavit"),
    "payment_or_settlement": ("payment", "paid", "payoff", "settlement", "receipt", "statement", "zero-balance"),
    "duplicate_support": ("duplicate", "tradeline", "same-account", "mixed-file"),
    "prior_deletion_or_response": ("prior-response", "deletion", "investigation", "verified", "reinserted"),
    "furnisher_response": ("furnisher", "creditor", "collector", "servicer", "lender-response"),
    "mailing_proof": ("certified", "mailing", "tracking", "receipt"),
    "personal_info_proof": ("address-proof", "name-proof", "identity-proof", "personal-info"),
}

ISSUE_ALIASES = {
    "fraud": "identity_theft",
    "identity theft": "identity_theft",
    "id theft": "identity_theft",
    "not mine": "not_mine",
    "not_mine": "not_mine",
    "paid": "paid_or_settled",
    "settled": "paid_or_settled",
    "paid_or_settled": "paid_or_settled",
    "wrong balance": "wrong_balance_or_status",
    "wrong status": "wrong_balance_or_status",
    "late payment": "wrong_balance_or_status",
    "wrong_balance_or_status": "wrong_balance_or_status",
    "duplicate": "duplicate_or_mixed_file",
    "mixed file": "duplicate_or_mixed_file",
    "duplicate_or_mixed_file": "duplicate_or_mixed_file",
    "obsolete": "obsolete_or_stale",
    "stale": "obsolete_or_stale",
    "obsolete_or_stale": "obsolete_or_stale",
    "personal info": "personal_info",
    "personal_info": "personal_info",
    "investigation": "investigation_response",
    "investigation_response": "investigation_response",
}

VALID_ISSUES = set(ISSUE_ALIASES.values()) | {"mixed"}

SENSITIVE_FILENAME = re.compile(
    r"(token|secret|api[-_ ]?key|private[-_ ]?key|password|full[-_ ]?card|cvv|ssn|passport|driver[-_ ]?license|bank[-_ ]?login)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CreditReportItem:
    row_number: int
    item_id: str
    bureau: str
    furnisher: str
    account_name: str
    issue_type: str
    report_date: date | None
    first_seen_date: date | None
    last_dispute_date: date | None
    response_date: date | None
    prior_result: str
    reported_status: str
    claimed_correction: str
    amount: Decimal
    identity_theft: bool
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


def normalize_issue(value: str, identity_theft: bool) -> str:
    cleaned = value.strip().lower().replace("-", "_")
    if not cleaned and identity_theft:
        return "identity_theft"
    return ISSUE_ALIASES.get(cleaned, cleaned)


def money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01'))} USD"


def read_items(path: Path) -> list[CreditReportItem]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        items: list[CreditReportItem] = []
        for index, raw in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw.items() if key}
            identity_theft = truthy(row.get("identity_theft", ""))
            issue_type = normalize_issue(row.get("issue_type", ""), identity_theft)
            items.append(
                CreditReportItem(
                    row_number=index,
                    item_id=row.get("item_id") or f"row-{index}",
                    bureau=row.get("bureau", ""),
                    furnisher=row.get("furnisher", ""),
                    account_name=row.get("account_name", ""),
                    issue_type=issue_type,
                    report_date=parse_date(row.get("report_date", "")),
                    first_seen_date=parse_date(row.get("first_seen_date", "")),
                    last_dispute_date=parse_date(row.get("last_dispute_date", "")),
                    response_date=parse_date(row.get("response_date", "")),
                    prior_result=row.get("prior_result", "").lower(),
                    reported_status=row.get("reported_status", ""),
                    claimed_correction=row.get("claimed_correction", ""),
                    amount=parse_decimal(row.get("amount", "")),
                    identity_theft=identity_theft or issue_type == "identity_theft",
                    live_action_requested=truthy(row.get("live_action_requested", "")),
                    fields=row,
                )
            )
        return items


def evidence_index(evidence_dir: Path) -> dict[str, list[Path]]:
    files: dict[str, list[Path]] = {}
    if not evidence_dir.exists():
        return files
    for path in evidence_dir.rglob("*"):
        if path.is_file():
            files.setdefault(path.name.lower(), []).append(path)
    return files


def evidence_present(item: CreditReportItem, evidence: dict[str, list[Path]], evidence_type: str) -> tuple[bool, list[str]]:
    field_name = {
        "highlighted_report_page": "highlighted_report_page",
        "identity_theft_report": "identity_theft_report",
        "payment_or_settlement": "payment_proof",
        "duplicate_support": "duplicate_support",
        "prior_deletion_or_response": "prior_deletion_or_response",
        "furnisher_response": "furnisher_response",
        "mailing_proof": "mailing_proof",
        "personal_info_proof": "personal_info_proof",
    }[evidence_type]
    if truthy(item.fields.get(field_name, "")):
        return True, [f"csv:{field_name}"]

    item_key = item.item_id.lower()
    keywords = EVIDENCE_KEYWORDS[evidence_type]
    hits: list[str] = []
    for name, paths in evidence.items():
        name_without_item = name.replace(item_key, "")
        if item_key in name and any(keyword in name_without_item for keyword in keywords):
            hits.extend(str(path) for path in paths)
    return bool(hits), hits[:3]


def sensitive_hits(evidence: dict[str, list[Path]]) -> list[str]:
    hits: list[str] = []
    for paths in evidence.values():
        for path in paths:
            if SENSITIVE_FILENAME.search(path.name):
                hits.append(str(path))
    return sorted(hits)


def required_evidence_types(item: CreditReportItem) -> list[str]:
    required = ["highlighted_report_page"]
    if item.identity_theft or item.issue_type in {"identity_theft", "not_mine"}:
        required.append("identity_theft_report")
    if item.issue_type in {"paid_or_settled", "wrong_balance_or_status"}:
        required.append("payment_or_settlement")
    if item.issue_type == "duplicate_or_mixed_file":
        required.append("duplicate_support")
    if item.issue_type in {"personal_info", "duplicate_or_mixed_file"}:
        required.append("personal_info_proof")
    if item.issue_type == "investigation_response" or "reinsert" in item.claimed_correction.lower():
        required.append("prior_deletion_or_response")
    return required


def evaluate(item: CreditReportItem, evidence: dict[str, list[Path]], today: date) -> tuple[str, list[str], list[str]]:
    blockers: list[str] = []
    reviews: list[str] = []

    if not item.bureau:
        blockers.append("missing_bureau")
    if not (item.furnisher or item.account_name):
        blockers.append("missing_account_or_furnisher")
    if not item.claimed_correction:
        blockers.append("missing_requested_correction")
    if not item.issue_type:
        blockers.append("missing_error_type")
    elif item.issue_type not in VALID_ISSUES:
        reviews.append("unrecognized_error_type_verify_before_send")

    for evidence_type in required_evidence_types(item):
        present, _ = evidence_present(item, evidence, evidence_type)
        if not present:
            if evidence_type == "highlighted_report_page":
                blockers.append("highlighted_report_page_missing")
            elif evidence_type == "identity_theft_report":
                blockers.append("identity_theft_report_missing")
            elif evidence_type == "payment_or_settlement":
                blockers.append("payment_or_settlement_proof_missing")
            elif evidence_type == "duplicate_support":
                blockers.append("duplicate_or_mixed_file_support_missing")
            elif evidence_type == "prior_deletion_or_response":
                blockers.append("reinserted_item_prior_deletion_missing")
            elif evidence_type == "personal_info_proof":
                reviews.append("personal_info_or_identity_proof_missing")

    if item.furnisher and item.issue_type not in {"personal_info", "investigation_response"}:
        if not evidence_present(item, evidence, "furnisher_response")[0]:
            reviews.append("furnisher_routing_or_response_missing")

    if item.last_dispute_date and item.prior_result in {"verified", "unchanged", "no relief", "closed"}:
        has_new_evidence = any(
            evidence_present(item, evidence, evidence_type)[0]
            for evidence_type in ("payment_or_settlement", "identity_theft_report", "duplicate_support", "prior_deletion_or_response", "furnisher_response")
        )
        if not has_new_evidence:
            blockers.append("repeat_dispute_needs_new_evidence")
        else:
            reviews.append("repeat_dispute_explain_new_evidence")

    if item.response_date and (today - item.response_date).days > 45 and item.prior_result in {"", "pending", "under review"}:
        reviews.append("response_followup_or_complaint_timing_review")

    if item.report_date is None:
        reviews.append("missing_report_date")
    if item.live_action_requested:
        blockers.append("live_action_requested")

    if item.issue_type == "obsolete_or_stale" and not item.fields.get("date_of_first_delinquency", ""):
        reviews.append("date_of_first_delinquency_missing")

    decision = "Ready for owner review"
    if reviews:
        decision = "Review before send"
    if blockers:
        decision = "Hold dispute packet pending evidence repair"
    return decision, blockers, reviews


def why_blocker(flag: str) -> tuple[str, str]:
    messages = {
        "missing_bureau": ("A bureau-specific item is needed for a targeted dispute.", "Add Equifax, Experian, TransUnion, other CRA, or furnisher context."),
        "missing_account_or_furnisher": ("The recipient cannot identify the tradeline or record.", "Add account label, furnisher, collector, or masked account number."),
        "missing_requested_correction": ("The packet must say exactly what should be corrected.", "Write the requested correction in one factual sentence."),
        "missing_error_type": ("A vague dispute is easier to reject or mishandle.", "Classify the error type and disputed field."),
        "highlighted_report_page_missing": ("The packet needs the exact bureau page and disputed field.", "Attach or label a highlighted official report page."),
        "identity_theft_report_missing": ("Fraud or not-mine claims usually need sworn identity-theft support.", "Attach an FTC IdentityTheft.gov report, police report, or equivalent record."),
        "payment_or_settlement_proof_missing": ("Paid or wrong-balance claims need creditor or payment evidence.", "Attach payoff, settlement, receipt, statement, or creditor letter."),
        "duplicate_or_mixed_file_support_missing": ("Duplicate or mixed-file disputes need comparison evidence.", "Attach both report entries and identity/account mismatch proof."),
        "reinserted_item_prior_deletion_missing": ("Reinserted-item follow-up depends on the prior deletion or response record.", "Attach the prior investigation, deletion, or response letter."),
        "repeat_dispute_needs_new_evidence": ("Repeated verified disputes need new facts or a narrower theory.", "Add new evidence or rewrite as a specific field correction."),
        "live_action_requested": ("The skill prepares packets only and must not submit live disputes.", "Have the owner submit in the portal or authorize a separate live-action workflow."),
    }
    return messages.get(flag, ("This issue can weaken or block the dispute packet.", "Repair or document this issue before sending."))


def why_review(flag: str) -> tuple[str, str]:
    messages = {
        "unrecognized_error_type_verify_before_send": ("The script cannot map this issue to a standard evidence rule.", "Verify the theory and add manual notes."),
        "personal_info_or_identity_proof_missing": ("Personal-information and mixed-file cases often need identity/address proof.", "Attach redacted proof or explain why it is not needed."),
        "furnisher_routing_or_response_missing": ("Furnished account data may need creditor or collector routing.", "Prepare a furnisher letter or explain bureau-only routing."),
        "repeat_dispute_explain_new_evidence": ("A repeated dispute should call out what changed.", "Summarize the new evidence in the packet."),
        "response_followup_or_complaint_timing_review": ("A stale pending response may need follow-up tracking.", "Check current status and consider complaint readiness."),
        "missing_report_date": ("Report date anchors the disputed record.", "Add the official report date."),
        "date_of_first_delinquency_missing": ("Obsolete collection review needs the aging anchor.", "Add date-of-first-delinquency or account history proof."),
    }
    return messages.get(flag, ("This flag can weaken the dispute packet.", "Review before sending."))


def render_report(items: list[CreditReportItem], evidence: dict[str, list[Path]], today: date) -> tuple[str, int]:
    item_results = [(item, *evaluate(item, evidence, today)) for item in items]
    any_blockers = any(blockers for _, _, blockers, _ in item_results)
    any_reviews = any(reviews for _, _, _, reviews in item_results)
    overall = "Ready for owner review"
    if any_reviews:
        overall = "Review before send"
    if any_blockers:
        overall = "Hold dispute packet pending evidence repair"

    lines = [
        "# Credit Report Dispute Preflight Report",
        "",
        f"Run date: {today.isoformat()}",
        "",
        "## Credit Report Dispute Decision",
        overall,
        "",
        "## Item Summary",
        "| Item | Bureau | Furnisher | Error Type | Amount | Decision |",
        "|---|---|---|---|---:|---|",
    ]
    for item, decision, _, _ in item_results:
        lines.append(
            f"| {item.item_id} | {item.bureau or 'missing'} | {item.furnisher or item.account_name or 'missing'} | "
            f"{item.issue_type or 'missing'} | {money(item.amount)} | {decision} |"
        )

    lines.extend(["", "## Evidence Matrix", "| Item | Evidence | Status | Source | Repair action |", "|---|---|---|---|---|"])
    evidence_labels = {
        "highlighted_report_page": "Highlighted bureau report page",
        "identity_theft_report": "Identity-theft report",
        "payment_or_settlement": "Payment or settlement proof",
        "duplicate_support": "Duplicate or mixed-file support",
        "prior_deletion_or_response": "Prior deletion or response",
        "furnisher_response": "Furnisher response",
        "personal_info_proof": "Personal info or identity proof",
    }
    for item, _, _, _ in item_results:
        needed = list(dict.fromkeys(required_evidence_types(item) + ["furnisher_response"]))
        for evidence_type in needed:
            present, sources = evidence_present(item, evidence, evidence_type)
            status = "present" if present else "missing"
            source = ", ".join(sources) if sources else "-"
            repair = "Use attached record" if present else f"Add {evidence_labels[evidence_type].lower()}"
            lines.append(f"| {item.item_id} | {evidence_labels[evidence_type]} | {status} | {source} | {repair} |")

    lines.extend(["", "## Blockers", "| Item | Blocker | Why it matters | Next action |", "|---|---|---|---|"])
    blocker_count = 0
    for item, _, blockers, _ in item_results:
        for blocker in blockers:
            why, action = why_blocker(blocker)
            lines.append(f"| {item.item_id} | {blocker} | {why} | {action} |")
            blocker_count += 1
    if blocker_count == 0:
        lines.append("| - | none | No blocking evidence gaps detected. | Continue owner review before sending. |")

    lines.extend(["", "## Review Flags", "| Item | Flag | Why it matters | Next action |", "|---|---|---|---|"])
    review_count = 0
    for item, _, _, reviews in item_results:
        for review in reviews:
            why, action = why_review(review)
            lines.append(f"| {item.item_id} | {review} | {why} | {action} |")
            review_count += 1
    if review_count == 0:
        lines.append("| - | none | No review-only flags detected. | Keep evidence packet concise. |")

    sensitive = sensitive_hits(evidence)
    lines.extend(["", "## Sensitive Filename Review"])
    if sensitive:
        lines.append("Remove or rename files before sharing: " + ", ".join(sensitive))
    else:
        lines.append("No sensitive filename patterns detected in the supplied evidence directory.")

    lines.extend(
        [
            "",
            "## Packet Notes",
            "- Use bureau-specific item names, dates, disputed fields, requested corrections, and attachments.",
            "- Separate bureau dispute, furnisher dispute, identity-theft packet, and CFPB complaint follow-up.",
            "- Do not claim guaranteed deletion; dispute only factual inaccuracies or unsupported investigation outcomes.",
            "",
            "## Do Not Upload",
            "Full SSNs, full ID scans, account credentials, full card or bank numbers, private keys, tokens, `.env` files, or unrelated consumer records.",
            "",
        ]
    )
    return "\n".join(lines), 2 if any_blockers else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--items", required=True, type=Path, help="CSV of credit report dispute items")
    parser.add_argument("--evidence-dir", required=True, type=Path, help="Directory containing local evidence files")
    parser.add_argument("--today", default=date.today().isoformat(), help="Run date in YYYY-MM-DD format")
    parser.add_argument("--output", type=Path, help="Optional output Markdown path")
    args = parser.parse_args()

    today = parse_date(args.today)
    if today is None:
        raise SystemExit("--today cannot be blank")

    items = read_items(args.items)
    evidence = evidence_index(args.evidence_dir)
    report, returncode = render_report(items, evidence, today)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    print(report)
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
