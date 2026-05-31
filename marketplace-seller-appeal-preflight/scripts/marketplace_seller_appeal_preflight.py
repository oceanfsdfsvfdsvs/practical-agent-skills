#!/usr/bin/env python3
"""Preflight online marketplace seller appeal packets before submission."""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


TYPE_ALIASES = {
    "authenticity": ("authenticity", "inauthentic", "counterfeit", "not authentic", "supplier invoice"),
    "ip": ("ip", "intellectual property", "copyright", "trademark", "patent", "rights owner"),
    "used_sold_as_new": ("used sold as new", "used item sold as new", "condition complaint", "not new"),
    "restricted_product": ("restricted", "restricted product", "prohibited", "category approval"),
    "safety": ("safety", "compliance", "certificate", "hazard", "recall"),
    "fulfillment": ("late shipment", "late dispatch", "cancellation", "valid tracking", "fulfillment"),
    "customer_defect": ("order defect", "negative feedback", "a-to-z", "customer defect", "complaint rate"),
    "account_deactivation": ("account deactivation", "section 3", "seller account", "account health", "deactivated"),
}

REQUIRED_EVIDENCE = {
    "authenticity": ("supplier_invoice", "product_identity_photos"),
    "ip": ("authorization_letter", "listing_correction"),
    "used_sold_as_new": ("customer_messages", "product_identity_photos", "corrective_action_evidence"),
    "restricted_product": ("policy_mapping", "compliance_document", "listing_correction"),
    "safety": ("compliance_document", "corrective_action_evidence"),
    "fulfillment": ("order_metrics", "tracking_or_carrier_evidence", "corrective_action_evidence"),
    "customer_defect": ("order_metrics", "customer_messages", "corrective_action_evidence"),
    "account_deactivation": ("notice_text", "issue_inventory", "corrective_action_evidence"),
    "unknown": ("notice_text", "policy_mapping"),
}

FIELD_EVIDENCE = {
    "notice_text": ("notice", "deactivation", "account-health", "seller-central", "case"),
    "issue_inventory": ("issue", "inventory", "account-health", "case-list", "violations"),
    "supplier_invoice": ("invoice", "receipt", "purchase", "supplier", "wholesale"),
    "authorization_letter": ("authorization", "letter", "license", "distributor", "brand"),
    "product_identity_photos": ("photo", "product", "label", "packaging", "asin", "sku"),
    "listing_correction": ("listing", "detail-page", "correction", "removed", "screenshot"),
    "policy_mapping": ("policy", "notice", "reason", "violation"),
    "compliance_document": ("certificate", "compliance", "test-report", "safety", "coa"),
    "order_metrics": ("metric", "defect", "late", "cancellation", "tracking", "orders"),
    "tracking_or_carrier_evidence": ("tracking", "carrier", "shipment", "scan", "delivery"),
    "customer_messages": ("customer", "buyer", "message", "complaint", "feedback"),
    "corrective_action_evidence": ("sop", "training", "refund", "replacement", "removed", "corrective"),
}

SENSITIVE_FILENAME = re.compile(
    r"(token|secret|api[-_ ]?key|private[-_ ]?key|password|full[-_ ]?card|cvv|ssn|\.env|unsafe[-_ ]?upload)",
    re.IGNORECASE,
)

VAGUE_POA = {
    "",
    "n/a",
    "na",
    "none",
    "unknown",
    "we will be careful",
    "will be careful",
    "mistake",
    "supplier issue",
    "not our fault",
}


@dataclass(frozen=True)
class AppealCase:
    row_number: int
    case_id: str
    marketplace: str
    scope: str
    reason: str
    enforcement_type: str
    notice_date: date | None
    appeal_deadline: date | None
    root_cause: str
    corrective_action: str
    preventive_action: str
    prior_appeal_count: int
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


def parse_int(value: str) -> int:
    value = value.strip()
    if not value:
        return 0
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"invalid integer '{value}'") from exc


def truthy(value: str) -> bool:
    return value.strip().lower() in {"yes", "y", "true", "1", "present", "available", "attached"}


def text_present(value: str) -> bool:
    normalized = re.sub(r"\s+", " ", value.strip().lower())
    return normalized not in VAGUE_POA and len(normalized) >= 12


