#!/usr/bin/env python3
"""Build a local chargeback evidence inventory report from a case JSON and files."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


REASON_ALIASES = {
    "product_not_received": (
        "product_not_received",
        "not received",
        "goods not received",
        "merchandise not received",
        "service not received",
        "item not received",
        "did not receive",
    ),
    "fraudulent_or_no_authorization": (
        "fraud",
        "fraudulent",
        "no authorization",
        "unauthorized",
        "not authorized",
        "cardholder does not recognize",
    ),
    "duplicate": ("duplicate", "charged twice", "multiple charges"),
    "credit_not_processed": (
        "credit not processed",
        "refund not processed",
        "refund not received",
        "cancelled merchandise",
    ),
    "product_unacceptable_or_not_as_described": (
        "not as described",
        "unacceptable",
        "defective",
        "damaged",
        "quality",
    ),
    "cancelled_subscription": (
        "subscription cancelled",
        "canceled subscription",
        "cancelled recurring",
        "recurring transaction cancelled",
    ),
    "digital_goods_or_service": (
        "digital goods",
        "digital service",
        "download",
        "license",
        "service provided",
    ),
}

REASON_REQUIREMENTS = {
    "product_not_received": {
        "required": [
            "order_receipt",
            "fulfillment_record",
            "proof_of_delivery",
            "customer_identity_match",
            "refund_status",
        ],
        "helpful": ["customer_communication", "signature_or_delivery_photo"],
    },
    "fraudulent_or_no_authorization": {
        "required": [
            "authorization_evidence",
            "customer_identity_match",
            "delivery_or_usage_evidence",
            "refund_status",
        ],
        "helpful": ["prior_relationship", "customer_communication"],
    },
    "duplicate": {
        "required": ["transaction_records", "order_history", "refund_status"],
        "helpful": ["cart_or_invoice_history"],
    },
    "credit_not_processed": {
        "required": [
            "refund_policy",
            "refund_status",
            "customer_communication",
            "return_or_cancellation_record",
        ],
        "helpful": ["processor_refund_id"],
    },
    "product_unacceptable_or_not_as_described": {
        "required": [
            "product_description",
            "fulfillment_record",
            "customer_communication",
            "remediation_offer",
            "refund_status",
        ],
        "helpful": ["quality_control_record", "photos_or_specs"],
    },
    "cancelled_subscription": {
        "required": [
            "subscription_terms",
            "cancellation_history",
            "billing_history",
            "usage_after_charge",
            "refund_status",
        ],
        "helpful": ["renewal_notice", "customer_communication"],
    },
    "digital_goods_or_service": {
        "required": [
            "access_logs",
            "download_or_usage",
            "terms_acceptance",
            "customer_identity_match",
            "refund_status",
        ],
        "helpful": ["ip_device_match", "customer_communication"],
    },
    "unknown": {
        "required": [
            "processor_notice",
            "order_receipt",
            "customer_claim_text",
            "refund_status",
        ],
        "helpful": ["delivery_or_usage_evidence", "customer_communication"],
    },
}

PRODUCT_ADDITIONS = {
    "physical": ["proof_of_delivery", "shipping_address_match"],
    "digital": ["access_logs", "download_or_usage", "terms_acceptance"],
    "saas": ["subscription_terms", "usage_after_charge", "cancellation_history"],
    "subscription": ["subscription_terms", "usage_after_charge", "cancellation_history"],
    "service": ["service_completion", "appointment_or_delivery_record"],
    "marketplace": ["seller_fulfillment_record", "platform_order_record"],
}

FILENAME_KEYWORDS = {
    "processor_notice": ("notice", "dispute", "chargeback", "reason"),
    "order_receipt": ("receipt", "order", "invoice"),
    "fulfillment_record": ("fulfillment", "shipment", "packing", "dispatch"),
    "proof_of_delivery": ("delivery", "delivered", "tracking", "carrier", "signed"),
    "signature_or_delivery_photo": ("signature", "delivery-photo", "porch", "handoff"),
    "customer_identity_match": ("avs", "cvv", "3ds", "3d-secure", "address-match", "identity"),
    "authorization_evidence": ("authorization", "auth", "3ds", "cvv", "avs"),
    "delivery_or_usage_evidence": ("delivery", "usage", "access", "download", "login"),
    "refund_status": ("refund", "credit", "reversal"),
    "customer_communication": ("email", "message", "chat", "ticket", "support"),
    "prior_relationship": ("history", "previous", "account"),
    "transaction_records": ("transaction", "charge", "payment", "settlement"),
    "order_history": ("order-history", "orders", "invoice-history"),
    "cart_or_invoice_history": ("cart", "invoice", "checkout"),
    "refund_policy": ("refund-policy", "return-policy", "policy"),
    "return_or_cancellation_record": ("return", "cancellation", "cancel"),
    "processor_refund_id": ("refund-id", "processor-refund"),
    "product_description": ("listing", "product-description", "spec", "catalog"),
    "remediation_offer": ("replacement", "remediation", "resolution", "offer"),
    "quality_control_record": ("quality", "qc", "inspection"),
    "photos_or_specs": ("photo", "image", "spec"),
    "subscription_terms": ("subscription-terms", "renewal-terms", "subscription", "renewal"),
    "cancellation_history": ("cancellation", "cancelled", "canceled"),
    "billing_history": ("billing", "renewal", "invoice"),
    "usage_after_charge": ("usage-after", "post-charge", "active-after", "renewal-usage"),
    "renewal_notice": ("renewal-notice", "renewal-email"),
    "access_logs": ("access", "login", "license", "activation"),
    "download_or_usage": ("download", "usage", "event"),
    "terms_acceptance": ("terms-accepted", "tos", "policy-accepted", "checkout-terms"),
    "ip_device_match": ("ip", "device", "fingerprint"),
    "service_completion": ("completion", "complete", "deliverable"),
    "appointment_or_delivery_record": ("appointment", "attended", "check-in"),
    "seller_fulfillment_record": ("seller", "supplier", "fulfillment"),
    "platform_order_record": ("platform", "marketplace", "shopify", "amazon"),
    "shipping_address_match": ("shipping-address", "address-match", "delivery-address"),
    "customer_claim_text": ("claim", "customer-claim", "reason"),
}

CASE_FIELD_EVIDENCE = {
    "order_id": "order_receipt",
    "charge_date": "transaction_records",
    "tracking_number": "fulfillment_record",
    "delivered_at": "proof_of_delivery",
    "carrier": "proof_of_delivery",
    "signature_required": "signature_or_delivery_photo",
    "billing_address_match": "customer_identity_match",
    "shipping_address_match": "shipping_address_match",
    "avs_result": "authorization_evidence",
    "cvv_result": "authorization_evidence",
    "three_d_secure": "authorization_evidence",
    "refund_status": "refund_status",
    "policy_accepted_at": "terms_acceptance",
    "customer_messages": "customer_communication",
    "support_ticket": "customer_communication",
    "access_events": "access_logs",
    "download_events": "download_or_usage",
    "usage_after_charge": "usage_after_charge",
    "subscription_terms_url": "subscription_terms",
    "cancellation_history": "cancellation_history",
    "service_completed_at": "service_completion",
}

SENSITIVE_PATTERNS = re.compile(
    r"(cvv|full[-_ ]?card|pan|password|secret|token|api[-_ ]?key|private[-_ ]?key|ssn|passport)",
    re.IGNORECASE,
)


@dataclass
class EvidenceHit:
    evidence_type: str
    source: str
    note: str


def normalize_reason(raw: str | None) -> str:
    if not raw:
        return "unknown"
    value = raw.strip().lower().replace("-", "_").replace(" ", "_")
    if value in REASON_REQUIREMENTS:
        return value
    text = raw.lower()
    for reason, aliases in REASON_ALIASES.items():
        if any(alias in text for alias in aliases):
            return reason
    return "unknown"


def load_case(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit("Case JSON must be an object.")
    return data


def collect_files(evidence_dir: Path | None) -> list[Path]:
    if evidence_dir is None:
        return []
    if not evidence_dir.exists():
        raise SystemExit(f"Evidence directory not found: {evidence_dir}")
    return sorted(path for path in evidence_dir.rglob("*") if path.is_file())


def evidence_from_case(case: dict[str, Any]) -> list[EvidenceHit]:
    hits: list[EvidenceHit] = []
    for field, evidence_type in CASE_FIELD_EVIDENCE.items():
        value = case.get(field)
        if value not in (None, "", [], {}):
            hits.append(EvidenceHit(evidence_type, f"case.{field}", "case field present"))
    if case.get("delivered_at") or case.get("access_events") or case.get("download_events"):
        hits.append(
            EvidenceHit(
                "delivery_or_usage_evidence",
                "case.delivery_or_usage",
                "delivery/access/use field present",
            )
        )
    return hits


def evidence_from_files(files: list[Path]) -> tuple[list[EvidenceHit], list[Path]]:
    hits: list[EvidenceHit] = []
    sensitive: list[Path] = []
    for path in files:
        normalized = path.name.lower().replace(" ", "-").replace("_", "-")
        if SENSITIVE_PATTERNS.search(path.name):
            sensitive.append(path)
        for evidence_type, keywords in FILENAME_KEYWORDS.items():
            if any(filename_matches(normalized, keyword) for keyword in keywords):
                hits.append(EvidenceHit(evidence_type, str(path), "filename keyword match"))
    return hits, sensitive


def filename_matches(normalized_name: str, keyword: str) -> bool:
    tokens = set(re.split(r"[^a-z0-9]+", normalized_name))
    normalized_keyword = keyword.lower().replace("_", "-")
    if len(normalized_keyword) <= 3:
        return normalized_keyword in tokens
    if "-" in normalized_keyword:
        return normalized_keyword in normalized_name
    return normalized_keyword in tokens or normalized_keyword in normalized_name


def format_case_summary(case: dict[str, Any], reason: str) -> str:
    fields = [
        ("Processor", case.get("processor", "unknown")),
        ("Dispute ID", case.get("dispute_id", "unknown")),
        ("Reason category", reason),
        ("Product type", case.get("product_type", "unknown")),
        ("Amount", f"{case.get('amount', 'unknown')} {case.get('currency', '')}".strip()),
        ("Deadline", case.get("deadline", "unknown")),
        ("Order ID", case.get("order_id", "unknown")),
    ]
    lines = ["## Case Summary", "| Field | Value |", "|---|---|"]
    lines.extend(f"| {key} | {value} |" for key, value in fields)
    return "\n".join(lines)


def parse_deadline(value: Any, today: date | None = None) -> str:
    if not value:
        return "Deadline unknown; verify processor response window before drafting."
    try:
        deadline = date.fromisoformat(str(value)[:10])
    except ValueError:
        return "Deadline format not parsed; verify processor response window manually."
    review_date = today or datetime.now().date()
    days = (deadline - review_date).days
    if days < 0:
        return f"Deadline appears passed by {abs(days)} day(s); confirm whether evidence is still accepted."
    if days <= 2:
        return f"Deadline risk: {days} day(s) remaining."
    return f"Deadline check: {days} day(s) remaining."


def build_report(case: dict[str, Any], files: list[Path], today: date | None = None) -> str:
    reason = normalize_reason(str(case.get("reason_category") or case.get("reason_code") or ""))
    product_type = str(case.get("product_type", "")).strip().lower()
    requirements = REASON_REQUIREMENTS.get(reason, REASON_REQUIREMENTS["unknown"])
    required = list(dict.fromkeys(requirements["required"] + PRODUCT_ADDITIONS.get(product_type, [])))
    helpful = requirements["helpful"]

    hits = evidence_from_case(case)
    file_hits, sensitive_files = evidence_from_files(files)
    hits.extend(file_hits)
    present = {hit.evidence_type for hit in hits}
    missing_required = [item for item in required if item not in present]
    missing_helpful = [item for item in helpful if item not in present]

    if case.get("deadline") and parse_deadline(case["deadline"], today).startswith("Deadline appears passed"):
        decision = "Deadline risk - confirm whether evidence can still be submitted"
    elif missing_required:
        decision = "Blocked until evidence is added"
    elif sensitive_files:
        decision = "Challenge candidate after redaction review"
    else:
        decision = "Challenge candidate after owner review"

    lines = [
        "# Chargeback Evidence Pack",
        "",
        "## Dispute Decision",
        decision,
        "",
        "## Deadline Check",
        parse_deadline(case.get("deadline"), today),
        "",
        format_case_summary(case, reason),
        "",
        "## Evidence Index",
        "| Evidence type | Status | Source | Note |",
        "|---|---|---|---|",
    ]

    for evidence_type in sorted(present):
        sources = [hit.source for hit in hits if hit.evidence_type == evidence_type]
        lines.append(f"| {evidence_type} | present | {', '.join(sources[:3])} | Review and redact before upload |")

    for evidence_type in missing_required:
        lines.append(f"| {evidence_type} | missing blocker | - | Required for this reason/product type |")

    for evidence_type in missing_helpful:
        lines.append(f"| {evidence_type} | missing helpful | - | Helpful but not always blocking |")

    lines.extend(
        [
            "",
            "## Redaction Review",
        ]
    )
    if sensitive_files:
        lines.extend(f"- Review before upload: `{path}`" for path in sensitive_files)
    else:
        lines.append("- No sensitive filenames detected. Still inspect file contents before submission.")

    lines.extend(
        [
            "",
            "## Submission Narrative Draft",
            narrative(case, reason, missing_required),
            "",
            "## Submit Checklist",
            "- Verify processor-specific deadline, file limits, and accepted evidence types.",
            "- Attach only transaction-relevant files and crop or redact unrelated customer data.",
            "- Keep a timestamped copy of exactly what was submitted.",
            "- Have the owner confirm the facts before submitting.",
        ]
    )
    return "\n".join(lines) + "\n"


def narrative(case: dict[str, Any], reason: str, missing_required: list[str]) -> str:
    order_id = case.get("order_id", "[order_id]")
    amount = f"{case.get('amount', '[amount]')} {case.get('currency', '')}".strip()
    product_type = case.get("product_type", "[product_type]")
    if missing_required:
        return (
            "Draft is intentionally limited because required evidence is missing: "
            + ", ".join(missing_required)
            + ". Do not submit a final narrative until these gaps are resolved or explicitly accepted."
        )
    return (
        f"The customer placed order {order_id} for a {product_type} transaction totaling {amount}. "
        f"The dispute reason is {reason}. The attached evidence supports the order, transaction, "
        "fulfillment or access, customer identity or policy context, and refund status. "
        "Based on these transaction-specific records, the merchant requests reversal of the dispute."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a chargeback evidence inventory report.")
    parser.add_argument("--case", type=Path, help="Path to a case JSON file.")
    parser.add_argument("--evidence-dir", type=Path, help="Directory containing evidence files.")
    parser.add_argument("--today", help="Optional review date in YYYY-MM-DD format for stable deadline checks.")
    args = parser.parse_args()

    today = date.fromisoformat(args.today) if args.today else None
    case = load_case(args.case)
    files = collect_files(args.evidence_dir)
    print(build_report(case, files, today))


if __name__ == "__main__":
    main()
