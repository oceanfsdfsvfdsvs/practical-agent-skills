#!/usr/bin/env python3
"""Preflight parcel loss and damage claims before carrier or insurer submission."""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


CLAIM_ALIASES = {
    "damage": ("damage", "damaged", "broken", "crushed", "wet", "contents damaged"),
    "loss": ("loss", "lost", "missing package", "not delivered", "no delivery"),
    "missing_contents": ("missing contents", "shortage", "empty box", "contents missing"),
    "late": ("late", "delayed", "service failure"),
}

STATUS_LOSS_HINTS = ("lost", "exception", "investigation", "no scan", "pending", "not delivered")
STATUS_DAMAGE_HINTS = ("damage", "damaged", "exception", "inspection")

FIELD_EVIDENCE = {
    "proof_of_value": ("invoice", "receipt", "proof-of-value", "value", "order"),
    "tracking_proof": ("tracking", "delivery", "scan", "carrier"),
    "damage_photos": ("damage", "damaged", "broken", "item-photo", "product-photo"),
    "outer_packaging_photos": ("outer", "box", "carton", "label", "packaging"),
    "inner_packaging_photos": ("inner", "padding", "packing", "bubble", "void-fill"),
    "recipient_statement": ("recipient", "customer-statement", "buyer-message", "message"),
    "repair_estimate": ("repair", "replacement", "estimate"),
    "packing_slip": ("packing-slip", "pick-list", "contents-list"),
}