def normalize_type(value: str) -> str:
    lowered = value.strip().lower()
    for normalized, aliases in TYPE_ALIASES.items():
        if lowered == normalized or any(alias in lowered for alias in aliases):
            return normalized
    return "unknown"


def read_cases(path: Path) -> list[AppealCase]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows: list[AppealCase] = []
        for index, raw in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw.items() if key}
            reason = row.get("reason") or row.get("notice_reason") or row.get("complaint_type") or ""
            case_id = row.get("case_id") or row.get("appeal_id") or row.get("ticket_id") or f"row-{index}"
            scope = row.get("scope") or row.get("asin") or row.get("sku") or row.get("listing_id") or "unknown"
            rows.append(
                AppealCase(
                    row_number=index,
                    case_id=case_id,
                    marketplace=row.get("marketplace", ""),
                    scope=scope,
                    reason=reason,
                    enforcement_type=normalize_type(row.get("enforcement_type") or reason),
                    notice_date=parse_date(row.get("notice_date", "")),
                    appeal_deadline=parse_date(row.get("appeal_deadline", "")),
                    root_cause=row.get("root_cause", ""),
                    corrective_action=row.get("corrective_action", ""),
                    preventive_action=row.get("preventive_action", ""),
                    prior_appeal_count=parse_int(row.get("prior_appeal_count", "")),
                    fields=row,
                )
            )
        return rows


def evidence_index(evidence_dir: Path) -> dict[str, list[Path]]:
    files: dict[str, list[Path]] = {}
    if not evidence_dir.exists():
        return files
    for path in evidence_dir.rglob("*"):
        if path.is_file():
            files.setdefault(path.name.lower(), []).append(path)
    return files


def evidence_present(case: AppealCase, evidence: dict[str, list[Path]], evidence_type: str) -> tuple[bool, list[str]]:
    if truthy(case.fields.get(evidence_type, "")):
        return True, [f"csv:{evidence_type}"]

    keys = [case.case_id.lower(), case.scope.lower()]
    asin = case.fields.get("asin", "").lower()
    sku = case.fields.get("sku", "").lower()
    if asin:
        keys.append(asin)
    if sku:
        keys.append(sku)

    keywords = FIELD_EVIDENCE[evidence_type]
    hits: list[str] = []
    for name, paths in evidence.items():
        belongs = any(key and key != "unknown" and key in name for key in keys)
        if belongs and any(keyword in name for keyword in keywords):
            hits.extend(str(path) for path in paths)
    return bool(hits), hits[:3]


def required_evidence(enforcement_type: str) -> tuple[str, ...]:
    return REQUIRED_EVIDENCE.get(enforcement_type, REQUIRED_EVIDENCE["unknown"])


def supplier_docs_match(case: AppealCase) -> bool:
    marker = case.fields.get("supplier_docs_match_listing", "")
    return truthy(marker)


def evaluate(case: AppealCase, evidence: dict[str, list[Path]], today: date) -> tuple[str, list[str], list[str]]:
    blockers: list[str] = []
    reviews: list[str] = []

    if case.appeal_deadline is None:
        reviews.append("missing_appeal_deadline")
    else:
        days_left = (case.appeal_deadline - today).days
        if days_left < 0:
            blockers.append("appeal_deadline_passed")
        elif days_left <= 3:
            reviews.append("appeal_deadline_within_3_days")

    if case.enforcement_type == "unknown":
        reviews.append("unknown_enforcement_type")

    if not text_present(case.root_cause):
        blockers.append("missing_root_cause")
    if not text_present(case.corrective_action):
        blockers.append("missing_corrective_action")
    if not text_present(case.preventive_action):
        blockers.append("missing_preventive_action")

    for evidence_type in required_evidence(case.enforcement_type):
        present, _ = evidence_present(case, evidence, evidence_type)
        if present:
            continue
        if evidence_type == "supplier_invoice":
            blockers.append("missing_supply_chain_invoice")
        elif evidence_type == "authorization_letter":
            blockers.append("missing_authorization_letter")
        elif evidence_type == "compliance_document":
            blockers.append("missing_compliance_document")
        elif evidence_type == "corrective_action_evidence":
            reviews.append("corrective_action_evidence_missing")
        elif evidence_type == "policy_mapping":
            reviews.append("missing_policy_mapping")
        else:
            reviews.append(f"{evidence_type}_missing")

    if case.enforcement_type in {"authenticity", "ip", "restricted_product", "safety"} and not supplier_docs_match(case):
        blockers.append("supplier_docs_do_not_match_listing")

    if case.prior_appeal_count >= 1:
        reviews.append("prior_appeals_rejected")
    if case.prior_appeal_count >= 2 and not truthy(case.fields.get("addresses_rejection_reason", "")):
        blockers.append("repeated_appeal_without_rejection_fix")

    if truthy(case.fields.get("live_portal_action_requested", "")):
        reviews.append("live_portal_action_requires_explicit_authority")

    sensitive_hits = [
        name
        for name in evidence
        if (case.case_id.lower() in name or case.scope.lower() in name) and SENSITIVE_FILENAME.search(name)
    ]
    if sensitive_hits:
        blockers.append("sensitive_file_redaction_required")

    if blockers:
        decision = "Hold appeal pending evidence repair"
    elif reviews:
        decision = "Review before submit"
    else:
        decision = "Submit-ready after owner review"
    return decision, sorted(set(blockers)), sorted(set(reviews))


def build_report(cases: list[AppealCase], evidence: dict[str, list[Path]], today: date) -> tuple[str, bool]:
    lines = ["# Marketplace Seller Appeal Preflight Report", "", f"Run date: {today.isoformat()}", ""]
    any_blocker = False
    summary: dict[str, int] = {}
    details: list[tuple[AppealCase, str, list[str], list[str]]] = []

    for case in cases:
        decision, blockers, reviews = evaluate(case, evidence, today)
        any_blocker = any_blocker or bool(blockers)
        summary[decision] = summary.get(decision, 0) + 1
        details.append((case, decision, blockers, reviews))

    lines.append("## Seller Appeal Decision")
    for decision, count in sorted(summary.items()):
        lines.append(f"- {decision}: {count}")
    lines.append("")

    lines.append("## Case Rows")
    lines.append("| Case | Marketplace | Scope | Reason | Decision | Blockers | Review notes |")
    lines.append("|---|---|---|---|---|---|---|")
    for case, decision, blockers, reviews in details:
        lines.append(
            "| {case_id} | {marketplace} | {scope} | {reason} | {decision} | {blockers} | {reviews} |".format(
                case_id=case.case_id,
                marketplace=case.marketplace or "unknown",
                scope=case.scope,
                reason=case.enforcement_type,
                decision=decision,
                blockers=", ".join(blockers) or "-",
                reviews=", ".join(reviews) or "-",
            )
        )
    lines.append("")

    lines.append("## Evidence Coverage")
    for case, _, _, _ in details:
        lines.append(f"### {case.case_id}")
        for evidence_type in required_evidence(case.enforcement_type):
            present, hits = evidence_present(case, evidence, evidence_type)
            status = "present" if present else "missing"
            source = "; ".join(hits) if hits else "-"
            lines.append(f"- {evidence_type}: {status} ({source})")
        lines.append("")

    lines.append("## Submit Guardrails")
    lines.append("- Do not submit until blockers are resolved or explicitly accepted by the seller owner.")
    lines.append("- Do not invent invoices, supplier authorization, customer messages, compliance documents, root causes, or remediation.")
    lines.append("- Separate root cause, corrective action, and preventive action in the appeal draft.")
    lines.append("- Redact credentials, private keys, full payment data, unrelated customer records, and internal secrets.")
    return "\n".join(lines), any_blocker


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", required=True, type=Path, help="CSV of marketplace seller appeal cases")
    parser.add_argument("--evidence-dir", required=True, type=Path, help="Directory containing appeal evidence files")
    parser.add_argument("--today", default=date.today().isoformat(), help="Run date, YYYY-MM-DD")
    parser.add_argument("--output", type=Path, help="Optional Markdown output path")
    args = parser.parse_args()

    try:
        today = parse_date(args.today)
        if today is None:
            raise ValueError("--today is required")
        cases = read_cases(args.cases)
        evidence = evidence_index(args.evidence_dir)
        report, blocked = build_report(cases, evidence, today)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 1

    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
    print(report)
    return 2 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