SENSITIVE_FILENAME = re.compile(
    r"(token|secret|api[-_ ]?key|private[-_ ]?key|password|full[-_ ]?card|cvv|ssn)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Shipment:
    row_number: int
    shipment_id: str
    order_id: str
    carrier: str
    claim_type: str
    tracking_status: str
    item_value: Decimal
    declared_value: Decimal
    insured_value: Decimal
    currency: str
    discovery_date: date | None
    claim_deadline: date | None
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
    return value.strip().lower() in {"yes", "y", "true", "1", "present", "available", "attached"}


def normalize_claim_type(value: str) -> str:
    lowered = value.strip().lower()
    for normalized, aliases in CLAIM_ALIASES.items():
        if lowered == normalized or any(alias in lowered for alias in aliases):
            return normalized
    return "unknown"


def read_shipments(path: Path) -> list[Shipment]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows: list[Shipment] = []
        for index, raw in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw.items() if key}
            shipment_id = row.get("shipment_id") or row.get("tracking_number") or f"row-{index}"
            rows.append(
                Shipment(
                    row_number=index,
                    shipment_id=shipment_id,
                    order_id=row.get("order_id", ""),
                    carrier=row.get("carrier", ""),
                    claim_type=normalize_claim_type(row.get("claim_type", "")),
                    tracking_status=row.get("tracking_status", ""),
                    item_value=parse_decimal(row.get("item_value", "")),
                    declared_value=parse_decimal(row.get("declared_value", "")),
                    insured_value=parse_decimal(row.get("insured_value", "")),
                    currency=row.get("currency", "USD") or "USD",
                    discovery_date=parse_date(row.get("discovery_date", "")),
                    claim_deadline=parse_date(row.get("claim_deadline", "")),
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


def evidence_present(shipment: Shipment, evidence: dict[str, list[Path]], evidence_type: str) -> tuple[bool, list[str]]:
    if truthy(shipment.fields.get(evidence_type, "")):
        return True, [f"csv:{evidence_type}"]

    shipment_key = shipment.shipment_id.lower()
    order_key = shipment.order_id.lower()
    keywords = FIELD_EVIDENCE[evidence_type]
    hits: list[str] = []
    for name, paths in evidence.items():
        belongs_to_shipment = shipment_key and shipment_key in name
        belongs_to_order = order_key and order_key in name
        if (belongs_to_shipment or belongs_to_order) and any(keyword in name for keyword in keywords):
            hits.extend(str(path) for path in paths)
    return bool(hits), hits[:3]


def required_evidence(claim_type: str) -> list[str]:
    if claim_type == "damage":
        return [
            "proof_of_value",
            "tracking_proof",
            "damage_photos",
            "outer_packaging_photos",
            "inner_packaging_photos",
        ]
    if claim_type == "loss":
        return ["proof_of_value", "tracking_proof", "recipient_statement"]
    if claim_type == "missing_contents":
        return [
            "proof_of_value",
            "tracking_proof",
            "outer_packaging_photos",
            "inner_packaging_photos",
            "packing_slip",
        ]
    if claim_type == "late":
        return ["tracking_proof", "proof_of_value"]
    return ["proof_of_value", "tracking_proof"]


def evaluate(shipment: Shipment, evidence: dict[str, list[Path]], today: date) -> tuple[str, list[str], list[str]]:
    blockers: list[str] = []
    reviews: list[str] = []

    if shipment.claim_deadline is None:
        reviews.append("missing_claim_deadline")
    else:
        days_left = (shipment.claim_deadline - today).days
        if days_left < 0:
            blockers.append("claim_deadline_passed")
        elif days_left <= 7:
            reviews.append("claim_deadline_within_7_days")

    if shipment.claim_type == "unknown":
        reviews.append("unknown_claim_type")

    for evidence_type in required_evidence(shipment.claim_type):
        present, _ = evidence_present(shipment, evidence, evidence_type)
        if not present:
            if evidence_type == "proof_of_value":
                blockers.append("missing_proof_of_value")
            elif evidence_type == "tracking_proof":
                blockers.append("tracking_proof_missing")
            elif evidence_type == "damage_photos":
                blockers.append("damage_photos_missing")
            elif evidence_type in {"outer_packaging_photos", "inner_packaging_photos"}:
                blockers.append("packaging_photos_missing")
            else:
                reviews.append(f"{evidence_type}_missing")

    if shipment.claim_type in {"damage", "missing_contents"} and not truthy(
        shipment.fields.get("original_packaging_available", "")
    ):
        blockers.append("original_packaging_unavailable")

    covered_value = max(shipment.declared_value, shipment.insured_value)
    if covered_value and shipment.item_value > covered_value:
        reviews.append("claim_amount_exceeds_declared_or_insured_value")
    elif shipment.item_value and not covered_value:
        reviews.append("no_declared_or_insured_value_recorded")

    status = shipment.tracking_status.lower()
    if shipment.claim_type == "loss" and status and not any(hint in status for hint in STATUS_LOSS_HINTS):
        reviews.append("tracking_status_does_not_show_loss")
    if shipment.claim_type == "damage" and status and not any(hint in status for hint in STATUS_DAMAGE_HINTS):
        reviews.append("tracking_status_does_not_show_damage")

    if truthy(shipment.fields.get("replacement_shipped", "")) and blockers:
        reviews.append("replacement_sent_before_claim_packet_ready")

    sensitive_hits = [
        name for name in evidence if (shipment.shipment_id.lower() in name or shipment.order_id.lower() in name) and SENSITIVE_FILENAME.search(name)
    ]
    if sensitive_hits:
        blockers.append("sensitive_file_redaction_required")

    if blockers:
        decision = "Hold claim pending evidence repair"
    elif reviews:
        decision = "Review before submit"
    else:
        decision = "Submit-ready after owner review"
    return decision, sorted(set(blockers)), sorted(set(reviews))


def build_report(shipments: list[Shipment], evidence: dict[str, list[Path]], today: date) -> tuple[str, bool]:
    lines = ["# Parcel Claim Preflight Report", "", f"Run date: {today.isoformat()}", ""]
    any_blocker = False
    summary: dict[str, int] = {}
    details: list[tuple[Shipment, str, list[str], list[str]]] = []

    for shipment in shipments:
        decision, blockers, reviews = evaluate(shipment, evidence, today)
        any_blocker = any_blocker or bool(blockers)
        summary[decision] = summary.get(decision, 0) + 1
        details.append((shipment, decision, blockers, reviews))

    lines.append("## Parcel Claim Decision")
    for decision, count in sorted(summary.items()):
        lines.append(f"- {decision}: {count}")
    lines.append("")

    lines.append("## Claim Rows")
    lines.append("| Shipment | Carrier | Type | Value | Decision | Blockers | Review notes |")
    lines.append("|---|---|---|---:|---|---|---|")
    for shipment, decision, blockers, reviews in details:
        value = f"{shipment.currency} {shipment.item_value}"
        lines.append(
            "| {shipment} | {carrier} | {claim_type} | {value} | {decision} | {blockers} | {reviews} |".format(
                shipment=shipment.shipment_id,
                carrier=shipment.carrier or "unknown",
                claim_type=shipment.claim_type,
                value=value,
                decision=decision,
                blockers=", ".join(blockers) or "-",
                reviews=", ".join(reviews) or "-",
            )
        )
    lines.append("")

    lines.append("## Evidence Coverage")
    for shipment, _, _, _ in details:
        lines.append(f"### {shipment.shipment_id}")
        for evidence_type in required_evidence(shipment.claim_type):
            present, hits = evidence_present(shipment, evidence, evidence_type)
            status = "present" if present else "missing"
            source = "; ".join(hits) if hits else "-"
            lines.append(f"- {evidence_type}: {status} ({source})")
        lines.append("")

    lines.append("## Submit Guardrails")
    lines.append("- Do not submit until blockers are resolved or explicitly accepted by the claim owner.")
    lines.append("- Keep original packaging available for inspection when the claim involves damage or missing contents.")
    lines.append("- Include proof of value, tracking/scans, photos, and concise facts; avoid speculation about carrier intent.")
    lines.append("- Redact credentials, payment secrets, full card data, unrelated customer records, and internal tokens.")
    return "\n".join(lines), any_blocker


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shipments", required=True, type=Path, help="CSV of parcel claims to preflight")
    parser.add_argument("--evidence-dir", required=True, type=Path, help="Directory containing claim evidence files")
    parser.add_argument("--today", default=date.today().isoformat(), help="Run date, YYYY-MM-DD")
    parser.add_argument("--output", type=Path, help="Optional Markdown output path")
    args = parser.parse_args()

    try:
        today = parse_date(args.today)
        if today is None:
            raise ValueError("--today is required")
        shipments = read_shipments(args.shipments)
        evidence = evidence_index(args.evidence_dir)
        report, blocked = build_report(shipments, evidence, today)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 1

    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
    print(report)
    return 2 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
